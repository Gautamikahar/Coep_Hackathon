import pandas as pd

# ===================================================
# 📂 Load Dataset Safely
# ===================================================
DATA_PATH = "tata_motors_cleaned_reviews.csv"

try:
    df = pd.read_csv(DATA_PATH)
    df.columns = [c.strip().lower() for c in df.columns]  # normalize headers
    print(f"✅ Loaded dataset with {len(df)} records.")
except FileNotFoundError:
    df = pd.DataFrame(columns=[
        "vehicle", "sentiment", "feature", "feature_sentiment",
        "competitor", "pain_point", "rating", "region"
    ])
    print("⚠️ Warning: Dataset not found! Using empty DataFrame.")


# ===================================================
# 💡 Helper Function: Compute Priority Index
# ===================================================
def compute_priority(cost, impact, duration):
    """Convert cost/impact/time into a weighted numeric priority score."""
    cost_map = {"Low": 3, "₹1 Cr": 3, "₹2 Cr": 2, "₹5–7 Cr": 2, "₹10 Cr": 1, "₹15–20 Cr": 1}
    impact_map = {"Low": 1, "Medium": 2, "High": 3, "Very High": 4}
    time_map = {"Ongoing": 4, "3–6 months": 3, "6–12 months": 2, "Immediate": 5}

    cost_score = cost_map.get(cost, 2)
    impact_score = impact_map.get(impact.split("—")[0] if "—" in impact else impact, 2)
    time_score = time_map.get(duration, 2)

    return round((impact_score * 2 + time_score - cost_score), 2)


# ===================================================
# 💡 Generate Actionable Recommendations
# ===================================================
def generate_recommendations(vehicle=None, sentiment=None):
    """
    Generate actionable sales growth recommendations for Tata Motors.
    Includes time duration, cost, impact, and risk analysis.
    """
    recs = {"Negative": [], "Positive": [], "Summary": ""}

    if df.empty:
        recs["Negative"].append({
            "issue": "Dataset not loaded",
            "suggestion": "Upload the latest Tata Motors sentiment dataset.",
            "time_duration": "Immediate",
            "cost": "N/A",
            "impact": "N/A",
            "risk": "System dependency",
            "priority_index": 0
        })
        recs["Summary"] = "⚠️ No dataset available to generate recommendations."
        return recs

    # Copy + filter data
    dff = df.copy()
    if vehicle:
        dff = dff[dff["vehicle"].str.contains(vehicle, case=False, na=False)]
    if sentiment:
        dff = dff[dff["sentiment"].str.contains(sentiment, case=False, na=False)]

    # ===============================
    # 🔴 NEGATIVE INSIGHTS
    # ===============================
    if "pain_point" in dff.columns and (dff["pain_point"].str.contains("service", case=False, na=False)).sum() > 10:
        recs["Negative"].append({
            "issue": "Service Delays / Quality Complaints",
            "suggestion": "Expand Tier-2 city service centers & digitize booking slots.",
            "time_duration": "6–12 months",
            "cost": "₹15–20 Cr",
            "impact": "High",
            "risk": "Hiring bottlenecks, supply chain constraints",
            "priority_index": compute_priority("₹15–20 Cr", "High", "6–12 months")
        })

    if "pain_point" in dff.columns and (dff["pain_point"].str.contains("price", case=False, na=False)).sum() > 10:
        recs["Negative"].append({
            "issue": "High Price Perception",
            "suggestion": "Introduce festive offers and flexible financing (EMIs or exchange bonus).",
            "time_duration": "3–6 months",
            "cost": "₹5–7 Cr",
            "impact": "High",
            "risk": "Short-term margin compression",
            "priority_index": compute_priority("₹5–7 Cr", "High", "3–6 months")
        })

    if "pain_point" in dff.columns and (dff["pain_point"].str.contains("mileage", case=False, na=False)).sum() > 10:
        recs["Negative"].append({
            "issue": "Mileage-related Negative Feedback",
            "suggestion": "Run public mileage challenge campaigns; improve engine optimization.",
            "time_duration": "4–8 months",
            "cost": "₹3–5 Cr",
            "impact": "Medium",
            "risk": "Dependent on R&D execution speed",
            "priority_index": compute_priority("₹3–5 Cr", "Medium", "4–8 months")
        })

    if "competitor" in dff.columns and not dff["competitor"].dropna().empty:
        top_comp = dff["competitor"].value_counts().idxmax()
        recs["Negative"].append({
            "issue": f"Competition from {top_comp}",
            "suggestion": f"Highlight Tata’s safety & build quality advantages over {top_comp}.",
            "time_duration": "2–3 months",
            "cost": "₹2 Cr",
            "impact": "Medium",
            "risk": "Ad-fatigue or counter-campaign from rival",
            "priority_index": compute_priority("₹2 Cr", "Medium", "2–3 months")
        })

    # ===============================
    # 🟢 POSITIVE OPPORTUNITIES
    # ===============================
    if "feature" in dff.columns and (dff["feature"].str.contains("comfort", case=False, na=False)).sum() > 10:
        recs["Positive"].append({
            "opportunity": "Comfort & Space Perception",
            "suggestion": "Position Safari as the ultimate family SUV for long-distance trips.",
            "time_duration": "Ongoing",
            "cost": "₹1 Cr",
            "impact": "High",
            "priority_index": compute_priority("₹1 Cr", "High", "Ongoing")
        })

    if "vehicle" in dff.columns and (dff["vehicle"].str.contains("Nexon EV", case=False, na=False)).sum() > 10:
        recs["Positive"].append({
            "opportunity": "EV Adoption Trend",
            "suggestion": "Promote Nexon EV with government subsidy awareness & charging-infra tie-ups.",
            "time_duration": "6 months",
            "cost": "₹10 Cr",
            "impact": "Very High",
            "priority_index": compute_priority("₹10 Cr", "Very High", "6 months")
        })

    # ===============================
    # ⚪ DEFAULT FALLBACK
    # ===============================
    if not recs["Negative"] and not recs["Positive"]:
        recs["Positive"].append({
            "opportunity": "Stable Customer Sentiment",
            "suggestion": "Continue monitoring sentiment trends and competitor dynamics monthly.",
            "time_duration": "Ongoing",
            "cost": "Minimal",
            "impact": "Low",
            "priority_index": compute_priority("Minimal", "Low", "Ongoing")
        })

    # Executive Summary
    neg_count = len(recs["Negative"])
    pos_count = len(recs["Positive"])
    recs["Summary"] = (
        f"📊 {pos_count} growth opportunities and {neg_count} critical issues detected. "
        f"Tata should focus on service expansion and EV momentum for maximum ROI."
    )

    return recs
