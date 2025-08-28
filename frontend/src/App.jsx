import React from "react";
import PredictPanel from "./components/PredictPanel";
import TrainPanel from "./components/TrainPanel";

function App() {
  return (
    <div>
      <h1>ML Model Dashboard</h1>
      <TrainPanel />
      <PredictPanel />
    </div>
  );
}

export default App;
