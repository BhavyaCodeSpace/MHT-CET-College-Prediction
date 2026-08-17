import os
import sqlite3
import pandas as pd
import streamlit as st

# ============================================================
# PAGE CONFIG (Auto-adapts sidebar based on screen size)
# ============================================================

st.set_page_config(
    page_title="MHT CET College Predictor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="auto"  # Expanded on Desktop, Collapsed on Mobile
)


# ============================================================
# RESPONSIVE DESKTOP & MOBILE STYLING
# ============================================================

st.markdown(
    """
    
<style>
/* Move the main title closer to the top of the page */
.block-container {
    padding-top: 0.8rem !important;
}
</style>

<style>
    /* ========================================================
       PREMIUM NEON UI — VISUAL ONLY
       ======================================================== */

    :root {
        --neon-blue: #00c8ff;
        --neon-purple: #c026ff;
        --neon-pink: #ff2bd6;
        --neon-green: #20e890;
        --neon-yellow: #ffbd1a;
        --panel: #080d1d;
        --panel-2: #0d1428;
        --border: rgba(130, 160, 220, 0.20);
    }

    /* App background */
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at 85% 8%, rgba(0, 170, 255, 0.10), transparent 28%),
            radial-gradient(circle at 45% 35%, rgba(192, 38, 255, 0.07), transparent 30%),
            #070a12;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        max-width: 1500px !important;
    }

    /* ========================================================
       SIDEBAR
       ======================================================== */
    [data-testid="stSidebar"] {
        background:
            radial-gradient(circle at 15% 10%, rgba(192, 38, 255, 0.12), transparent 28%),
            linear-gradient(180deg, #090d1d 0%, #050914 100%);
        border-right: 1px solid rgba(150, 100, 255, 0.22);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.4rem;
    }

    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #f5f7ff !important;
        text-shadow: 0 0 14px rgba(192, 38, 255, 0.45);
    }

    [data-testid="stSidebar"] label {
        color: #dce5ff !important;
        font-weight: 600 !important;
    }

    /* Sidebar inputs */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-baseweb="input"] > div {
        background: rgba(4, 9, 22, 0.92) !important;
        border: 1px solid rgba(120, 145, 210, 0.22) !important;
        border-radius: 10px !important;
        color: #f6f8ff !important;
        transition: all 0.2s ease;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] > div:hover,
    [data-testid="stSidebar"] [data-baseweb="input"] > div:hover {
        border-color: rgba(0, 200, 255, 0.65) !important;
        box-shadow: 0 0 16px rgba(0, 200, 255, 0.12);
    }

    /* Sidebar buttons */
    [data-testid="stSidebar"] .stButton > button {
        border-radius: 11px !important;
        border: 1px solid rgba(0, 200, 255, 0.55) !important;
        background: linear-gradient(100deg, #b90cff 0%, #7d27ff 48%, #007dff 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        box-shadow: 0 0 22px rgba(160, 30, 255, 0.30), 0 0 12px rgba(0, 160, 255, 0.18);
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 0 30px rgba(192, 38, 255, 0.48), 0 0 22px rgba(0, 200, 255, 0.30);
    }

    /* ========================================================
       MAIN TITLE — PINK / BLUE NEON
       ======================================================== */
    .neon-title {
        position: relative;
        overflow: hidden;
        margin: 0.2rem 0 1.25rem 0;
        padding: 1.55rem 2rem;
        border-radius: 18px;
        border: 1px solid rgba(0, 200, 255, 0.75);
        background:
            radial-gradient(circle at 10% 50%, rgba(255, 0, 190, 0.15), transparent 35%),
            radial-gradient(circle at 95% 40%, rgba(0, 180, 255, 0.13), transparent 38%),
            linear-gradient(105deg, rgba(35, 6, 58, 0.92), rgba(7, 16, 37, 0.96));
        box-shadow:
            0 0 10px rgba(255, 43, 214, 0.30),
            0 0 32px rgba(0, 200, 255, 0.16),
            inset 0 0 30px rgba(100, 40, 180, 0.08);
    }

    .neon-title::after {
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(110deg, transparent 15%, rgba(255,255,255,0.08) 48%, transparent 62%);
        transform: translateX(-100%);
        animation: neon-shine 7s linear infinite;
        pointer-events: none;
    }

    @keyframes neon-shine {
        0%, 65% { transform: translateX(-100%); }
        85%, 100% { transform: translateX(100%); }
    }

    .neon-title h1 {
        margin: 0 !important;
        font-size: clamp(1.8rem, 3vw, 3rem) !important;
        line-height: 1.15 !important;
        font-weight: 800 !important;
        letter-spacing: -0.03em;
        color: #ffffff !important;
        text-shadow: 0 0 12px rgba(255, 255, 255, 0.18);
    }

    .neon-title .subtitle {
        margin-top: 0.55rem;
        color: #f3f5ff;
        font-size: clamp(1rem, 1.8vw, 1.35rem);
        font-weight: 600;
    }

    .neon-title .hint {
        margin-top: 0.45rem;
        color: #c49cff;
        font-size: 0.98rem;
    }

    /* ========================================================
       COLLEGE PREDICTIONS HEADING — PURPLE NEON
       ======================================================== */
    .neon-heading {
        margin: 0.45rem 0 0.45rem 0;
        padding: 0.75rem 1.05rem;
        display: inline-flex;
        align-items: center;
        gap: 0.55rem;
        border-radius: 13px;
        border: 1px solid rgba(192, 38, 255, 0.70);
        background: linear-gradient(100deg, rgba(70, 10, 95, 0.65), rgba(18, 14, 45, 0.68));
        box-shadow: 0 0 20px rgba(192, 38, 255, 0.18), inset 0 0 18px rgba(192, 38, 255, 0.06);
    }

    .neon-heading h2 {
        margin: 0 !important;
        font-size: clamp(1.45rem, 2.2vw, 2rem) !important;
        color: #f7f2ff !important;
        text-shadow: 0 0 14px rgba(192, 38, 255, 0.55);
    }

    /* ========================================================
       SUMMARY CARDS — FOUR DIFFERENT NEON COLOURS
       ======================================================== */
    .summary-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 1rem;
        margin: 0 0 0.8rem 0;
    }


    .summary-card {
        min-height: 108px;
        padding: 1rem 1.15rem;
        border-radius: 15px;
        background: rgba(8, 14, 31, 0.82);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        display: flex;
        flex-direction: column;
        justify-content: center;
        border: 1px solid var(--accent);
        box-shadow: 0 0 22px var(--glow), inset 0 0 24px rgba(255,255,255,0.025);
    }

    .summary-card .label {
        color: var(--accent);
        font-size: 0.86rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        margin-bottom: 0.28rem;
    }

    .summary-card .value {
        color: #ffffff;
        font-size: clamp(1.7rem, 2.7vw, 2.25rem);
        line-height: 1;
        font-weight: 800;
        text-shadow: 0 0 13px var(--glow);
    }

    .card-blue { --accent: #00c8ff; --glow: rgba(0,200,255,0.28); }
    .card-purple { --accent: #ef55ff; --glow: rgba(239,85,255,0.28); }
    .card-green { --accent: #20e890; --glow: rgba(32,232,144,0.24); }
    .card-yellow { --accent: #ffbd1a; --glow: rgba(255,189,26,0.25); }

    /* Hide default metric visuals if any remain in Streamlit rerun DOM */
    [data-testid="stMetric"] {
        background: transparent;
        border: none;
    }

    /* ========================================================
       TABLE — FULL WIDTH, NO INNER SCROLL / COLUMN MENUS
       ======================================================== */
    [data-testid="stTable"] {
        width: 100%;
        border: 1px solid rgba(100, 145, 220, 0.24);
        border-radius: 12px;
        overflow: visible;
        box-shadow: 0 0 22px rgba(0, 140, 255, 0.08);
    }

    [data-testid="stTable"] table {
        width: 100% !important;
        table-layout: fixed;
        border-collapse: collapse;
    }

    [data-testid="stTable"] th,
    [data-testid="stTable"] td {
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        vertical-align: middle;
        padding: 0.55rem 0.55rem !important;
        font-size: 0.86rem !important;
        line-height: 1.2 !important;
    }

    /* Compact, predictable column widths. Long college names stay on one line. */
    [data-testid="stTable"] th:nth-child(1),
    [data-testid="stTable"] td:nth-child(1) {
        width: 5% !important;
        text-align: center;
    }

    [data-testid="stTable"] th:nth-child(2),
    [data-testid="stTable"] td:nth-child(2) {
        width: 39% !important;
        max-width: 39% !important;
    }

    [data-testid="stTable"] th:nth-child(3),
    [data-testid="stTable"] td:nth-child(3) {
        width: 22% !important;
        max-width: 22% !important;
    }

    [data-testid="stTable"] th:nth-child(4),
    [data-testid="stTable"] td:nth-child(4) {
        width: 11% !important;
        max-width: 11% !important;
    }

    [data-testid="stTable"] th:nth-child(5),
    [data-testid="stTable"] td:nth-child(5) {
        width: 11% !important;
        max-width: 11% !important;
        text-align: center;
    }

    [data-testid="stTable"] th:nth-child(6),
    [data-testid="stTable"] td:nth-child(6) {
        width: 12% !important;
        max-width: 12% !important;
    }

    [data-testid="stTable"] th {
        background: rgba(20, 28, 52, 0.96);
    }

    [data-testid="stTable"] tr:hover td {
        background: rgba(40, 70, 130, 0.12);
    }

    /* ========================================================
       GENERAL BUTTONS
       ======================================================== */
    .stButton > button,
    .stDownloadButton > button {
        width: 100%;
        min-height: 2.7rem;
        padding-top: 0.6rem;
        padding-bottom: 0.6rem;
        font-size: 1rem;
        border-radius: 10px;
        transition: all 0.2s ease;
    }

    /* ========================================================
       MOBILE
       ======================================================== */
    @media (max-width: 900px) {
        .summary-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }

    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
            padding-top: 1.2rem !important;
        }

        .neon-title {
            padding: 1.15rem 1.2rem;
        }

        .summary-grid {
            grid-template-columns: 1fr 1fr;
            gap: 0.7rem;
        }

        .summary-card {
            min-height: 94px;
            padding: 0.85rem;
        }
    }

    @media (max-width: 480px) {
        .summary-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATABASE
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = os.path.join(
    BASE_DIR,
    "data",
    "cutoffs_2025.db"
)


@st.cache_data
def load_database():

    if not os.path.exists(DATABASE):
        return pd.DataFrame()

    conn = sqlite3.connect(DATABASE)

    data = pd.read_sql_query(
        "SELECT * FROM cutoffs",
        conn
    )

    conn.close()

    return data


df = load_database()

# ============================================================
# CORRECT "OTHER" LOCATIONS USING DTE DISTRICT MAPPING
# ============================================================

LOCATION_MAPPING_FILE = os.path.join(
    BASE_DIR,
    "data",
    "other_college_district_mapping.csv"
)

if os.path.exists(LOCATION_MAPPING_FILE):

    location_mapping = pd.read_csv(
        LOCATION_MAPPING_FILE,
        dtype={"college_code": str}
    )

    # Make sure college codes match even if SQLite stores them differently
    df["college_code"] = (
        df["college_code"]
        .astype(str)
        .str.strip()
    )

    location_mapping["college_code"] = (
        location_mapping["college_code"]
        .astype(str)
        .str.strip()
    )

    # Create college-code → district lookup
    district_map = dict(
        zip(
            location_mapping["college_code"],
            location_mapping["corrected_district"]
        )
    )

    # IMPORTANT:
    # Only replace locations currently marked "Other".
    # All existing locations remain untouched.
    other_mask = (
        df["location"]
        .astype(str)
        .str.strip()
        .str.lower()
        == "other"
    )

    df.loc[other_mask, "location"] = (
        df.loc[other_mask, "college_code"]
        .map(district_map)
        .fillna(df.loc[other_mask, "location"])
    )

if df.empty:
    st.error("Something went wrong while loading the predictor.")
    st.stop()


# ============================================================
# CLEAN DATA
# ============================================================

required_columns = [
    "category",
    "round",
    "college_name",
    "branch",
    "location",
    "percentile"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error("The predictor data could not be loaded correctly.")
    st.stop()


for column in [
    "category",
    "round",
    "college_name",
    "branch",
    "location"
]:

    df[column] = (
        df[column]
        .astype(str)
        .str.strip()
    )


df["percentile"] = pd.to_numeric(
    df["percentile"],
    errors="coerce"
)

df = df.dropna(
    subset=["percentile"]
)


# ============================================================
# CATEGORY OPTIONS
# ============================================================

category_order = [
    "OPEN",
    "Minority",
    "OBC",
    "SC",
    "ST",
    "VJ",
    "NT1",
    "NT2",
    "NT3",
    "SEBC",
    "EWS",
    "TFWS"
]

categories = [
    category
    for category in category_order
    if category in df["category"].unique()
]


# ============================================================
# LOCATION OPTIONS
# ============================================================

locations = sorted(
    df["location"]
    .dropna()
    .unique()
    .tolist()
)

location_options = [
    "All Locations"
] + locations


# ============================================================
# BRANCH OPTIONS
# ============================================================

branches = sorted(
    df["branch"]
    .dropna()
    .unique()
    .tolist()
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="neon-title">
        <h1>🎓 MHT CET College Predictor</h1>
        <div class="subtitle">Find engineering colleges based on your MHT CET percentile and preferences.</div>
        <div class="hint">Select your details in the sidebar to explore college options.</div>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Your Details")


# ------------------------------------------------------------
# PERCENTILE
# ------------------------------------------------------------

percentile = st.sidebar.number_input(
    "MHT CET Percentile",
    min_value=0.00,
    max_value=100.00,
    value=None,
    placeholder="Enter percentile",
    step=0.01,
    format="%.2f"
)


# ------------------------------------------------------------
# CATEGORY
# ------------------------------------------------------------

category = st.sidebar.selectbox(
    "Category",
    categories,
    index=None,
    placeholder="Select category"
)


# ------------------------------------------------------------
# LOCATION
# ------------------------------------------------------------

location = st.sidebar.selectbox(
    "Preferred Location",
    location_options,
    index=None,
    placeholder="Select location"
)


# ------------------------------------------------------------
# BRANCH
# ------------------------------------------------------------

branch_selection = st.sidebar.multiselect(
    "Preferred Engineering Branches",
    branches,
    placeholder="Select branch(es)"
)


# ------------------------------------------------------------
# BUTTON
# ------------------------------------------------------------

predict_clicked = st.sidebar.button(
    "🔍 Predict Colleges",
    type="primary",
    use_container_width=True
)

if predict_clicked:
    st.session_state["predicted"] = True

    # Save the current inputs only when the Predict button is clicked.
    st.session_state["search_percentile"] = percentile
    st.session_state["search_category"] = category
    st.session_state["search_location"] = location
    st.session_state["search_branches"] = branch_selection.copy()

predict = st.session_state.get("predicted", False)


# ============================================================
# HOME SCREEN
# ============================================================

if not predict:

    st.divider()

    st.subheader("How to use")

    st.markdown(
        """
        **1.** Enter your MHT CET percentile.

        **2.** Select your category.

        **3.** Choose your preferred location.

        **4.** Select one or more engineering branches.

        **5.** Click **Predict Colleges**.
        """
    )

    st.divider()

    st.subheader("Explore your options")

    st.write(
        "Use your percentile and preferences to find "
        "colleges that may be suitable based on previous "
        "CAP cutoff trends."
    )

    st.stop()


# ============================================================
# USE SAVED SEARCH VALUES
# ============================================================

# Keep displaying the previous prediction while the user edits
# the sidebar. These values change only after Predict Colleges
# is clicked.
percentile = st.session_state["search_percentile"]
category = st.session_state["search_category"]
location = st.session_state["search_location"]
branch_selection = st.session_state["search_branches"]


# ============================================================
# VALIDATION
# ============================================================

if percentile is None:

    st.warning(
        "Please enter your MHT CET percentile."
    )

    st.stop()


if category is None:

    st.warning(
        "Please select your category."
    )

    st.stop()


if location is None:

    st.warning(
        "Please select a preferred location."
    )

    st.stop()


if not branch_selection:

    st.warning(
        "Please select at least one engineering branch."
    )

    st.stop()


# ============================================================
# FILTER RESULTS ACROSS ALL CAP ROUNDS
# ============================================================

# We keep all four CAP rounds so the table can show the complete
# cutoff history. Prediction is based on the latest available
# cutoff for each college/branch:
# CAP IV -> CAP III -> CAP II -> CAP I.
results = df.copy()


# ------------------------------------------------------------
# CATEGORY
# ------------------------------------------------------------

results = results[
    results["category"].str.upper()
    ==
    category.upper()
]


# ------------------------------------------------------------
# LOCATION
# ------------------------------------------------------------

if location != "All Locations":

    results = results[
        results["location"].str.lower()
        ==
        location.lower()
    ]


# ------------------------------------------------------------
# BRANCH
# ------------------------------------------------------------

results = results[
    results["branch"].isin(
        branch_selection
    )
]


# ============================================================
# BUILD ONE ROW PER COLLEGE / BRANCH
# ============================================================

round_order = [
    "CAP Round I",
    "CAP Round II",
    "CAP Round III",
    "CAP Round IV"
]

# Use the same identity fields used by the original predictor,
# while also keeping branch/location so each displayed option
# remains distinct.
identity_columns = [
    column
    for column in [
        "college_code",
        "choice_code",
        "college_name",
        "branch",
        "location",
        "category"
    ]
    if column in results.columns
]

if not identity_columns:
    st.error("The predictor data could not be grouped correctly.")
    st.stop()


# If duplicate records exist inside one CAP round, keep the
# highest cutoff for that college/branch/category combination.
round_data = (
    results.groupby(
        identity_columns + ["round"],
        as_index=False
    )["percentile"]
    .max()
)


cutoff_pivot = (
    round_data
    .pivot_table(
        index=identity_columns,
        columns="round",
        values="percentile",
        aggfunc="max"
    )
    .reset_index()
)


# Make sure all four CAP columns exist even if a round has no
# records in the filtered dataset.
for round_label in round_order:
    if round_label not in cutoff_pivot.columns:
        cutoff_pivot[round_label] = float("nan")


# ============================================================
# LATEST AVAILABLE CAP CUTOFF
# ============================================================

# For every row, use CAP IV if available; otherwise CAP III,
# then CAP II, then CAP I.
cutoff_columns = list(reversed(round_order))

cutoff_pivot["Latest Cutoff"] = cutoff_pivot[
    cutoff_columns
].bfill(axis=1).iloc[:, 0]

cutoff_pivot["Latest CAP"] = cutoff_pivot.apply(
    lambda row: next(
        (
            round_label
            for round_label in reversed(round_order)
            if pd.notna(row[round_label])
        ),
        None
    ),
    axis=1
)


# Remove rows for which no CAP-round cutoff exists.
results = cutoff_pivot[
    cutoff_pivot["Latest Cutoff"].notna()
].copy()


# ============================================================
# CHANCE — BASED ON LAST AVAILABLE CAP
# ============================================================

def calculate_chance(cutoff):

    difference = percentile - cutoff

    if difference >= 3:
        return "🟢 Very High"

    if difference >= 1:
        return "🟢 High"

    if difference >= -1:
        return "🟡 Possible"

    if difference >= -3:
        return "🟠 Borderline"

    return "🔴 Less Likely"


results["Chance"] = (
    results["Latest Cutoff"]
    .apply(calculate_chance)
)


# ============================================================
# SORT RESULTS
# ============================================================

chance_order = {
    "🟢 Very High": 1,
    "🟢 High": 2,
    "🟡 Possible": 3,
    "🟠 Borderline": 4,
    "🔴 Less Likely": 5
}

results["chance_order"] = (
    results["Chance"]
    .map(chance_order)
)


results = results.sort_values(
    ["chance_order", "Latest Cutoff"],
    ascending=[False, False]
)


# ============================================================
# SUMMARY — FOUR DIFFERENT NEON COLOURS
# ============================================================

summary_html = f"""
<div class="summary-grid">
    <div class="summary-card card-blue">
        <div class="label">Your Percentile</div>
        <div class="value">{percentile:.2f}</div>
    </div>
    <div class="summary-card card-purple">
        <div class="label">Category</div>
        <div class="value">{category}</div>
    </div>
    <div class="summary-card card-green">
        <div class="label">Location</div>
        <div class="value">{location}</div>
    </div>
    <div class="summary-card card-yellow">
        <div class="label">Colleges Found</div>
        <div class="value">{len(results)}</div>
    </div>
</div>
"""

st.markdown(summary_html, unsafe_allow_html=True)


# ============================================================
# NO RESULTS
# ============================================================

if results.empty:

    st.warning(
        "No matching colleges were found for your "
        "selected preferences."
    )

    st.info(
        "Try selecting All Locations or adding "
        "more branches."
    )

    st.stop()


# ============================================================
# DISPLAY TABLE
# ============================================================

def format_cutoff(value):
    # Always return a plain string. Missing/unavailable CAP data is
    # represented by a literal hyphen, never a dataframe missing-value dot.
    if value is None or pd.isna(value):
        return "/"

    if isinstance(value, str):
        cleaned = value.strip()
        if cleaned in {"", ".", "-", "nan", "NaN", "None", "NULL", "null"}:
            return "/"
        value = cleaned

    try:
        number = float(value)
    except (TypeError, ValueError):
        return "/"

    if pd.isna(number):
        return "/"

    return ("%0.2f" % number).rstrip("0").rstrip(".")


display_df = pd.DataFrame({
    "College": results["college_name"].astype(str),
    "Branch": results["branch"].astype(str),
    "CAP 1": results["CAP Round I"].map(format_cutoff),
    "CAP 2": results["CAP Round II"].map(format_cutoff),
    "CAP 3": results["CAP Round III"].map(format_cutoff),
    "CAP 4": results["CAP Round IV"].map(format_cutoff),
    "Chance": results["Chance"].astype(str)
}).reset_index(drop=True)

# Replace the DataFrame's default 0, 1, 2... index with a clean
# student-facing index starting from 1.
display_df.insert(0, "#", range(1, len(display_df) + 1))

# Final safety pass: make CAP 1-4 cells literal strings. This prevents
# Streamlit/Pandas from rendering missing values as a dot or other marker.
for cap_column in ["CAP 1", "CAP 2", "CAP 3", "CAP 4"]:
    display_df[cap_column] = (
        display_df[cap_column]
        .astype("string")
        .fillna("-")
        .replace({"<NA>": "/", "nan": "/", "NaN": "/", ".": "/"})
        .astype(str)
    )


# Use a static table instead of st.dataframe.
# This removes the dataframe column menus/three-dot controls and
# lets the table expand naturally with the page instead of creating
# an internal scrolling area.
st.markdown(
    """
    <style>
    /* Compact, clean results table */
    .results-html-table {
        width: 100%;
        overflow: visible;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.10);
    }

    .results-html-table table {
        width: 100%;
        table-layout: fixed;
        border-collapse: collapse;
        font-size: 0.86rem;
    }

    .results-html-table th {
        padding: 0.25rem 0.48rem;
        text-align: left;
        white-space: nowrap;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.72);
        background: rgba(255, 255, 255, 0.025);
        border-bottom: 1px solid rgba(255, 255, 255, 0.10);
    }

    .results-html-table td {
        padding: 0.30rem 0.48rem;
        white-space: nowrap;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        vertical-align: middle;
    }

    /* Keep the whole table inside the page and wrap long college names
       to a maximum of two lines. */
    .results-html-table th:nth-child(1),
    .results-html-table td:nth-child(1) {
        width: 4%;
        text-align: center;
    }

    .results-html-table th:nth-child(2),
    .results-html-table td:nth-child(2) {
        width: 30%;
        white-space: normal;
        overflow: hidden;
        line-height: 1.2;
        overflow-wrap: anywhere;
        display: table-cell;
    }

    .results-html-table td:nth-child(2) {
        max-height: 2.4em;
    }

    .results-html-table th:nth-child(3),
    .results-html-table td:nth-child(3) {
        width: 20%;
        white-space: normal;
        overflow-wrap: anywhere;
    }

    .results-html-table th:nth-child(4),
    .results-html-table td:nth-child(4),
    .results-html-table th:nth-child(5),
    .results-html-table td:nth-child(5),
    .results-html-table th:nth-child(6),
    .results-html-table td:nth-child(6),
    .results-html-table th:nth-child(7),
    .results-html-table td:nth-child(7) {
        width: 6%;
        min-width: 6%;
        max-width: 6%;
        text-align: center;
        white-space: nowrap;
    }

    .results-html-table th:nth-child(9),
    .results-html-table td:nth-child(9) {
        width: 10%;
        text-align: center;
    }

    .results-html-table tr:last-child td {
        border-bottom: none;
    }

    div[data-testid="stTable"] {
        border-radius: 8px !important;
        overflow: hidden !important;
        border: 1px solid rgba(255, 255, 255, 0.10) !important;
    }

    div[data-testid="stTable"] table {
        width: 100% !important;
        table-layout: auto !important;
        border-collapse: collapse !important;
        font-size: 0.86rem !important;
    }

    div[data-testid="stTable"] thead th {
        padding: 0.25rem 0.48rem !important;
        height: 30px !important;
        line-height: 1 !important;
        background: rgba(255, 255, 255, 0.045) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.12) !important;
        color: rgba(255, 255, 255, 0.82) !important;
        font-weight: 650 !important;
        white-space: nowrap !important;
    }

    div[data-testid="stTable"] tbody td {
        padding: 0.30rem 0.48rem !important;
        height: 32px !important;
        line-height: 1.1 !important;
        white-space: nowrap !important;
    }

    div[data-testid="stTable"] tbody tr {
        height: 32px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.caption(
    "Following results are based on the latest available CAP cutoff for each college. "
    "A '/' means cutoff data was not available for that CAP round."
)

# Render the table as explicit HTML so unavailable CAP values are
# guaranteed to display as a literal slash instead of any dataframe
# missing-value marker.
import html

html_rows = []
html_rows.append("<thead><tr>" + "".join(
    f"<th>{html.escape(str(column))}</th>" for column in display_df.columns
) + "</tr></thead>")

body_rows = []
for _, row in display_df.iterrows():
    cells = []
    for column in display_df.columns:
        value = row[column]
        if column in ["CAP 1", "CAP 2", "CAP 3", "CAP 4"]:
            value = str(value).strip()
            if value in {"", ".", "nan", "NaN", "None", "<NA>", "-", "/"}:
                value = "/"
        else:
            value = str(value)
        cells.append(f"<td>{html.escape(value)}</td>")
    body_rows.append("<tr>" + "".join(cells) + "</tr>")

html_rows.append("<tbody>" + "".join(body_rows) + "</tbody>")

st.markdown(
    '<div class="results-html-table"><table>' + "".join(html_rows) + '</table></div>',
    unsafe_allow_html=True
)


# ============================================================
# DOWNLOAD RESULTS
# ============================================================

# Ensure unavailable CAP values are literal slashes in the CSV too.
for cap_column in ["CAP 1", "CAP 2", "CAP 3", "CAP 4"]:
    display_df[cap_column] = display_df[cap_column].map(
        lambda value: "/" if str(value).strip() in {"", ".", "nan", "NaN", "None", "<NA>", "-"} else str(value)
    )


csv_data = display_df.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    "⬇️ Download Results",
    data=csv_data,
    file_name="mht_cet_college_predictions.csv",
    mime="text/csv",
    use_container_width=True
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Results are based on "
    "previous CAP cutoff trends and are for guidance only."
    "All rights are reserved only to Bhavya Solanki (Developer)."
)