import pandas as pd

# ==============================================
# 🔹 Load and Prepare Dataset
# ==============================================
DATA_PATH = "tata_motors_cleaned_reviews.csv"

try:
    df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    df = pd.DataFrame(columns=[
        "vehicle", "sentiment", "feature", "feature_sentiment",
        "competitor", "pain_point", "rating", "region"
    ])
    print("⚠️ Warning: Dataset not found! Using empty DataFrame.")


# ==============================================
# 📌 Helper: Apply Filters
# ==============================================
def apply_filters(df, vehicle=None, sentiment=None):
    """Filter dataset based on vehicle and sentiment."""
    df_filtered = df.copy()

    if vehicle and "vehicle" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["vehicle"].str.contains(vehicle, case=False, na=False)]

    if sentiment and "sentiment" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["sentiment"].str.contains(sentiment, case=False, na=False)]

    return df_filtered


# ==============================================
# 📊 Core Analysis Functions (with filters)
# ==============================================
def sentiment_overview(vehicle=None, sentiment=None):
    """Return overall sentiment distribution."""
    df_filtered = apply_filters(df, vehicle, sentiment)
    return df_filtered["sentiment"].value_counts().to_dict()


def feature_sentiment(vehicle=None, sentiment=None):
    """Return sentiment count for each feature."""
    df_filtered = apply_filters(df, vehicle, sentiment)
    if "feature" not in df_filtered.columns or "feature_sentiment" not in df_filtered.columns:
        return {}
    pivot = (
        df_filtered.groupby(["feature", "feature_sentiment"])
        .size()
        .unstack(fill_value=0)
    )
    return pivot.to_dict(orient="dict")


def competitor_analysis(vehicle=None, sentiment=None):
    """Return mentions of competitors."""
    df_filtered = apply_filters(df, vehicle, sentiment)
    if "competitor" not in df_filtered.columns:
        return {}
    return df_filtered["competitor"].value_counts().head(10).to_dict()


def painpoints(vehicle=None, sentiment=None):
    """Return most frequent pain points."""
    df_filtered = apply_filters(df, vehicle, sentiment)
    if "pain_point" not in df_filtered.columns:
        return {}
    return df_filtered["pain_point"].value_counts().head(10).to_dict()


def ratings_by_vehicle(vehicle=None, sentiment=None):
    """Return average rating per vehicle."""
    df_filtered = apply_filters(df, vehicle, sentiment)
    if "vehicle" not in df_filtered.columns or "rating" not in df_filtered.columns:
        return {}
    return df_filtered.groupby("vehicle")["rating"].mean().round(2).to_dict()


# ==============================================
# 🧠 Insights for Summary / KPI Cards
# ==============================================
def filter_insights(vehicle=None, sentiment=None):
    """Generate summary insights for KPIs."""
    df_filtered = apply_filters(df, vehicle, sentiment)

    if df_filtered.empty:
        return {
            "total_reviews": 0,
            "avg_rating": None,
            "pos_percent": 0,
            "neg_percent": 0,
            "growth_potential": 0,
        }

    total = len(df_filtered)
    pos = (df_filtered["sentiment"].str.contains("pos", case=False, na=False)).sum()
    neg = (df_filtered["sentiment"].str.contains("neg", case=False, na=False)).sum()

    insights = {
        "total_reviews": int(total),
        "avg_rating": round(df_filtered["rating"].mean(), 2) if "rating" in df_filtered else None,
        "pos_percent": round((pos / total) * 100, 2) if total else 0,
        "neg_percent": round((neg / total) * 100, 2) if total else 0,
        "growth_potential": round(((pos - neg) / total) * 100, 2) if total else 0,
        "dominant_sentiment": df_filtered["sentiment"].value_counts().idxmax() if "sentiment" in df_filtered else None,
        "top_features": df_filtered["feature"].value_counts().head(5).to_dict() if "feature" in df_filtered else {},
        "common_painpoints": df_filtered["pain_point"].value_counts().head(5).to_dict() if "pain_point" in df_filtered else {},
    }
    return insights
