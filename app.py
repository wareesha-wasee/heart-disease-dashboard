 

import streamlit as st
import base64
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Heart Disease | EDA Dashboard",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Elegant medical palette
MAROON = "#76243D"
BURGUNDY = "#54172B"
ROSE = "#C56B86"
BLUSH = "#F7E8ED"
PALE = "#FFF8FA"
PURPLE = "#8D7BAA"
TEAL = "#6D9E98"
BLUE = "#789DB8"
GOLD = "#C99B55"
INK = "#3D3035"
PALETTE = [MAROON, ROSE, PURPLE, TEAL, BLUE, GOLD]

# --------------------------------------------------
# CSS
# --------------------------------------------------
st.markdown("""
<style>
.stApp { background: #FFF7F9; color: #3D3035; }

[data-testid="stHeader"] {
    background: rgba(255,247,249,0.92);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #F5DFE7 0%, #F9EAF0 100%);
    border-right: 1px solid #E7C6D1;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #76243D !important;
}

[data-testid="stSidebar"] label {
    color: #513944 !important;
    font-weight: 600;
}

h1, h2, h3 {
    color: #76243D !important;
}

/* TITLE BANNER */
.hero {
    background: linear-gradient(
        115deg,
        #54172B 0%,
        #76243D 58%,
        #A64D68 100%
    );
    border-radius: 22px;
    padding: 20px 26px;
    color: white;
    box-shadow: 0 9px 25px rgba(84,23,43,.16);
    margin-bottom: 18px;

    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 18px;
}

.hero-copy {
    flex: 1;
    min-width: 0;
}

/* SMALL HEART IMAGE */
.hero-heart {
    width: 105px;
    height: 105px;
    object-fit: contain;
    flex-shrink: 0;
}

.hero h1 {
    color: white !important;
    margin: 0;
    font-size: 31px;
}

.hero p {
    color: #F8E8ED !important;
    margin: 7px 0 0 0;
    font-size: 14px;
}

@media (max-width: 640px) {
    .hero {
        padding: 17px 18px;
        gap: 10px;
    }

    .hero-heart {
        width: 76px;
        height: 76px;
    }

    .hero h1 {
        font-size: 23px;
    }

    .hero p {
        font-size: 12px;
    }
}

.eyebrow {
    color: #F1C8D5;
    text-transform: uppercase;
    letter-spacing: 2px;
    font-size: 10px;
    font-weight: 700;
}

.section-label {
    color: #76243D;
    font-size: 21px;
    font-weight: 800;
    margin: 20px 0 12px 0;
}

.kpi {
    background: #FFFFFF;
    border: 1px solid #F0DDE4;
    border-top: 4px solid #76243D;
    border-radius: 16px;
    padding: 17px 15px 14px 15px;
    min-height: 112px;
    box-shadow: 0 5px 17px rgba(84,23,43,.055);
}

.kpi-label {
    color: #79666E;
    font-size: 12px;
    font-weight: 700;
}

.kpi-value {
    font-size: 27px;
    font-weight: 850;
    margin-top: 7px;
}

.kpi-foot {
    color: #A18E95;
    font-size: 10px;
    margin-top: 3px;
}

.insight {
    background: white;
    border: 1px solid #F0DDE4;
    border-left: 4px solid #C56B86;
    border-radius: 13px;
    padding: 15px;
    min-height: 104px;
    box-shadow: 0 4px 13px rgba(84,23,43,.045);
}

.insight b {
    color: #76243D;
    display: block;
    margin-bottom: 6px;
}

.insight span {
    color: #5B4B51;
    font-size: 13px;
}

div[data-testid="stPlotlyChart"] {
    background: white;
    border: 1px solid #F0DDE4;
    border-radius: 15px;
    padding: 7px;
    box-shadow: 0 4px 14px rgba(84,23,43,.045);
}

.stButton button {
    background: #76243D;
    color: white;
    border-radius: 9px;
}

hr {
    border-color: #EBD4DD;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    folder = Path(__file__).parent

    candidates = [
        folder / "heart_cleveland_upload.csv",
        folder / "heart_cleveland_upload(2).csv"
    ]

    csv_file = next(
        (p for p in candidates if p.exists()),
        None
    )

    if csv_file is None:
        other_csvs = list(folder.glob("*.csv"))

        if len(other_csvs) == 1:
            csv_file = other_csvs[0]
        else:
            raise FileNotFoundError(
                "CSV file not found. Place heart_cleveland_upload.csv beside app.py."
            )

    data = pd.read_csv(csv_file)
    data.columns = data.columns.str.strip().str.lower()

    return data, csv_file.name


try:
    df, source_filename = load_data()

except Exception as exc:
    st.error(str(exc))
    st.stop()


required = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "thalach",
    "condition"
]

missing = [c for c in required if c not in df.columns]

if missing:
    st.error(f"Required columns are missing: {missing}")
    st.write("CSV columns found:", df.columns.tolist())
    st.stop()


# --------------------------------------------------
# SIDEBAR / FILTERS
# --------------------------------------------------
with st.sidebar:

    st.markdown(
        "<div style='text-align:center;padding:5px 0 10px'>"
        "<div style='font-size:43px'>♡</div>"
        "<h2 style='margin:0;color:#76243D'>HEART HEALTH</h2>"
        "<div style='font-size:11px;color:#80616D;letter-spacing:1px'>"
        "CLEVELAND DATA STUDY</div></div>",
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.markdown("### Refine the data")

    sex_options = sorted(
        df["sex"].dropna().unique().tolist()
    )

    chosen_sex = st.multiselect(
        "Sex code",
        sex_options,
        default=sex_options
    )

    condition_options = sorted(
        df["condition"].dropna().unique().tolist()
    )

    chosen_condition = st.multiselect(
        "Heart condition",
        condition_options,
        default=condition_options
    )

    age_min = int(df.age.min())
    age_max = int(df.age.max())

    age_range = st.slider(
        "Patient age range",
        age_min,
        age_max,
        (age_min, age_max)
    )

    st.markdown("---")
    st.caption("Dataset: Heart Disease Cleveland")
    st.caption(f"Source file: {source_filename}")


# --------------------------------------------------
# FILTERED DATA
# --------------------------------------------------
filtered = df[
    df["sex"].isin(chosen_sex)
    & df["condition"].isin(chosen_condition)
    & df["age"].between(age_range[0], age_range[1])
].copy()

if filtered.empty:
    st.warning(
        "No records match these filters. Change your selections."
    )
    st.stop()


# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def styled(fig, height=350):

    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Arial",
            color=INK,
            size=11
        ),
        title=dict(
            font=dict(color=MAROON, size=16),
            x=0.03
        ),
        margin=dict(
            l=25,
            r=20,
            t=55,
            b=35
        ),
        height=height,
        legend_title_text=""
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False
    )

    fig.update_yaxes(
        gridcolor="#F2E7EB",
        zeroline=False
    )

    return fig


def section(text):
    st.markdown(
        f"<div class='section-label'>{text}</div>",
        unsafe_allow_html=True
    )


 
# --------------------------------------------------
# HEADER WITH SMALL HEART IMAGE
# --------------------------------------------------
title_col, image_col = st.columns([5, 1])

with title_col:
    st.markdown("""
    <div class="hero" style="min-height:125px; display:flex;
         flex-direction:column; justify-content:center;">
        <div class="eyebrow">
            Exploratory data analysis · Medical dataset
        </div>
        <h1>♡ Heart Disease Analytics</h1>
        <p>
            Exploring patient characteristics, clinical measurements
            and heart condition patterns.
        </p>
    </div>
    """, unsafe_allow_html=True)

with image_col:
    heart_path = Path(__file__).parent / "heart.png"

    if heart_path.exists():
        st.image(str(heart_path), width=105)


# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------
section("At a glance")

n = len(filtered)
avg_age = filtered.age.mean()
avg_chol = filtered.chol.mean()
positive = int((filtered.condition > 0).sum())

kpis = [
    (
        "PATIENT RECORDS",
        f"{n:,}",
        "Filtered sample",
        MAROON
    ),
    (
        "MEAN AGE",
        f"{avg_age:.1f}",
        "Years",
        ROSE
    ),
    (
        "MEAN CHOLESTEROL",
        f"{avg_chol:.1f}",
        "Dataset measurement",
        PURPLE
    ),
    (
        "CONDITION = 1",
        f"{positive:,}",
        f"{positive/n*100:.1f}% of filtered records",
        TEAL
    )
]

cols = st.columns(4)

for col, (label, value, foot, color) in zip(cols, kpis):

    with col:

        st.markdown(
            f"<div class='kpi' style='border-top-color:{color}'>"
            f"<div class='kpi-label'>{label}</div>"
            f"<div class='kpi-value' style='color:{color}'>{value}</div>"
            f"<div class='kpi-foot'>{foot}</div></div>",
            unsafe_allow_html=True
        )


# --------------------------------------------------
# DEMOGRAPHICS / UNIVARIATE
# --------------------------------------------------
section("01 · Patient profile")

left, right = st.columns(2)

with left:

    fig = px.histogram(
        filtered,
        x="age",
        nbins=16,
        marginal="box",
        title="Age distribution of patients",
        color_discrete_sequence=[ROSE]
    )

    fig.update_layout(
        xaxis_title="Age (years)",
        yaxis_title="Number of patients"
    )

    st.plotly_chart(
        styled(fig),
        use_container_width=True
    )


with right:

    cp_counts = (
        filtered["cp"]
        .value_counts()
        .sort_index()
        .rename_axis("Chest pain type")
        .reset_index(name="Patients")
    )

    fig = px.bar(
        cp_counts,
        x="Chest pain type",
        y="Patients",
        title="Patients by chest pain type",
        color="Chest pain type",
        color_discrete_sequence=PALETTE
    )

    fig.update_layout(
        showlegend=False,
        yaxis_title="Number of patients"
    )

    st.plotly_chart(
        styled(fig),
        use_container_width=True
    )


left, right = st.columns(2)

with left:

    fig = px.histogram(
        filtered,
        x="chol",
        nbins=18,
        title="Cholesterol level distribution",
        color_discrete_sequence=[PURPLE]
    )

    fig.update_layout(
        xaxis_title="Cholesterol",
        yaxis_title="Number of patients"
    )

    st.plotly_chart(
        styled(fig),
        use_container_width=True
    )


with right:

    cond_counts = (
        filtered["condition"]
        .value_counts()
        .sort_index()
        .rename_axis("Condition")
        .reset_index(name="Patients")
    )

    fig = px.pie(
        cond_counts,
        names="Condition",
        values="Patients",
        title="Heart condition categories",
        hole=0.52,
        color_discrete_sequence=[TEAL, MAROON]
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )

    st.plotly_chart(
        styled(fig),
        use_container_width=True
    )


# --------------------------------------------------
# BIVARIATE
# --------------------------------------------------
section("02 · Relationships between health measures")

left, right = st.columns(2)

with left:

    fig = px.scatter(
        filtered,
        x="age",
        y="thalach",
        color="condition",
        title="Age vs maximum heart rate",
        color_discrete_sequence=[TEAL, MAROON],
        labels={
            "age": "Age (years)",
            "thalach": "Maximum heart rate"
        }
    )

    st.plotly_chart(
        styled(fig),
        use_container_width=True
    )


with right:

    fig = px.scatter(
        filtered,
        x="chol",
        y="trestbps",
        color="condition",
        title="Cholesterol vs resting blood pressure",
        color_discrete_sequence=[PURPLE, GOLD],
        labels={
            "chol": "Cholesterol",
            "trestbps": "Resting blood pressure"
        }
    )

    st.plotly_chart(
        styled(fig),
        use_container_width=True
    )


# --------------------------------------------------
# GROUP COMPARISON
# --------------------------------------------------
section("03 · Group comparison")

left, right = st.columns(2)

with left:

    mean_chol = (
        filtered.groupby("condition", as_index=False)["chol"].mean()
    )

    fig = px.bar(
        mean_chol,
        x="condition",
        y="chol",
        color="condition",
        title="Average cholesterol by condition",
        color_discrete_sequence=[TEAL, MAROON],
        labels={
            "condition": "Condition category",
            "chol": "Average cholesterol"
        }
    )

    fig.update_layout(showlegend=False)

    st.plotly_chart(
        styled(fig),
        use_container_width=True
    )


with right:

    sex_condition = (
        filtered.groupby(["sex", "condition"])
        .size()
        .reset_index(name="Patients")
    )

    fig = px.bar(
        sex_condition,
        x="sex",
        y="Patients",
        color="condition",
        barmode="group",
        title="Condition categories across sex groups",
        color_discrete_sequence=[TEAL, MAROON],
        labels={
            "sex": "Sex code",
            "Patients": "Number of patients"
        }
    )

    st.plotly_chart(
        styled(fig),
        use_container_width=True
    )


# --------------------------------------------------
# CORRELATION HEATMAP
# --------------------------------------------------
section("04 · Correlation overview")

numeric = filtered.select_dtypes(include="number")

if numeric.shape[1] >= 2:

    corr = numeric.corr()

    fig = px.imshow(
        corr,
        text_auto=".2f",
        aspect="auto",
        title="Correlation heatmap of numeric features",
        color_continuous_scale=[
            "#E8DCE2",
            "#D58CA5",
            "#76243D"
        ],
        zmin=-1,
        zmax=1
    )

    st.plotly_chart(
        styled(fig, height=510),
        use_container_width=True
    )


# --------------------------------------------------
# EDA FINDINGS
# --------------------------------------------------
section("05 · Key findings from the EDA")

a, b, c = st.columns(3)

with a:

    st.markdown(
        "<div class='insight'><b>Age & heart rate</b>"
        "<span>Age and maximum heart rate show a negative correlation "
        "(approximately −0.395).</span></div>",
        unsafe_allow_html=True
    )


with b:

    st.markdown(
        "<div class='insight'><b>Cholesterol & condition</b>"
        "<span>Mean cholesterol: 243.49 for condition 0 and "
        "251.85 for condition 1.</span></div>",
        unsafe_allow_html=True
    )


with c:

    st.markdown(
        "<div class='insight'><b>Data quality</b>"
        "<span>No missing values or duplicate rows were found. "
        "Potential outliers were retained.</span></div>",
        unsafe_allow_html=True
    )


# --------------------------------------------------
# DATA QUALITY / OUTLIERS
# --------------------------------------------------
section("06 · Data quality checks")

q1, q2, q3 = st.columns(3)

q1.metric(
    "Missing values",
    int(df.isna().sum().sum())
)

q2.metric(
    "Duplicate rows",
    int(df.duplicated().sum())
)

q3.metric(
    "Columns",
    df.shape[1]
)


out_left, out_right = st.columns(2)

for col, target in [
    ("trestbps", out_left),
    ("chol", out_right)
]:

    with target:

        q1v = df[col].quantile(.25)
        q3v = df[col].quantile(.75)

        iqr = q3v - q1v

        lo = q1v - 1.5 * iqr
        hi = q3v + 1.5 * iqr

        count = int(
            ((df[col] < lo) | (df[col] > hi)).sum()
        )

        fig = px.box(
            df,
            y=col,
            points="outliers",
            title=f"{col.upper()} · IQR outlier check",
            color_discrete_sequence=[
                ROSE if col == "trestbps" else PURPLE
            ]
        )

        st.plotly_chart(
            styled(fig, height=300),
            use_container_width=True
        )

        st.caption(
            f"IQR limits: {lo:g} to {hi:g} · "
            f"Potential outliers: {count}. "
            "Retained as potentially genuine measurements."
        )


# --------------------------------------------------
# RAW DATA
# --------------------------------------------------
section("07 · Explore the records")

if st.checkbox("Show raw patient data"):

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download filtered data as CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="filtered_heart_disease_data.csv",
        mime="text/csv"
    )


# --------------------------------------------------
# FOOTER / TRANSPARENCY
# --------------------------------------------------
st.markdown("---")

st.markdown(
    "<div style='text-align:center;padding:12px;color:#80616D'>"
    "<b style='color:#76243D'>♡ Heart Disease Cleveland · EDA Dashboard</b><br>"
    "<span style='font-size:11px'>Descriptive analysis only — "
    "correlations do not establish causation.</span>"
    "</div>",
    unsafe_allow_html=True
)

