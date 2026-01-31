import camelot
import pandas as pd
import glob
import os
import numpy as np
from pdf2image import convert_from_path
import pytesseract
import re

MASTER_CSV = r"C:\Users\wiiga\Downloads\Toronto Project\Workbook\MLS Google - MLS.csv"
PDF_FOLDER = "Monthly Data - PDF"
OUTPUT_CSV = "MLS_Google_MLS_FULL.csv"

COLUMNS = [
    "Location",
    "CompIndex",
    "CompBenchmark",
    "CompYoYChange",
    "SFDetachIndex",
    "SFDetachBenchmark",
    "SFDetachYoYChange",
    "SFAttachIndex",
    "SFAttachBenchmark",
    "SFAttachYoYChange",
    "THouseIndex",
    "THouseBenchmark",
    "THouseYoYChange",
    "ApartIndex",
    "ApartBenchmark",
    "ApartYoYChange",
    "Date"
]

expected_cols = len(COLUMNS) - 1  # exclude 'Date'

master_df = pd.read_csv(MASTER_CSV)
master_df = master_df[COLUMNS]
master_df["Date"] = pd.to_datetime(master_df["Date"], errors="coerce")
print(f"Loaded master CSV: {master_df.shape[0]} rows")

def extract_date_from_filename(path):
    name = os.path.basename(path).replace(".pdf", "")
    return pd.to_datetime(name, format="%B_%Y", errors="coerce")

def fix_row(row):
    lst = row.tolist()
    if len(lst) > expected_cols:
        lst = lst[:expected_cols]
    elif len(lst) < expected_cols:
        lst = lst + [None]*(expected_cols - len(lst))
    return lst

def parse_ocr_text(text, file_date):
    """Parse raw OCR text into DataFrame aligned to schema"""
    rows = []
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = re.split(r'\s+', line.strip())
        row = parts[:expected_cols] + [None]*(expected_cols - len(parts))
        rows.append(row)
    df = pd.DataFrame(rows, columns=COLUMNS[:-1])
    df["Date"] = file_date
    return df

def clean_numeric(df):
    """Clean numeric columns"""
    for col in COLUMNS[1:-1]:
        df[col] = (
            df[col].astype(str)
            .str.replace(r"[$,%]", "", regex=True)
            .str.replace(",", "")
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

pdf_files = sorted(
    glob.glob(os.path.join(PDF_FOLDER, "*.pdf")),
    key=extract_date_from_filename
)
print(f"PDF files discovered: {len(pdf_files)}")
if not pdf_files:
    raise RuntimeError("❌ No PDF files found — check folder path.")

new_rows = []
files_processed = 0
tables_processed = 0
rows_read = 0
rows_added = 0

for file in pdf_files:
    file_date = extract_date_from_filename(file)
    print(f"\n📂 Processing: {os.path.basename(file)} → {file_date.date()}")

    try:
        tables = camelot.read_pdf(file, pages='all', flavor='stream')
    except Exception as e:
        print(f"⚠️ Camelot failed for {file}: {e}")
        tables = []

    df_list = []
    if tables and len(tables) > 0:
        for table in tables:
            tables_processed += 1
            df = table.df
            df = df.dropna(how='all')
            df = df[df.iloc[:,0].notna() & df.iloc[:,0].apply(lambda x: isinstance(x, str))]
            df_fixed = df.apply(fix_row, axis=1)
            df = pd.DataFrame(df_fixed.tolist(), columns=COLUMNS[:-1])
            df["Date"] = file_date
            df = clean_numeric(df)
            df_list.append(df)
        print(f"✅ Camelot detected {len(df_list)} tables")
    else:
        print("⚠️ No tables detected with Camelot, using OCR fallback")
        try:
            pages = convert_from_path(file)
            ocr_text = ""
            for page in pages:
                ocr_text += pytesseract.image_to_string(page) + "\n"
            df = parse_ocr_text(ocr_text, file_date)
            df = clean_numeric(df)
            df_list.append(df)
        except Exception as e:
            print(f"❌ OCR failed for {file}: {e}")
            continue

    if df_list:
        pdf_df = pd.concat(df_list, ignore_index=True)
        rows_read += pdf_df.shape[0]

        for _, row in pdf_df.iterrows():
            location = row["Location"]
            existing_dates = master_df.loc[master_df["Location"] == location, "Date"]
            last_date = existing_dates.max() if not existing_dates.empty else None
            if last_date is None or row["Date"] > last_date:
                new_rows.append(row)
                rows_added += 1

    files_processed += 1

if new_rows:
    new_df = pd.DataFrame(new_rows)
    final_df = pd.concat([master_df, new_df], ignore_index=True)
else:
    final_df = master_df.copy()

final_df = final_df.sort_values(["Location", "Date"]).reset_index(drop=True)

final_df.to_csv(OUTPUT_CSV, index=False)

print("\n================ SUMMARY ================")
print(f"PDF files processed:       {files_processed}")
print(f"Tables processed (Camelot): {tables_processed}")
print(f"Rows read from PDFs:      {rows_read}")
print(f"New rows appended:        {rows_added}")
print(f"Final dataset rows:       {final_df.shape[0]}")
print(f"Date range:               {final_df['Date'].min().date()} → {final_df['Date'].max().date()}")
print("========================================")
