from flask import Flask, request, jsonify
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle
import os

app = Flask(__name__)

MODEL_FILE = "model.pkl"

@app.route("/train", methods=["POST"])
def train_model():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    try:
        # Read CSV directly from uploaded file
        df = pd.read_csv(file)

        # Expecting 2 columns: "text" and "label"
        if "text" not in df.columns or "label" not in df.columns:
            return jsonify({"error": "CSV must have 'text' and 'label' columns"}), 400

        X = df["text"]
        y = df["label"]

        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Vectorization
        vectorizer = CountVectorizer()
        X_train_vec = vectorizer.fit_transform(X_train)
        X_test_vec = vectorizer.transform(X_test)

        # Train model
        model = MultinomialNB()
        model.fit(X_train_vec, y_train)

        # Save vectorizer and model
        with open(MODEL_FILE, "wb") as f:
            pickle.dump((vectorizer, model), f)

        accuracy = model.score(X_test_vec, y_test)

        return jsonify({"message": "Model trained successfully", "accuracy": accuracy})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/predict", methods=["POST"])
def predict():
    if not os.path.exists(MODEL_FILE):
        return jsonify({"error": "Model not trained yet"}), 400

    data = request.json
    if "text" not in data:
        return jsonify({"error": "Missing 'text' field"}), 400

    with open(MODEL_FILE, "rb") as f:
        vectorizer, model = pickle.load(f)

    text = data["text"]
    X_vec = vectorizer.transform([text])
    prediction = model.predict(X_vec)[0]

    return jsonify({"prediction": prediction})


if __name__ == "__main__":
    app.run(debug=True)
