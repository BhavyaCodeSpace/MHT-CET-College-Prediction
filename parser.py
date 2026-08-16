import re
import sqlite3
import fitz


DB_NAME = "cutoffs.db"


# ============================================================
# CATEGORY MAPPING
# ============================================================

def get_category(seat_code):

    code = seat_code.upper().strip()

    if code == "TFWS":
        return "TFWS"

    if code == "EWS":
        return "EWS"

    if code == "MI":
        return "Minority"

    # OPEN
    if code.startswith("GOPEN"):
        return "OPEN"

    if code.startswith("LOPEN"):
        return "OPEN"

    # OBC
    if code.startswith("GOBC"):
        return "OBC"

    if code.startswith("LOBC"):
        return "OBC"

    # SC
    if code.startswith("GSC"):
        return "SC"

    if code.startswith("LSC"):
        return "SC"

    # ST
    if code.startswith("GST"):
        return "ST"

    if code.startswith("LST"):
        return "ST"

    # VJ
    if code.startswith("GVJ"):
        return "VJ"

    if code.startswith("LVJ"):
        return "VJ"

    # NT1
    if code.startswith("GNT1"):
        return "NT1"

    if code.startswith("LNT1"):
        return "NT1"

    # NT2
    if code.startswith("GNT2"):
        return "NT2"

    if code.startswith("LNT2"):
        return "NT2"

    # NT3
    if code.startswith("GNT3"):
        return "NT3"

    if code.startswith("LNT3"):
        return "NT3"

    # SEBC treated separately if needed later
    if code.startswith("GSEBC"):
        return "SEBC"

    if code.startswith("LSEBC"):
        return "SEBC"

    return None


# ============================================================
# CITY DETECTION
# ============================================================

CITIES = [
    "Mumbai",
    "Navi Mumbai",
    "Thane",
    "Pune",
    "Nagpur",
    "Nashik",
    "Kolhapur",
    "Amravati",
    "Chhatrapati Sambhajinagar",
    "Aurangabad",
    "Jalgaon",
    "Nanded",
    "Sangli",
    "Satara",
    "Solapur",
    "Akola",
    "Latur",
    "Ahmednagar",
    "Ahilyanagar",
    "Dhule",
    "Nandurbar",
    "Jalna",
    "Parbhani",
    "Beed",
    "Dharashiv",
    "Osmanabad",
    "Ratnagiri",
    "Raigad",
    "Palghar",
    "Wardha",
    "Yavatmal",
    "Buldhana",
    "Washim",
    "Chandrapur",
    "Gondia",
    "Bhandara",
    "Panvel",
    "Kalyan",
    "Dombivli",
    "Vasai",
    "Virar",
    "Ulhasnagar",
    "Ichalkaranji",
    "Karad",
    "Baramati",
    "Pimpri-Chinchwad",
]


def detect_city(college_name):

    text = college_name.lower()

    for city in sorted(
        CITIES,
        key=len,
        reverse=True
    ):

        if city.lower() in text:

            if city.lower() == "aurangabad":
                return "Chhatrapati Sambhajinagar"

            if city.lower() == "ahmednagar":
                return "Ahilyanagar"

            if city.lower() == "osmanabad":
                return "Dharashiv"

            return city

    return "Other"


# ============================================================
# TEXT CLEANING
# ============================================================

def clean(text):

    return re.sub(
        r"\s+",
        " ",
        text.replace("\u00a0", " ")
    ).strip()


# ============================================================
# SEAT CODE DETECTION
# ============================================================

def is_seat_code(text):

    text = text.upper().strip()

    prefixes = [
        "GOPEN",
        "LOPEN",
        "GOBC",
        "LOBC",
        "GSC",
        "LSC",
        "GST",
        "LST",
        "GVJ",
        "LVJ",
        "GNT1",
        "LNT1",
        "GNT2",
        "LNT2",
        "GNT3",
        "LNT3",
        "GSEBC",
        "LSEBC",
        "TFWS",
        "EWS",
        "MI",
    ]

    return (
        text in ["EWS", "TFWS", "MI"]
        or any(
            text.startswith(p)
            for p in prefixes
        )
    )


# ============================================================
# CREATE DATABASE
# ============================================================

def create_database():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS cutoffs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            year INTEGER,
            round TEXT,

            college_code TEXT,
            college_name TEXT,
            location TEXT,

            choice_code TEXT,
            branch TEXT,

            seat_code TEXT,
            category TEXT,

            section TEXT,
            stage TEXT,

            merit_rank INTEGER,
            percentile REAL
        )
        """
    )

    conn.commit()
    conn.close()


# ============================================================
# REBUILD DATABASE
# ============================================================

def rebuild_database():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        "DROP TABLE IF EXISTS cutoffs"
    )

    conn.commit()
    conn.close()

    create_database()


# ============================================================
# EXTRACT WORDS WITH COORDINATES
# ============================================================

def get_words(page):

    words = page.get_text(
        "words"
    )

    output = []

    for word in words:

        x0, y0, x1, y1, text = word[:5]

        text = clean(text)

        if not text:
            continue

        output.append(
            {
                "x0": x0,
                "y0": y0,
                "x1": x1,
                "y1": y1,
                "x": (x0 + x1) / 2,
                "y": (y0 + y1) / 2,
                "text": text
            }
        )

    return output


# ============================================================
# GROUP WORDS INTO LINES
# ============================================================

def group_lines(words):

    lines = []

    for word in sorted(
        words,
        key=lambda w: (w["y"], w["x"])
    ):

        placed = False

        for line in lines:

            if abs(
                line["y"] - word["y"]
            ) < 3:

                line["words"].append(word)

                placed = True

                break

        if not placed:

            lines.append(
                {
                    "y": word["y"],
                    "words": [word]
                }
            )

    for line in lines:

        line["words"].sort(
            key=lambda w: w["x"]
        )

        line["text"] = " ".join(
            w["text"]
            for w in line["words"]
        )

    return lines


# ============================================================
# FIND COLLEGE
# ============================================================

def find_college(lines):

    for line in lines:

        match = re.match(
            r"^(\d{5})\s*-\s*(.+)$",
            line["text"]
        )

        if match:

            return (
                match.group(1),
                clean(match.group(2))
            )

    return None, None


# ============================================================
# FIND BRANCHES
# ============================================================

def find_branch_lines(lines):

    branches = []

    for index, line in enumerate(lines):

        match = re.match(
            r"^(\d{10})\s*-\s*(.+)$",
            line["text"]
        )

        if match:

            branches.append(
                {
                    "index": index,
                    "choice_code": match.group(1),
                    "branch": clean(match.group(2)),
                    "y": line["y"]
                }
            )

    return branches


# ============================================================
# FIND SEAT HEADER
# ============================================================

def find_seat_header(
    lines,
    start_index,
    end_index
):

    candidates = []

    for index in range(
        start_index,
        min(
            end_index,
            start_index + 15
        )
    ):

        words = lines[index]["words"]

        found = []

        for word in words:

            if is_seat_code(
                word["text"]
            ):

                found.append(
                    {
                        "code":
                            word["text"].upper(),

                        "x":
                            word["x"],

                        "y":
                            word["y"]
                    }
                )

        if len(found) >= 1:

            candidates.append(found)

    if not candidates:
        return []

    # Usually the first line containing
    # multiple seat codes is the header.
    return max(
        candidates,
        key=len
    )


# ============================================================
# FIND PERCENTILE
# ============================================================

def extract_percentile(text):

    match = re.search(
        r"\(?(\d{1,3}\.\d+)\)?",
        text
    )

    if not match:
        return None

    value = float(
        match.group(1)
    )

    if 0 <= value <= 100:

        return value

    return None


# ============================================================
# FIND MERIT RANK
# ============================================================

def extract_rank(text):

    match = re.fullmatch(
        r"\d{3,8}",
        text
    )

    if not match:
        return None

    return int(text)


# ============================================================
# EXTRACT COLUMN VALUES
# ============================================================

def extract_column_values(
    lines,
    start_index,
    end_index,
    seat_headers
):

    values = {
        header["code"]: []
        for header in seat_headers
    }


    # --------------------------------------------------------
    # Look below the header.
    #
    # Percentile numbers are physically underneath their
    # respective seat-code columns.
    # --------------------------------------------------------

    for line_index in range(
        start_index,
        end_index
    ):

        line = lines[line_index]

        for word in line["words"]:

            percentile = extract_percentile(
                word["text"]
            )

            if percentile is None:
                continue


            # Find closest header horizontally
            nearest = min(
                seat_headers,
                key=lambda header:
                    abs(
                        header["x"]
                        - word["x"]
                    )
            )


            distance = abs(
                nearest["x"]
                - word["x"]
            )


            # Ignore values that are clearly
            # outside the table columns.
            if distance > 80:
                continue


            values[
                nearest["code"]
            ].append(
                {
                    "percentile":
                        percentile,

                    "y":
                        word["y"]
                }
            )


    return values


# ============================================================
# SELECT BEST CUTOFF
# ============================================================

def select_cutoff(
    values
):

    if not values:
        return None

    # The PDF can contain multiple stages.
    #
    # For the prediction database we use the final/latest
    # available cutoff value in the table.
    #
    # Since the values are ordered vertically, choose the
    # lowest y (first stage) only when there is one value.
    #
    # If multiple values exist, the highest percentile is
    # retained as the conservative single cutoff.
    #
    return max(
        values,
        key=lambda item:
            item["percentile"]
    )


# ============================================================
# PROCESS PDF
# ============================================================

def extract_pdf(
    pdf_path,
    year=2025,
    round_name="CAP Round III"
):

    rebuild_database()

    document = fitz.open(
        pdf_path
    )

    records = []


    # ========================================================
    # EACH PAGE
    # ========================================================

    for page in document:

        words = get_words(page)

        lines = group_lines(words)

        college_code, college_name = (
            find_college(lines)
        )

        if not college_code:
            continue


        location = detect_city(
            college_name
        )


        branches = find_branch_lines(
            lines
        )


        if not branches:
            continue


        # ====================================================
        # EACH BRANCH ON PAGE
        # ====================================================

        for branch_index, branch_info in enumerate(
            branches
        ):

            choice_code = (
                branch_info["choice_code"]
            )

            branch_name = (
                branch_info["branch"]
            )


            start = branch_info["index"]


            if branch_index + 1 < len(branches):

                end = branches[
                    branch_index + 1
                ]["index"]

            else:

                end = len(lines)


            # ------------------------------------------------
            # Find seat headers
            # ------------------------------------------------

            seat_headers = find_seat_header(
                lines,
                start,
                end
            )


            if not seat_headers:
                continue


            # ------------------------------------------------
            # Find table values
            # ------------------------------------------------

            values = extract_column_values(
                lines,
                start,
                end,
                seat_headers
            )


            # ------------------------------------------------
            # Save each seat column
            # ------------------------------------------------

            for header in seat_headers:

                code = header[
                    "code"
                ]


                category = get_category(
                    code
                )


                if category is None:
                    continue


                column_values = values.get(
                    code,
                    []
                )


                selected = select_cutoff(
                    column_values
                )


                if selected is None:
                    continue


                records.append(
                    {

                        "year":
                            year,

                        "round":
                            round_name,

                        "college_code":
                            college_code,

                        "college_name":
                            college_name,

                        "location":
                            location,

                        "choice_code":
                            choice_code,

                        "branch":
                            branch_name,

                        "seat_code":
                            code,

                        "category":
                            category,

                        "section":
                            "Detected",

                        "stage":
                            "CAP",

                        "merit_rank":
                            None,

                        "percentile":
                            selected[
                                "percentile"
                            ]
                    }
                )


    document.close()


    # ========================================================
    # SAVE
    # ========================================================

    if not records:

        return 0


    import pandas as pd

    df = pd.DataFrame(
        records
    )


    # ========================================================
    # CRITICAL DEDUPLICATION
    #
    # EXACTLY ONE:
    #
    # college + branch + category
    # ========================================================

    df = df.sort_values(
        "percentile",
        ascending=False
    )


    df = df.drop_duplicates(
        subset=[
            "college_code",
            "choice_code",
            "category"
        ],
        keep="first"
    )


    # ========================================================
    # DATABASE
    # ========================================================

    conn = sqlite3.connect(
        DB_NAME
    )


    df.to_sql(
        "cutoffs",
        conn,
        if_exists="replace",
        index=False
    )


    conn.close()


    return len(df)