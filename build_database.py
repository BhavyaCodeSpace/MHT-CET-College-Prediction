import os
import sqlite3
import pandas as pd

from parser import extract_pdf


# ============================================================
# SETTINGS
# ============================================================

DATA_FOLDER = "data"
DATABASE = os.path.join(
    DATA_FOLDER,
    "cutoffs_2025.db"
)


PDF_FILES = [
    ("cap1.pdf", "CAP Round I"),
    ("cap2.pdf", "CAP Round II"),
    ("cap3.pdf", "CAP Round III"),
    ("cap4.pdf", "CAP Round IV"),
]


# ============================================================
# CHECK FILES
# ============================================================

print("\n========================================")
print(" MHT CET MASTER DATABASE BUILDER")
print("========================================\n")


missing = []

for filename, round_name in PDF_FILES:

    path = os.path.join(
        DATA_FOLDER,
        filename
    )

    if not os.path.exists(path):

        missing.append(
            filename
        )


if missing:

    print("ERROR: These PDF files are missing:\n")

    for file in missing:
        print(" -", file)

    print(
        "\nPut all four PDFs inside the data folder."
    )

    raise SystemExit


# ============================================================
# IMPORTANT
# ============================================================

print(
    "Found all four CAP PDFs.\n"
)


# ============================================================
# TEMP DATABASE
# ============================================================

TEMP_DATABASE = "cutoffs.db"


# ============================================================
# PROCESS EACH PDF
# ============================================================

all_data = []


for filename, round_name in PDF_FILES:

    pdf_path = os.path.join(
        DATA_FOLDER,
        filename
    )

    print("----------------------------------------")
    print("Processing:", filename)
    print("Round:", round_name)
    print("----------------------------------------")

    try:

        # ----------------------------------------------------
        # The existing parser creates cutoffs.db.
        # We temporarily use it to extract this round.
        # ----------------------------------------------------

        count = extract_pdf(
            pdf_path,
            year=2025,
            round_name=round_name
        )

        print(
            "Records extracted:",
            count
        )


        # ----------------------------------------------------
        # Read temporary database
        # ----------------------------------------------------

        if not os.path.exists(
            TEMP_DATABASE
        ):

            print(
                "WARNING: parser did not create database."
            )

            continue


        conn = sqlite3.connect(
            TEMP_DATABASE
        )


        try:

            df = pd.read_sql_query(
                "SELECT * FROM cutoffs",
                conn
            )

        except Exception as error:

            print(
                "Could not read database:",
                error
            )

            conn.close()

            continue


        conn.close()


        if df.empty:

            print(
                "WARNING: No records found."
            )

            continue


        # ----------------------------------------------------
        # Make absolutely sure round is correct
        # ----------------------------------------------------

        df["round"] = round_name

        df["year"] = 2025


        all_data.append(
            df
        )


        print(
            "Added",
            len(df),
            "records."
        )


    except Exception as error:

        print(
            "\nERROR while processing",
            filename
        )

        print(error)

        continue


# ============================================================
# CHECK RESULTS
# ============================================================

print("\n========================================")
print(" Combining all rounds...")
print("========================================\n")


if not all_data:

    print(
        "ERROR: No data was extracted."
    )

    raise SystemExit


master = pd.concat(
    all_data,
    ignore_index=True
)


# ============================================================
# REMOVE DUPLICATES
# ============================================================

dedup_columns = [
    "year",
    "round",
    "college_code",
    "choice_code",
    "category"
]


available_columns = [
    column
    for column in dedup_columns
    if column in master.columns
]


if available_columns:

    master = master.drop_duplicates(
        subset=available_columns,
        keep="first"
    )


# ============================================================
# CREATE DATA FOLDER
# ============================================================

os.makedirs(
    DATA_FOLDER,
    exist_ok=True
)


# ============================================================
# CREATE MASTER DATABASE
# ============================================================

if os.path.exists(
    DATABASE
):

    os.remove(
        DATABASE
    )


conn = sqlite3.connect(
    DATABASE
)


master.to_sql(
    "cutoffs",
    conn,
    if_exists="replace",
    index=False
)


conn.close()


# ============================================================
# REMOVE TEMPORARY DATABASE
# ============================================================

if os.path.exists(
    TEMP_DATABASE
):

    os.remove(
        TEMP_DATABASE
    )


# ============================================================
# SUMMARY
# ============================================================

print("\n========================================")
print(" DATABASE CREATED SUCCESSFULLY")
print("========================================\n")

print(
    "Database:",
    DATABASE
)

print(
    "Total records:",
    len(master)
)


if "round" in master.columns:

    print("\nRecords by round:")

    print(
        master["round"]
        .value_counts()
        .sort_index()
    )


if "category" in master.columns:

    print("\nRecords by category:")

    print(
        master["category"]
        .value_counts()
    )


print(
    "\nYour master database is ready."
)

print(
    "========================================\n"
)