TalentRecs 🎯
📌 Overview

TalentRecs is a full-stack job recommendation system.
Backend (FastAPI + Python): Handles CSV upload, candidate ranking, and analytics.
Frontend (React + Vite): Interactive UI to upload jobs/candidates, view scores, and insights.
This project helps recruiters quickly match candidates with jobs using embeddings, cosine similarity, and simple explanations.

✨ Features

📂 Upload CSVs with candidate/job data
✅ Data validation & cleaning
📊 Candidate ranking with explanation
📈 Analytics dashboard (React + Chart.js)
⚡ FastAPI backend + React frontend

🛠 Tech Stack

Backend
Python 3.11+
FastAPI + Uvicorn
Pandas, NumPy
python-multipart (for file upload)

Frontend
React (Vite)
Chart.js (visualizations)
CSS (custom styles)

🚀 Installation
1. Clone the repository
git clone https://github.com/Chirayu98/TalentRecs.git
cd TalentRecs

2. Backend Setup
cd src
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt

Run API:
uvicorn main:app --reload

Backend runs on http://127.0.0.1:8000

3. Frontend Setup
cd talentrecs-frontend
npm install
npm run dev

Frontend runs on http://localhost:3000

▶️ Usage

Upload candidate/job CSV via frontend or API.
Backend processes embeddings → similarity scores.
Frontend displays ranked candidates with explanations & charts.

📂 Folder Structure

TalentRecs/
|
│
├── src/                  # Backend
│   ├── main.py           # FastAPI entry point
│   ├── utils.py          # Helper functions
│   ├── embedding_utils.py# Embedding logic
│   └── ranking.py        # Candidate ranking
│
├── talentrecs-frontend/  # React frontend
│   ├── public/           # index.html, manifest, favicon
│   └── src/              # React components, styles
│
├── requirements.txt
├── package.json
└── README.md


🔮 Future Enhancements

OAuth authentication & roles
Smarter LLM-based explanations
Database integration (Postgres/MongoDB)
Resume parsing

📜 License
This project is licensed under the MIT License.
