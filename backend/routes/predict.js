const express = require("express");
const { PythonShell } = require("python-shell");
const router = express.Router();

router.post("/predict", (req, res) => {
  const { events } = req.body;

  if (!events) {
    return res.status(400).json({ error: "Missing 'events' in body" });
  }

  let options = {
    pythonPath: "C:/Users/kall/Desktop/sami/customer-journey-mapping-system/.venv/Scripts/python.exe",
    args: [events]
  };

  PythonShell.run("predict.py", options).then(results => {
    const stage = results[0];
    res.json({ predictedStage: stage });
  }).catch(err => {
    console.error("Prediction error:", err);
    res.status(500).json({ error: "Prediction failed" });
  });
});

module.exports = router;
