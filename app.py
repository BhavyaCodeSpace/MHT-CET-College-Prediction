import os
import sqlite3
import pandas as pd
import streamlit as st

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="MHT CET College Predictor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="auto"
)


# ============================================================
# RESPONSIVE STYLING & OVERLAP FIX
# ============================================================

st.markdown(
    """
<style>
.block-container {
    padding-top: 0.8rem !important;
    max-width: 1500px !important;
}

[data-testid="stHeader"] {
    background: transparent;
}

/* App background */
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 85% 8%, rgba(0, 170, 255, 0.10), transparent 28%),
        radial-gradient(circle at 45% 35%, rgba(192, 38, 255, 0.07), transparent 30%),
        #070a12;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at 15% 10%, rgba(192, 38, 255, 0.12), transparent 28%),
        linear-gradient(180deg, #090d1d 0%, #050914 100%);
    border-right: 1px solid rgba(150, 100, 255, 0.22);
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

[data-testid="stSidebar"] input,
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="input"] > div {
    background: rgba(4, 9, 22, 0.92) !important;
    border: 1px solid rgba(120, 145, 210, 0.22) !important;
    border-radius: 10px !important;
    color: #f6f8ff !important;
}

[data-testid="stSidebar"] .stButton > button {
    border-radius: 11px !important;
    border: 1px solid rgba(0, 200, 255, 0.55) !important;
    background: linear-gradient(100deg, #b90cff 0%, #7d27ff 48%, #007dff 100%) !important;
    color: white !important;
    font-weight: 700 !important;
    box-shadow: 0 0 22px rgba(160, 30, 255, 0.30);
}

/* NEON TITLE WITH SHINE EFFECT */
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
    box-shadow: 0 0 10px rgba(255, 43, 214, 0.30), 0 0 32px rgba(0, 200, 255, 0.16);
}

.neon-title::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -60%;
    width: 50%;
    height: 200%;
    background: linear-gradient(
        90deg,
        transparent,
        rgba(255, 255, 255, 0.22),
        transparent
    );
    transform: rotate(25deg);
    pointer-events: none;
    animation: shine-sweep 5s ease-in-out infinite;
}

@keyframes shine-sweep {
    0% {
        left: -60%;
    }
    40% {
        left: 140%;
    }
    100% {
        left: 140%;
    }
}

.neon-title h1 {
    margin: 0 !important;
    font-size: clamp(1.8rem, 3vw, 3rem) !important;
    color: #ffffff !important;
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

/* SUMMARY CARDS */
.summary-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 1rem;
    margin: 0 0 1rem 0;
}

.summary-card {
    min-height: 108px;
    padding: 1rem 1.15rem;
    border-radius: 15px;
    background: rgba(8, 14, 31, 0.82);
    display: flex;
    flex-direction: column;
    justify-content: center;
    border: 1px solid var(--accent);
    box-shadow: 0 0 22px var(--glow);
}

.summary-card .label {
    color: var(--accent);
    font-size: 0.86rem;
    font-weight: 700;
    margin-bottom: 0.28rem;
}

.summary-card .value {
    color: #ffffff;
    font-size: clamp(1.5rem, 2.5vw, 2.25rem);
    font-weight: 800;
}

.card-blue { --accent: #00c8ff; --glow: rgba(0,200,255,0.28); }
.card-purple { --accent: #ef55ff; --glow: rgba(239,85,255,0.28); }
.card-green { --accent: #20e890; --glow: rgba(32,232,144,0.24); }
.card-yellow { --accent: #ffbd1a; --glow: rgba(255,189,26,0.25); }

/* FIXED TABLE STYLING (PREVENTS OVERLAPPING & CUSTOM COLUMN WIDTHS) */
.results-html-table {
    width: 100%;
    overflow-x: auto;
    border-radius: 12px;
    border: 1px solid rgba(100, 145, 220, 0.24);
    background: rgba(8, 14, 31, 0.90);
    box-shadow: 0 0 22px rgba(0, 140, 255, 0.08);
    margin-bottom: 1rem;
}

.results-html-table table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
    table-layout: fixed;
}

.results-html-table th {
    padding: 0.75rem 0.75rem;
    text-align: left;
    font-weight: 700;
    color: #00c8ff;
    background: rgba(20, 28, 52, 0.96);
    border-bottom: 1px solid rgba(100, 145, 220, 0.3);
    word-break: break-word;
}

.results-html-table td {
    padding: 0.65rem 0.75rem;
    color: #e2e8f0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    vertical-align: middle;
    word-break: break-word;
}

/* Specific Column Width Control */
.results-html-table th:nth-child(1), .results-html-table td:nth-child(1) { 
    width: 4%; 
    white-space: nowrap; 
    text-align: center; 
} /* # Index column */
.results-html-table th:nth-child(2), .results-html-table td:nth-child(2) { 
    width: 36%; 
} /* College */
.results-html-table th:nth-child(3), .results-html-table td:nth-child(3) { 
    width: 18%; 
    white-space: nowrap; 
} /* Branch (Minimized and set to no wrap) */
.results-html-table th:nth-child(4), .results-html-table td:nth-child(4),
.results-html-table th:nth-child(5), .results-html-table td:nth-child(5),
.results-html-table th:nth-child(6), .results-html-table td:nth-child(6),
.results-html-table th:nth-child(7), .results-html-table td:nth-child(7) { 
    width: 6%; 
    white-space: nowrap; 
    text-align: center; 
} /* CAP 1 to 4 */
.results-html-table th:nth-child(8), .results-html-table td:nth-child(8) { 
    width: 14%; 
    white-space: nowrap; 
    text-align: center; 
} /* Chance column */

.results-html-table tr:hover td {
    background: rgba(40, 70, 130, 0.15);
}

.stButton > button, .stDownloadButton > button {
    width: 100%;
    min-height: 2.7rem;
    border-radius: 10px;
}
</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# DATABASE LOADING
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "data", "cutoffs_2025.db")


@st.cache_data
def load_database():
    if not os.path.exists(DATABASE):
        return pd.DataFrame()
    conn = sqlite3.connect(DATABASE)
    data = pd.read_sql_query("SELECT * FROM cutoffs", conn)
    conn.close()
    return data


df = load_database()

# District Mapping for "Other" Locations
LOCATION_MAPPING_FILE = os.path.join(BASE_DIR, "data", "other_college_district_mapping.csv")

if os.path.exists(LOCATION_MAPPING_FILE):
    location_mapping = pd.read_csv(LOCATION_MAPPING_FILE, dtype={"college_code": str})
    df["college_code"] = df["college_code"].astype(str).str.strip()
    location_mapping["college_code"] = location_mapping["college_code"].astype(str).str.strip()
    district_map = dict(zip(location_mapping["college_code"], location_mapping["corrected_district"]))
    other_mask = df["location"].astype(str).str.strip().str.lower() == "other"
    df.loc[other_mask, "location"] = df.loc[other_mask, "college_code"].map(district_map).fillna(df.loc[other_mask, "location"])

if df.empty:
    st.error("Something went wrong while loading the predictor database.")
    st.stop()

# Clean data
for col in ["category", "round", "college_name", "branch", "location"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

df["percentile"] = pd.to_numeric(df["percentile"], errors="coerce")
df = df.dropna(subset=["percentile"])

# Category, Location, Branch Options
category_order = ["OPEN", "Minority", "OBC", "SC", "ST", "VJ", "NT1", "NT2", "NT3", "SEBC", "EWS", "TFWS"]
categories = [c for c in category_order if c in df["category"].unique()]
locations = sorted(df["location"].dropna().unique().tolist())
location_options = ["All Locations"] + locations
branches = sorted(df["branch"].dropna().unique().tolist())


# ============================================================
# HEADER & SIDEBAR
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

st.sidebar.header("Your Details")

percentile = st.sidebar.number_input(
    "MHT CET Percentile", min_value=0.00, max_value=100.00, value=None, placeholder="Enter percentile", step=0.01, format="%.2f"
)
category = st.sidebar.selectbox("Category", categories, index=None, placeholder="Select category")
location = st.sidebar.selectbox("Preferred Location", location_options, index=None, placeholder="Select location")
branch_selection = st.sidebar.multiselect("Preferred Engineering Branches", branches, placeholder="Select branch(es)")

predict_clicked = st.sidebar.button("🔍 Predict Colleges", type="primary", use_container_width=True)

if predict_clicked:
    st.session_state["predicted"] = True
    st.session_state["search_percentile"] = percentile
    st.session_state["search_category"] = category
    st.session_state["search_location"] = location
    st.session_state["search_branches"] = branch_selection.copy()

predict = st.session_state.get("predicted", False)

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
    st.stop()

# Retrieve saved inputs
percentile = st.session_state["search_percentile"]
category = st.session_state["search_category"]
location = st.session_state["search_location"]
branch_selection = st.session_state["search_branches"]

if percentile is None or category is None or location is None or not branch_selection:
    st.warning("Please complete all input fields in the sidebar.")
    st.stop()


# ============================================================
# FILTER & PIVOT RESULTS
# ============================================================

results = df.copy()
results = results[results["category"].str.upper() == category.upper()]

if location != "All Locations":
    results = results[results["location"].str.lower() == location.lower()]

results = results[results["branch"].isin(branch_selection)]

round_order = ["CAP Round I", "CAP Round II", "CAP Round III", "CAP Round IV"]
identity_columns = [col for col in ["college_code", "choice_code", "college_name", "branch", "location", "category"] if col in results.columns]

round_data = results.groupby(identity_columns + ["round"], as_index=False)["percentile"].max()
cutoff_pivot = round_data.pivot_table(index=identity_columns, columns="round", values="percentile", aggfunc="max").reset_index()

for r_label in round_order:
    if r_label not in cutoff_pivot.columns:
        cutoff_pivot[r_label] = float("nan")

cutoff_cols = list(reversed(round_order))
cutoff_pivot["Latest Cutoff"] = cutoff_pivot[cutoff_cols].bfill(axis=1).iloc[:, 0]
results = cutoff_pivot[cutoff_pivot["Latest Cutoff"].notna()].copy()


def calculate_chance(cutoff):
    diff = percentile - cutoff
    if diff >= 3: return "🟢 Very High"
    if diff >= 1: return "🟢 High"
    if diff >= -1: return "🟡 Possible"
    if diff >= -3: return "🟠 Borderline"
    return "🔴 Less Likely"


results["Chance"] = results["Latest Cutoff"].apply(calculate_chance)
chance_order = {"🟢 Very High": 1, "🟢 High": 2, "🟡 Possible": 3, "🟠 Borderline": 4, "🔴 Less Likely": 5}
results["chance_order"] = results["Chance"].map(chance_order)
results = results.sort_values(["chance_order", "Latest Cutoff"], ascending=[False, False])


# ============================================================
# SUMMARY CARDS
# ============================================================

st.markdown(f"""
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
""", unsafe_allow_html=True)

if results.empty:
    st.warning("No matching colleges were found for your selected preferences.")
    st.stop()


# ============================================================
# DISPLAY TABLE (CLEAN & NON-OVERLAPPING)
# ============================================================

st.caption("Following results are based on the latest available CAP cutoff for each college.  A  '/'  means cutoff data was not available for that CAP round.")

def format_cutoff(val):
    if val is None or pd.isna(val): return "/"
    try:
        num = float(val)
        return f"{num:.2f}".rstrip("0").rstrip(".")
    except:
        return "/"

display_df = pd.DataFrame({
    "College": results["college_name"].astype(str),
    "Branch": results["branch"].astype(str),
    "CAP 1": results["CAP Round I"].map(format_cutoff),
    "CAP 2": results["CAP Round II"].map(format_cutoff),
    "CAP 3": results["CAP Round III"].map(format_cutoff),
    "CAP 4": results["CAP Round IV"].map(format_cutoff),
    "Chance": results["Chance"].astype(str)
}).reset_index(drop=True)

display_df.insert(0, "#", range(1, len(display_df) + 1))

import html
html_rows = ["<thead><tr>" + "".join(f"<th>{html.escape(str(col))}</th>" for col in display_df.columns) + "</tr></thead>"]

body_rows = []
for _, row in display_df.iterrows():
    cells = []
    for col in display_df.columns:
        val = str(row[col])
        if col in ["CAP 1", "CAP 2", "CAP 3", "CAP 4"] and val in {"", ".", "nan", "NaN", "None", "<NA>", "-", "/"}:
            val = "/"
        cells.append(f"<td>{html.escape(val)}</td>")
    body_rows.append("<tr>" + "".join(cells) + "</tr>")

html_rows.append("<tbody>" + "".join(body_rows) + "</tbody>")

st.markdown('<div class="results-html-table"><table>' + "".join(html_rows) + '</table></div>', unsafe_allow_html=True)


# ============================================================
# DOWNLOAD BUTTON
# ============================================================

csv_data = display_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Results as CSV",
    data=csv_data,
    file_name="mht_cet_college_predictions.csv",
    mime="text/csv",
    use_container_width=True
)

# ============================================================
# FOOTER
# ============================================================

st.divider()
st.caption("Results are based on previous CAP cutoff trends and are for guidance only. All rights reserved to Bhavya Solanki (Developer).")