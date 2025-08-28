import React, { useState } from "react";

const PredictPanel = () => {
  const [input, setInput] = useState("");
  const [result, setResult] = useState(null);

  const handlePredict = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/predict", {  // ✅ FIXED
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: input }),
      });
      const data = await response.json();
      if (data.error) {
        setResult({ error: data.error });
      } else {
        setResult({ prediction: data.prediction });
      }
    } catch (error) {
      console.error("Error:", error);
      setResult({ error: "Error predicting" });
    }
  };

  return (
    <div className="panel">
      <h2>Make a Prediction</h2>
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Enter text..."
      ></textarea>
      <button onClick={handlePredict}>Predict</button>

      {result && result.error && <p className="result error">{result.error}</p>}
      {result && !result.error && (
        <div className="result">
          <p>Prediction: <strong>{result.prediction}</strong></p>
        </div>
      )}
    </div>
  );
};

export default PredictPanel;
