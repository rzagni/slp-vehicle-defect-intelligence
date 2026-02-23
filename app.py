import streamlit as st
import plotly.express as px
import numpy as np
import os
from dotenv import load_dotenv
from openai import OpenAI

from nhtsa_client import get_complaints, get_recalls, decode_vin
from analysis import analyze_complaints


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("OPENAI_API_KEY not found. Please set it in your .env file.")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="SLP Vehicle Defect Intelligence",
    layout="wide"
)


# ==========================================
# SESSION STATE INIT
# ==========================================

defaults = {
    "analysis_data": None,
    "complaints_data": None,
    "recalls_data": None,
    "complaint_embeddings": None,
    "selected_vin": None,
    "selected_make": None,
    "selected_model": None,
    "selected_year": None,
}

for key, value in defaults.items():
    st.session_state.setdefault(key, value)


# ==========================================
# EMBEDDING UTILITIES
# ==========================================

def get_embedding(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(response.data[0].embedding)


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# ==========================================
# HEADER
# ==========================================

st.markdown("""
<div style="background-color:#0d1b2a; padding:30px; border-radius:8px;">
    <h1 style="color:white; margin:0;">SLP Vehicle Defect Intelligence Dashboard</h1>
    <p style="color:#d1d5db; margin-top:5px;">
        Internal litigation analytics platform for identifying defect patterns and evaluating case strength.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")


# ==========================================
# VEHICLE LOOKUP FORM
# ==========================================

with st.form("vehicle_form", clear_on_submit=True):

    vin_input = st.text_input("Enter VIN (optional)")
    col1, col2, col3 = st.columns(3)
    make_input = col1.text_input("Make")
    model_input = col2.text_input("Model")
    year_input = col3.text_input("Year")

    left_spacer, center_col, right_spacer = st.columns([2, 3, 2])

    with center_col:
        btn1, btn2 = st.columns(2)
        analyze_button = btn1.form_submit_button(
            "Analyze Vehicle", use_container_width=True
        )
        clear_button = btn2.form_submit_button(
            "Clear / New Analysis", use_container_width=True
        )


# ==========================================
# CLEAR LOGIC
# ==========================================

if clear_button:
    for key in defaults.keys():
        st.session_state[key] = None
    st.rerun()


# ==========================================
# ANALYZE VEHICLE
# ==========================================

if analyze_button:

    make = make_input
    model = model_input
    year = year_input

    # VIN decode override
    if vin_input:
        with st.spinner("Decoding VIN..."):
            vin_data = decode_vin(vin_input)

        if not vin_data:
            st.error("Unable to decode VIN.")
            st.stop()

        make = vin_data["make"]
        model = vin_data["model"]
        year = vin_data["year"]

    if not (make and model and year):
        st.error("Please provide VIN or Make/Model/Year.")
        st.stop()

    with st.spinner("Analyzing NHTSA data..."):
        complaints = get_complaints(make, model, year)
        recalls = get_recalls(make, model, year)
        analysis = analyze_complaints(complaints)

    # Store analysis
    st.session_state.complaints_data = complaints
    st.session_state.recalls_data = recalls
    st.session_state.analysis_data = analysis

    # Store selected vehicle info (FINAL resolved values)
    st.session_state.selected_vin = vin_input if vin_input else None
    st.session_state.selected_make = make
    st.session_state.selected_model = model
    st.session_state.selected_year = year

    # Generate embeddings once
    if complaints:
        with st.spinner("Generating complaint AI embeddings..."):
            summaries = [c["summary"] or "" for c in complaints]
            st.session_state.complaint_embeddings = [
                get_embedding(text[:2000]) for text in summaries
            ]
    else:
        st.session_state.complaint_embeddings = None


# ==========================================
# DISPLAY DASHBOARD
# ==========================================

if st.session_state.analysis_data:

    # ======================================
    # VEHICLE INFORMATION BANNER
    # ======================================

    with st.container(border=True):
        st.markdown("Vehicle Information")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("VIN", st.session_state.selected_vin or "—")
        c2.metric("Make", st.session_state.selected_make)
        c3.metric("Model", st.session_state.selected_model)
        c4.metric("Year", st.session_state.selected_year)

    st.markdown("---")

    complaints = st.session_state.complaints_data
    recalls = st.session_state.recalls_data
    analysis = st.session_state.analysis_data
    severity = analysis.get("severity", {})

    # ======================================
    # LITIGATION RISK SCORE
    # ======================================

    risk_score = (
        severity.get("crashes", 0) * 3 +
        severity.get("injuries", 0) * 2 +
        severity.get("fires", 0) * 2 +
        severity.get("deaths", 0) * 5
    )

    if risk_score > 10:
        st.error("High Litigation Risk")
    elif risk_score > 3:
        st.warning("Moderate Litigation Risk")
    else:
        st.success("Low Litigation Risk")

    # ======================================
    # METRICS
    # ======================================

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Complaints", severity.get("total_complaints", 0))
    col2.metric("Crashes", severity.get("crashes", 0))
    col3.metric("Injuries", severity.get("injuries", 0))
    col4.metric("Fires", severity.get("fires", 0))
    col5.metric("Deaths", severity.get("deaths", 0))

    st.markdown("---")

    # ======================================
    # SEMANTIC SEARCH
    # ======================================

    st.subheader("🔎 Semantic Search — Find Similar Complaints")

    semantic_query = st.text_area("Describe the client's issue:")
    run_semantic_search = st.button("Run Semantic Search")

    if run_semantic_search:

        if not semantic_query:
            st.warning("Please enter a symptom description.")
        elif not complaints:
            st.warning("No complaints available.")
        elif not st.session_state.complaint_embeddings:
            st.warning("Embeddings not available.")
        else:
            with st.spinner("Analyzing similarity..."):

                query_embedding = get_embedding(semantic_query)

                scores = [
                    cosine_similarity(query_embedding, emb)
                    for emb in st.session_state.complaint_embeddings
                ]

                ranked_indices = np.argsort(scores)[::-1][:5]

                st.markdown("### Top 5 Most Similar Complaints")

                for idx in ranked_indices:
                    complaint = complaints[idx]
                    similarity_score = round(scores[idx], 3)

                    st.markdown(f"""
                    **Similarity Score:** {similarity_score}  
                    **Component:** {complaint["component"]}  
                    **State:** {complaint["state"]}  

                    {complaint["summary"][:500]}  

                    ---
                    """)

    st.markdown("---")

    # ======================================
    # COMPONENT CHART
    # ======================================

    if not analysis["component_counts"].empty:
        st.subheader("Top Failing Components")

        fig = px.bar(
            analysis["component_counts"].head(10),
            x="component",
            y="count",
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

    # ======================================
    # TREND CHART
    # ======================================

    if not analysis["yearly_trend"].empty:
        st.subheader("Complaint Trend Over Time")

        fig2 = px.line(
            analysis["yearly_trend"],
            x="year",
            y="count",
            template="plotly_white"
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ======================================
    # GEOGRAPHIC MAP
    # ======================================

    if not analysis["state_counts"].empty:
        st.subheader("Geographic Distribution")

        fig3 = px.choropleth(
            analysis["state_counts"],
            locations="state",
            locationmode="USA-states",
            color="count",
            scope="usa",
            template="plotly_white"
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # ======================================
    # RECALLS
    # ======================================

    st.subheader("Recall Activity")

    if recalls:
        for recall in recalls:
            st.markdown(f"""
            **Component:** {recall.get("Component","Recall")}  
            **Safety Risk:** {recall.get("Consequence","N/A")}  
            **Remedy:** {recall.get("Remedy","N/A")}  

            ---
            """)
    else:
        st.info("No recalls found.")

    # ======================================
    # RAW TABLE
    # ======================================

    st.subheader("Complaint Explorer")

    st.dataframe(
        complaints,
        use_container_width=True,
        height=350
    )