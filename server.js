// -------------------- Imports --------------------
import express from 'express';
import 'dotenv/config';
import Groq from 'groq-sdk';
import fs from 'fs';
import Papa from 'papaparse';
import multer from 'multer';

// -------------------- App Setup --------------------
const app = express();
const port = 3000;

// Initialize Groq AI client
const groq = new Groq({ apikey: process.env.GROQ_API_KEY });

// Ensure uploads folder exists
if (!fs.existsSync('uploads')) fs.mkdirSync('uploads');

// -------------------- File Upload Config --------------------
const upload = multer({ dest: 'uploads/' });

// -------------------- CSV Loader --------------------
function loadDataset(filePath) {
  const file = fs.readFileSync(filePath, "utf8");
  return Papa.parse(file, { header: true }).data;
}

// -------------------- Negative Sentiment Analysis --------------------
function analyzeNegativeSentiment(data) {
  const filtered = data.filter(row => row.sentiment?.toLowerCase() === "negative");

  const featureCounts = {};
  filtered.forEach(row => {
    const feat = row.feature || "unknown";
    featureCounts[feat] = (featureCounts[feat] || 0) + 1;
  });

  const COST_PER_ISSUE = 5000;
  const costByFeature = {};
  Object.entries(featureCounts).forEach(([feat, count]) => {
    costByFeature[feat] = count * COST_PER_ISSUE;
  });

  return {
    total_negative: filtered.length,
    feature_breakdown: featureCounts,
    cost_by_feature: costByFeature,
    cost_estimate: filtered.length * COST_PER_ISSUE
  };
}

// -------------------- API Endpoint --------------------
app.post('/analyze', upload.single('csvFile'), async (req, res) => {
  try {
    const filePath = req.file.path;
    const data = loadDataset(filePath);

    const analysis = analyzeNegativeSentiment(data);

    // Call Groq AI for pointwise strategy
    const completion= await groq.chat.completions.create({
        messages: [{
            role: 'system',
            content:`You are an AI marketing & operation strategist for Tata Motors.
            Based on the Negative feedback data i provide , generate actionable strategies
            to reduce complaints, improve sales, and plan marketing campaigns.
            Present your suggestions as numbered points, each starting with a number`
    }, {
        role: 'user',content: JSON.stringify(analysis)}
    ],
    model :'llama-3.3-70b-versatile'
    });
   

    // Send response to frontend
    res.json({
      analysis,
      ai_strategy: completion.choices[0].message.content
    });

    // Delete uploaded file safely
    try { fs.unlinkSync(filePath); } catch (err) { console.warn("Failed to delete temp file:", err); }

  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Something went wrong' });
  }
});

// -------------------- Serve Frontend --------------------
app.use(express.static('public'));

// -------------------- Start Server --------------------
app.listen(port,() =>{
    console.log(`Server running at http://localhost:${port}`);
})

