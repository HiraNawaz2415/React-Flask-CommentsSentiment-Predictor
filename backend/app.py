from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

app = Flask(__name__)
CORS(app)

MODEL_FILE = "model.pkl"

# --- TRAIN ENDPOINT ---
@app.route("/train", methods=["POST"])
def train():
    try:
        file = request.files.get("file")

        if not file:
            return jsonify({"error": "Please upload a CSV file"}), 400

        df = pd.read_csv(file)

        # Flexible column handling
        if "comment" in df.columns:
            X = df["comment"].astype(str)
        elif "text" in df.columns:
            X = df["text"].astype(str)
        else:
            return jsonify({"error": "CSV must have 'comment' or 'text' column"}), 400

        if "label" not in df.columns:
            return jsonify({"error": "CSV must have a 'label' column"}), 400
        y = df["label"]

        # Checks
        if len(df) < 5:
            return jsonify({"error": "Dataset must have at least 5 rows"}), 400
        if y.nunique() < 2:
            return jsonify({"error": "Dataset must contain at least 2 unique labels"}), 400

        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        vectorizer = TfidfVectorizer()
        X_train_vec = vectorizer.fit_transform(X_train)
        X_test_vec = vectorizer.transform(X_test)

        model = LogisticRegression(max_iter=500, solver="liblinear")
        model.fit(X_train_vec, y_train)

        # Accuracy
        y_pred = model.predict(X_test_vec)
        accuracy = accuracy_score(y_test, y_pred)

        # Save model + vectorizer
        with open(MODEL_FILE, "wb") as f:
            pickle.dump((model, vectorizer), f)

        return jsonify({
            "message": "Model trained successfully ✅",
            "accuracy": round(accuracy * 100, 2)  # %
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- PREDICT ENDPOINT ---
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "No text provided"}), 400

        if not os.path.exists(MODEL_FILE):
            return jsonify({"error": "Model not trained yet. Please upload CSV to /train first."}), 400

        text = data["text"]

        with open(MODEL_FILE, "rb") as f:
            model, vectorizer = pickle.load(f)

        X_vec = vectorizer.transform([text])
        prediction = model.predict(X_vec)[0]
        proba = model.predict_proba(X_vec).max()

        return jsonify({
            "prediction": str(prediction),
            "confidence": round(float(proba) * 100, 2)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
