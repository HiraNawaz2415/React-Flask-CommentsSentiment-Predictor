import React, { useState } from "react";

const TrainPanel = () => {
  const [message, setMessage] = useState("");
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleTrain = async () => {
    if (!file) {
      setMessage("Please select a CSV file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:5000/train", {  // ✅ FIXED
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      if (data.error) {
        setMessage("Error: " + data.error);
      } else {
        setMessage(
          `✅ Model trained successfully (Accuracy: ${(data.accuracy * 100).toFixed(2)}%)`
        );
      }
    } catch (error) {
      console.error("Error:", error);
      setMessage("Error training model.");
    }
  };

  return (
    <div className="panel">
      <h2>Train the Model</h2>
      <input type="file" accept=".csv" onChange={handleFileChange} />
      <button onClick={handleTrain}>Start Training</button>
      {message && <p className="result">{message}</p>}
    </div>
  );
};

export default TrainPanel;
