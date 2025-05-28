
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="SmartClose AI Sales Predictor", layout="wide")

st.title("🤖 SmartClose – AI Sales Predictor")

st.markdown("Enter or upload opportunity data to get predictions, ROI estimates, and insights.")

# Sidebar for manual entry or upload
st.sidebar.header("Upload or Add Opportunity")
option = st.sidebar.radio("Choose Input Method", ("Upload CSV", "Manual Entry"))

# Placeholder DataFrame
data = pd.DataFrame(columns=["Client", "Deal Size", "Stage", "Last Activity (days)",
                             "Decision Maker", "Fit for Dynamics", "Notes"])

if option == "Upload CSV":
    uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
else:
    with st.sidebar.form("manual_form"):
        client = st.text_input("Client Name")
        deal_size = st.number_input("Deal Size (₪)", min_value=10000, step=5000)
        stage = st.selectbox("Deal Stage", ["Lead", "Discovery", "Proposal", "Negotiation", "Close"])
        last_activity = st.slider("Days Since Last Activity", 0, 60, 7)
        decision_maker = st.checkbox("Decision Maker Identified")
        fit = st.radio("Fit for Dynamics?", ("Yes", "No"))
        notes = st.text_area("Client Notes")
        submitted = st.form_submit_button("Add Opportunity")

        if submitted:
            new_row = {
                "Client": client,
                "Deal Size": deal_size,
                "Stage": stage,
                "Last Activity (days)": last_activity,
                "Decision Maker": "Yes" if decision_maker else "No",
                "Fit for Dynamics": fit,
                "Notes": notes
            }
            data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)

# Scoring logic
stage_weights = {"Lead": 10, "Discovery": 30, "Proposal": 60, "Negotiation": 80, "Close": 95}
def predict_score(row):
    base = stage_weights.get(row["Stage"], 0)
    activity_penalty = max(0, 20 - row["Last Activity (days)"]) * 0.5
    dm_bonus = 10 if row["Decision Maker"] == "Yes" else 0
    fit_bonus = 10 if row["Fit for Dynamics"] == "Yes" else 0
    score = base + activity_penalty + dm_bonus + fit_bonus
    return min(100, score)

def estimate_roi(deal_size):
    return int(deal_size * 3.2)  # Estimated 3.2x ROI

if not data.empty:
    data["Predicted Close %"] = data.apply(predict_score, axis=1)
    data["Estimated ROI (₪)"] = data["Deal Size"].apply(estimate_roi)

    st.subheader("📊 Opportunities Overview")
    st.dataframe(data.style.background_gradient(cmap='RdYlGn', subset=["Predicted Close %"]))

    st.markdown("---")
    st.subheader("📈 Summary Insights")
    st.metric("Top Opportunity", data.iloc[data["Predicted Close %"].idxmax()]["Client"])
    st.metric("Highest ROI Potential (₪)", f'{data["Estimated ROI (₪)"].max():,}')
else:
    st.info("No data yet. Add or upload opportunities to get started.")
