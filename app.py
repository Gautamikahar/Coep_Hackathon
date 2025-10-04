from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import analysis
import recommender

app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)

# ========== ROUTES ==========

@app.route("/sentiment")
def sentiment():
    vehicle = request.args.get("vehicle")
    sentiment = request.args.get("sentiment")
    return jsonify(analysis.sentiment_overview(vehicle, sentiment))


@app.route("/features")
def features():
    vehicle = request.args.get("vehicle")
    sentiment = request.args.get("sentiment")
    return jsonify(analysis.feature_sentiment(vehicle, sentiment))


@app.route("/competitors")
def competitors():
    vehicle = request.args.get("vehicle")
    sentiment = request.args.get("sentiment")
    return jsonify(analysis.competitor_analysis(vehicle, sentiment))


@app.route("/ratings")
def ratings():
    vehicle = request.args.get("vehicle")
    sentiment = request.args.get("sentiment")
    return jsonify(analysis.ratings_by_vehicle(vehicle, sentiment))


@app.route("/filter")
def filter_summary():
    vehicle = request.args.get("vehicle")
    sentiment = request.args.get("sentiment")
    return jsonify(analysis.filter_insights(vehicle, sentiment))


@app.route("/recommendations")
def recs():
    vehicle = request.args.get("vehicle")
    sentiment = request.args.get("sentiment")
    return jsonify(recommender.generate_recommendations(vehicle, sentiment))


@app.route("/summary")
def summary():
    vehicle = request.args.get("vehicle")
    sentiment = request.args.get("sentiment")
    insights = analysis.filter_insights(vehicle, sentiment)

    summary_text = (
        f"Analyzed {insights.get('total_reviews', 0)} posts. "
        f"Dominant sentiment: {insights.get('dominant_sentiment', 'N/A')}. "
        f"Avg rating: {insights.get('avg_rating', 'N/A')}. "
        f"Positive sentiment: {insights.get('pos_percent', 0)}%, "
        f"Negative sentiment: {insights.get('neg_percent', 0)}%. "
        f"Top features: {', '.join(insights.get('top_features', {}).keys()) or 'None'}. "
        f"Main pain points: {', '.join(insights.get('common_painpoints', {}).keys()) or 'None'}."
    )
    return jsonify({"summary": summary_text})


@app.route("/")
def serve_dashboard():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)


if __name__ == "__main__":
    print("🚗 Tata Motors Sentiment Dashboard Running → http://127.0.0.1:5000/")
    app.run(debug=True)
