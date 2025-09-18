import React, { useState, useEffect, useRef } from "react";
import "./style.css";
import Chart from "chart.js/auto";

export default function App() {
  const [globalData, setGlobalData] = useState(null);
  const [skillChart, setSkillChart] = useState(null);
  const chartRef = useRef(null);
  const [uploadMessage, setUploadMessage] = useState("");

  // =============================
  // 🚀 Upload CSV Handler
  // =============================
  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setUploadMessage("⏳ Uploading...");

    try {
      const res = await fetch("http://localhost:8000/upload_csv", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();

      if (res.ok) {
        setUploadMessage(`✅ Dataset uploaded successfully! Candidates reloaded: ${data.rows}`);
      } else {
        setUploadMessage(`❌ ${data.message}`);
      }
    } catch (err) {
      setUploadMessage("❌ Error uploading dataset: " + err);
    }
  };

  // =============================
  // 🚀 Fetch Recommendations
  // =============================
  const runRecommendation = async () => {
    const desc = document.getElementById("jobdesc").value;
    const budget = parseFloat(document.getElementById("budget").value || "0");
    const budget_type = document.getElementById("budget_type").value;
    const locations = document
      .getElementById("locations")
      .value.split(",")
      .map((s) => s.trim())
      .filter(Boolean);

    const payload = {
      title: "Ad-hoc Job",
      description: desc,
      budget_type: budget_type,
      budget_value: budget,
      preferred_locations: locations,
      remote_allowed: true,
      preferred_gender: document.getElementById("gender").value || null,
    };

    try {
      const res = await fetch("http://localhost:8000/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      setGlobalData(data);
      renderCharts(data.candidates);
    } catch (err) {
      alert("Error connecting to backend: " + err);
    }
  };

  // =============================
  // 📊 Render Charts
  // =============================
  const renderCharts = (candidates) => {
    const skillCounts = {};
    candidates.forEach((c) => {
      if (c.skills) {
        c.skills.split(",").forEach((s) => {
          const skill = s.trim().toLowerCase();
          if (skill) skillCounts[skill] = (skillCounts[skill] || 0) + 1;
        });
      }
    });

    const labels = Object.keys(skillCounts);
    const values = Object.values(skillCounts);

    if (skillChart) {
      skillChart.destroy();
    }

    const newChart = new Chart(chartRef.current, {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "Skills Count",
            data: values,
            backgroundColor: "rgba(54, 162, 235, 0.6)",
          },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
      },
    });

    setSkillChart(newChart);

    // =============================
    // 📝 Dynamic Explanation
    // =============================
    const explanationBox = document.getElementById("chartExplanation");
    if (labels.length === 0) {
      explanationBox.innerHTML = "⚠️ No skill data available.";
      return;
    }

    const maxVal = Math.max(...values);
    const minVal = Math.min(...values);
    const topSkills = labels.filter((s, i) => values[i] === maxVal);
    const rareSkills = labels.filter((s, i) => values[i] === minVal);

    let explanation = "";

    if (topSkills.length === 1) {
      explanation = `📌 The most common skill is <b>${topSkills[0]}</b>, 
      appearing ${maxVal} times among candidates.`;
    } else {
      explanation = `📌 Multiple top skills stand out: <b>${topSkills.join(", ")}</b>, 
      each with ${maxVal} candidates.`;
    }

    if (rareSkills.length > 0 && rareSkills.length < labels.length) {
      explanation += ` On the other hand, <b>${rareSkills.join(", ")}</b> 
      are the least common skills, appearing only ${minVal} times.`;
    }

    if (labels.length > 5) {
      explanation += ` 🎯 Overall, there’s a diverse skill set covering ${labels.length} unique skills.`;
    } else {
      explanation += ` 👥 The candidate pool is focused on a smaller set of ${labels.length} skills.`;
    }

    explanationBox.innerHTML = explanation;
  };

  // =============================
  // 🏆 Render Candidates
  // =============================
  const renderCandidates = (candidates) => {
    return candidates.map((c, i) => {
      let badge = "";
      if (i === 0) badge = "🥇";
      else if (i === 1) badge = "🥈";
      else if (i === 2) badge = "🥉";

      const skills = c.skills
        ? c.skills
            .split(",")
            .map((s, i) => (
              <span key={i} className="tag">
                {s.trim()}
              </span>
            ))
        : "Not listed";

      return (
        <div key={i} className="card fade-in">
          <div className="card-header">
            <img
              src={`https://ui-avatars.com/api/?name=${encodeURIComponent(c.name)}`}
              className="avatar"
              alt="avatar"
            />
            <h3>
              {badge} {c.name} {c.gender ? `(${c.gender})` : ""}
            </h3>
            <span className="score">⭐ {c.score.toFixed(2)}</span>
          </div>
          <p>
            <b>Location:</b> {c.location || "N/A"}
          </p>
          <p>
            <b>Short Bio:</b> {c.bio ? c.bio.substring(0, 150) + "..." : "No bio"}
          </p>
          <p>
            <b>Job Types:</b> {c.job_types || "N/A"}
          </p>
          <p>
            <b>Skills:</b> {skills}
          </p>
          <p>
            <b>Software:</b> {c.software || "N/A"}
          </p>
          <p>
            <b>Platforms:</b> {c.platforms || "N/A"}
          </p>
          <p>
            <b>Content Verticals:</b> {c.content_verticals || "N/A"}
          </p>
          <p>
            <b>Past Creators:</b> {c.past_creators || "N/A"}
          </p>
          <div className="rates">
            <span>
              <b>Monthly:</b> {c.monthly_rate || "N/A"}
            </span>
            <span>
              <b>Hourly:</b> {c.hourly_rate || "N/A"}
            </span>
          </div>
          <p>
            <b>Profile Views:</b> {c.views}
          </p>
        </div>
      );
    });
  };

  // =============================
  // Sorting + Filtering + Download
  // =============================
  const handleSort = (e) => {
    if (!globalData) return;
    const sortBy = e.target.value;
    const sorted = [...globalData.candidates].sort((a, b) => b[sortBy] - a[sortBy]);
    setGlobalData({ ...globalData, candidates: sorted });
  };

  const handleFilter = (e) => {
    if (!globalData) return;
    const term = e.target.value.toLowerCase();
    const filtered = globalData.candidates.filter((c) =>
      c.skills.toLowerCase().includes(term)
    );
    setGlobalData({ ...globalData, candidates: filtered });
  };

  const handleDownload = () => {
    if (!globalData) return;
    const rows = [
      ["Name", "Gender", "Location", "Skills", "Score", "Monthly Rate", "Hourly Rate", "Views"],
      ...globalData.candidates.map((c) => [
        c.name,
        c.gender,
        c.location,
        c.skills,
        c.score,
        c.monthly_rate,
        c.hourly_rate,
        c.views,
      ]),
    ];
    const csv = rows.map((r) => r.join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "top_candidates.csv";
    a.click();
  };

  return (
    <div className="layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <h2>TalentRecs</h2>
        </div>
        <nav className="sidebar-nav">
          <a href="#jobs" className="nav-link active">
            <span className="icon">📋</span>
            <span className="text">Job Post</span>
          </a>
          <a href="#candidates" className="nav-link">
            <span className="icon">🏆</span>
            <span className="text">Candidates</span>
          </a>
          <a href="#analytics" className="nav-link">
            <span className="icon">📊</span>
            <span className="text">Analytics</span>
          </a>
          <a href="#about" className="nav-link">
            <span className="icon">ℹ️</span>
            <span className="text">About</span>
          </a>
        </nav>
        <div className="sidebar-footer">
          <p>© 2025 TalentRecs</p>
        </div>
      </aside>

      {/* Main Content */}
      <main className="content">
        {/* Job Info + Upload */}
        <section id="jobs" className="section">
          <h1>🎯 Talent Recommender System</h1>
          <div className="job-grid">
            {/* Job Info */}
            <div className="job-form card">
              <h3>Job Info</h3>
              <textarea id="jobdesc" placeholder="Enter job description or required skills"></textarea>

              <div className="form-row">
                <input type="number" id="budget" placeholder="Budget value" />
                <select id="budget_type">
                  <option value="monthly">Monthly</option>
                  <option value="hourly">Hourly</option>
                </select>
              </div>

              <div className="form-row">
                <label htmlFor="gender">Preferred Gender:</label>
                <select id="gender">
                  <option value="">Any</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <input
                type="text"
                id="locations"
                placeholder="Preferred locations (comma separated)"
              />
            </div>

            {/* CSV Upload */}
            <div className="job-form card">
              <h3>Upload Candidate Dataset</h3>
              <div className="form-row">
                <label htmlFor="datasetUpload">Upload CSV:</label>
                <input type="file" id="datasetUpload" accept=".csv" onChange={handleUpload} />
              </div>
              <div id="uploadMessage" style={{ marginTop: "5px", fontSize: "14px" }}>
                {uploadMessage}
              </div>
              <button id="run" onClick={runRecommendation}>
                🚀 Get Top 10 Candidates
              </button>
            </div>
          </div>
        </section>

        {/* Candidates */}
        <section id="candidates" className="section">
          <h2>🏆 Top 10 Candidates</h2>
          <div className="job-form card">
            <div className="filters">
              <select id="sort" onChange={handleSort}>
                <option value="score">Sort by Score</option>
                <option value="views">Sort by Views</option>
              </select>
              <input type="text" id="filterSkill" placeholder="Filter by skill" onInput={handleFilter} />
              <button id="download" onClick={handleDownload}>
                ⬇️ Download CSV
              </button>
            </div>
            <div id="results" className="results">
              {globalData && renderCandidates(globalData.candidates)}
            </div>
          </div>
        </section>

        {/* Analytics */}
        <section id="analytics" className="section">
          <h2>📊 Analytics Dashboard</h2>
          <div className="job-form card">
            <canvas ref={chartRef} id="chartSkills"></canvas>
            <div id="chartExplanation" className="explanation"></div>
          </div>
        </section>

        {/* About */}
        <section id="about" className="section">
          <div className="job-form card">
            <h2>ℹ️ About</h2>
            <p>
              This AI-powered Talent Recommender helps recruiters find the best-fit creators
              based on skills, bio, budget, and popularity. Designed for a professional,
              data-driven recruitment workflow.
            </p>
          </div>
        </section>
      </main>
    </div>
  );
}
