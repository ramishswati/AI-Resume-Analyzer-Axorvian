import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import pdfplumber
import json
import re
from datetime import datetime

load_dotenv()

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { box-sizing: border-box; font-family: 'Inter', sans-serif; }
html, body, [data-testid="stAppViewContainer"] { background: #f8fafc !important; }
#MainMenu, footer, header, [data-testid="stToolbar"], .stDeployButton { display: none !important; }

[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
}
[data-testid="stSidebar"] > div { padding: 1.5rem 1.25rem !important; }

.brand {
    display: flex; align-items: center; gap: 10px;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid #f1f5f9;
    margin-bottom: 1.5rem;
}
.brand-icon {
    width: 40px; height: 40px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 10px; display: flex; align-items: center;
    justify-content: center; font-size: 1.2rem;
}
.brand-name { font-size: 1rem; font-weight: 700; color: #0f172a; }
.brand-sub { font-size: 0.68rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }

.sec-label {
    font-size: 0.68rem; font-weight: 600; color: #94a3b8;
    text-transform: uppercase; letter-spacing: 1px;
    margin: 1.25rem 0 0.5rem 0;
}

.top-bar {
    background: #fff; border-bottom: 1px solid #e2e8f0;
    padding: 1rem 2rem;
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 1.5rem;
}
.top-title { font-size: 1rem; font-weight: 700; color: #0f172a; }
.top-sub { font-size: 0.75rem; color: #94a3b8; }
.badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: #f0fdf4; border: 1px solid #bbf7d0;
    border-radius: 20px; padding: 3px 10px;
    font-size: 0.7rem; color: #15803d; font-weight: 500;
}
.badge-dot { width: 6px; height: 6px; border-radius: 50%; background: #22c55e; animation: blink 2s infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }

/* Score card */
.score-card {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 16px; padding: 1.5rem; text-align: center;
    color: white; margin-bottom: 1rem;
    box-shadow: 0 4px 20px rgba(99,102,241,0.3);
}
.score-number { font-size: 3.5rem; font-weight: 800; line-height: 1; }
.score-label { font-size: 0.85rem; opacity: 0.85; margin-top: 0.25rem; }
.score-sub { font-size: 0.75rem; opacity: 0.7; margin-top: 0.15rem; }

/* Info cards */
.info-card {
    background: #fff; border: 1px solid #e2e8f0;
    border-radius: 12px; padding: 1rem 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,.04);
}
.card-title {
    font-size: 0.78rem; font-weight: 700; color: #6366f1;
    text-transform: uppercase; letter-spacing: 0.5px;
    margin-bottom: 0.75rem; display: flex; align-items: center; gap: 6px;
}

/* Skills */
.skill-wrap { display: flex; flex-wrap: wrap; gap: 6px; }
.skill-tag {
    padding: 3px 10px; border-radius: 20px;
    font-size: 0.75rem; font-weight: 500;
}
.skill-match { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
.skill-missing { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }
.skill-extra { background: #eff6ff; color: #2563eb; border: 1px solid #bfdbfe; }

/* Section divider */
.divider { border: none; border-top: 1px solid #e2e8f0; margin: 1rem 0; }

/* Steps */
.step-card {
    background: #fafafa; border: 1px solid #e2e8f0;
    border-left: 3px solid #6366f1;
    border-radius: 8px; padding: 0.75rem 1rem;
    margin-bottom: 0.6rem; font-size: 0.82rem; color: #374151; line-height: 1.5;
}

/* Upload area */
[data-testid="stFileUploader"] {
    background: #fff !important;
    border: 2px dashed #c7d2fe !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}
[data-testid="stFileUploader"]:hover { border-color: #6366f1 !important; }

/* Text area */
.stTextArea textarea {
    background: #fff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    font-size: 0.85rem !important;
    color: #1e293b !important;
}
.stTextArea textarea:focus { border-color: #6366f1 !important; box-shadow: 0 0 0 3px rgba(99,102,241,.1) !important; }

/* Button */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; font-weight: 600 !important;
    font-size: 0.85rem !important; width: 100% !important;
    padding: 0.6rem !important; transition: all .2s !important;
}
.stButton > button:hover { opacity: .9 !important; transform: translateY(-1px) !important; }

.stTextInput input {
    background: #fff !important; border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important; color: #1e293b !important;
}
.stTextInput input:focus { border-color: #6366f1 !important; }

label { color: #64748b !important; font-size: 0.8rem !important; font-weight: 500 !important; }

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 3px; }

.empty-state {
    text-align: center; padding: 3rem 1rem; color: #94a3b8;
}
.empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-title { font-size: 1.1rem; font-weight: 600; color: #475569; margin-bottom: 0.5rem; }
.empty-text { font-size: 0.82rem; line-height: 1.6; }

.progress-bar-wrap {
    background: #e2e8f0; border-radius: 10px;
    height: 8px; margin: 0.5rem 0 1rem 0; overflow: hidden;
}
.progress-bar-fill {
    height: 100%; border-radius: 10px;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    transition: width 0.5s ease;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────
for k, v in [("result", None), ("resume_text", ""), ("analyzed", False)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helpers ────────────────────────────────────────────
def extract_pdf_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text.strip()

def analyze_with_gemini(api_key, resume_text, job_desc):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
You are an expert HR recruiter and resume analyst. Analyze the resume against the job description and return a JSON object ONLY — no markdown, no explanation.

Resume:
{resume_text}

Job Description:
{job_desc}

Return this exact JSON structure:
{{
  "match_score": <integer 0-100>,
  "candidate_name": "<name or Unknown>",
  "candidate_email": "<email or Not found>",
  "candidate_phone": "<phone or Not found>",
  "candidate_location": "<location or Not found>",
  "total_experience": "<e.g. 2 years or Fresher>",
  "education": "<highest degree>",
  "matched_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "extra_skills": ["skill1", "skill2"],
  "strengths": ["strength1", "strength2", "strength3"],
  "weaknesses": ["weakness1", "weakness2"],
  "suggestions": ["suggestion1", "suggestion2", "suggestion3", "suggestion4"],
  "overall_verdict": "<Excellent Match / Good Match / Average Match / Poor Match>",
  "verdict_reason": "<1-2 sentence explanation>"
}}
"""
    response = model.generate_content(prompt)
    raw = response.text.strip()
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)

# ── Sidebar ────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="brand">
      <div class="brand-icon">📄</div>
      <div>
        <div class="brand-name">ResumeAI</div>
        <div class="brand-sub">Axorvian · Task 3</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec-label">API Configuration</div>', unsafe_allow_html=True)
    api_key = st.text_input("Gemini API Key", type="password", placeholder="AIza...", label_visibility="collapsed")

    st.markdown('<div class="sec-label">Upload Resume</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed")

    if uploaded_file:
        st.markdown(f"""
        <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:0.6rem 0.8rem;font-size:0.78rem;color:#15803d;margin-top:0.5rem;">
        ✅ {uploaded_file.name}
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="sec-label" style="margin-top:1rem">How to Use</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.78rem;color:#94a3b8;line-height:1.7;">
    1️⃣ Paste your Gemini API key<br>
    2️⃣ Upload your resume (PDF)<br>
    3️⃣ Enter the Job Description<br>
    4️⃣ Click Analyze Resume<br>
    5️⃣ View your match score & suggestions
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.analyzed:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Analyze New Resume"):
            st.session_state.result = None
            st.session_state.resume_text = ""
            st.session_state.analyzed = False
            st.rerun()

# ── Top Bar ────────────────────────────────────────────
st.markdown("""
<div class="top-bar">
  <div>
    <div class="top-title">📄 ResumeAI — AI Resume Analyzer</div>
    <div class="top-sub">Powered by Google Gemini · Axorvian Internship Task 3</div>
  </div>
  <div class="badge"><div class="badge-dot"></div>Gemini 2.5 Flash · Ready</div>
</div>
""", unsafe_allow_html=True)

# ── Main Content ───────────────────────────────────────
if not st.session_state.analyzed:
    # Input form
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("#### 📋 Job Description")
        job_desc = st.text_area(
            "Job Description",
            height=320,
            placeholder="Paste the job description here...\n\nExample:\nWe are looking for a Python Developer with experience in Machine Learning, TensorFlow, and REST APIs...",
            label_visibility="collapsed"
        )

    with col2:
        st.markdown("#### 👤 Resume Preview")
        if uploaded_file:
            try:
                text = extract_pdf_text(uploaded_file)
                st.session_state.resume_text = text
                st.markdown(f"""
                <div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;
                padding:1rem;height:300px;overflow-y:auto;font-size:0.78rem;
                color:#374151;line-height:1.6;white-space:pre-wrap;">{text[:1500]}{'...' if len(text)>1500 else ''}</div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Could not read PDF: {e}")
        else:
            st.markdown("""
            <div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;
            padding:2rem;height:300px;display:flex;align-items:center;justify-content:center;
            text-align:center;color:#94a3b8;font-size:0.85rem;">
            📄 Upload a PDF resume from the sidebar to preview it here
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])
    with col_btn2:
        analyze_btn = st.button("🔍 Analyze Resume")

    if analyze_btn:
        if not api_key:
            st.warning("⚠️ Please enter your Gemini API Key in the sidebar.")
        elif not uploaded_file:
            st.warning("⚠️ Please upload a PDF resume from the sidebar.")
        elif not job_desc.strip():
            st.warning("⚠️ Please enter the Job Description.")
        else:
            with st.spinner("🤖 AI is analyzing your resume..."):
                try:
                    result = analyze_with_gemini(api_key, st.session_state.resume_text, job_desc)
                    st.session_state.result = result
                    st.session_state.analyzed = True
                    st.rerun()
                except json.JSONDecodeError:
                    st.error("❌ Could not parse AI response. Please try again.")
                except Exception as e:
                    err = str(e)
                    if "429" in err:
                        st.error("⚠️ API quota exceeded. Please use a different API key.")
                    else:
                        st.error(f"❌ Error: {err}")

else:
    # ── Results ────────────────────────────────────────
    r = st.session_state.result
    score = r.get("match_score", 0)

    # Score color
    if score >= 75:
        verdict_color = "#15803d"
        verdict_bg = "#f0fdf4"
        verdict_border = "#bbf7d0"
    elif score >= 50:
        verdict_color = "#d97706"
        verdict_bg = "#fffbeb"
        verdict_border = "#fde68a"
    else:
        verdict_color = "#dc2626"
        verdict_bg = "#fef2f2"
        verdict_border = "#fecaca"

    # Row 1 — Score + Candidate Info
    col1, col2 = st.columns([1, 2], gap="large")

    with col1:
        st.markdown(f"""
        <div class="score-card">
            <div class="score-number">{score}%</div>
            <div class="score-label">Resume Match Score</div>
            <div class="score-sub">{r.get('overall_verdict', '')}</div>
        </div>
        <div style="background:{verdict_bg};border:1px solid {verdict_border};
        border-radius:10px;padding:0.75rem 1rem;font-size:0.8rem;color:{verdict_color};line-height:1.5;">
        {r.get('verdict_reason', '')}
        </div>
        """, unsafe_allow_html=True)

        # Progress bar
        st.markdown(f"""
        <div style="margin-top:1rem;">
        <div style="font-size:0.75rem;color:#64748b;margin-bottom:4px;">Match Progress</div>
        <div class="progress-bar-wrap">
            <div class="progress-bar-fill" style="width:{score}%"></div>
        </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""<div class="info-card">
        <div class="card-title">👤 Candidate Information</div>""", unsafe_allow_html=True)

        info_rows = [
            ("Name", r.get("candidate_name", "—")),
            ("Email", r.get("candidate_email", "—")),
            ("Phone", r.get("candidate_phone", "—")),
            ("Location", r.get("candidate_location", "—")),
            ("Experience", r.get("total_experience", "—")),
            ("Education", r.get("education", "—")),
        ]
        for label, value in info_rows:
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
            padding:0.45rem 0;border-bottom:1px solid #f1f5f9;font-size:0.82rem;">
                <span style="color:#64748b;font-weight:500;">{label}</span>
                <span style="color:#0f172a;font-weight:500;">{value}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 2 — Skills
    col3, col4, col5 = st.columns(3, gap="medium")

    with col3:
        matched = r.get("matched_skills", [])
        st.markdown(f"""<div class="info-card">
        <div class="card-title">✅ Matched Skills ({len(matched)})</div>
        <div class="skill-wrap">
        {"".join(f'<span class="skill-tag skill-match">{s}</span>' for s in matched) or '<span style="font-size:0.8rem;color:#94a3b8;">None found</span>'}
        </div></div>""", unsafe_allow_html=True)

    with col4:
        missing = r.get("missing_skills", [])
        st.markdown(f"""<div class="info-card">
        <div class="card-title">❌ Missing Skills ({len(missing)})</div>
        <div class="skill-wrap">
        {"".join(f'<span class="skill-tag skill-missing">{s}</span>' for s in missing) or '<span style="font-size:0.8rem;color:#94a3b8;">None missing</span>'}
        </div></div>""", unsafe_allow_html=True)

    with col5:
        extra = r.get("extra_skills", [])
        st.markdown(f"""<div class="info-card">
        <div class="card-title">⭐ Additional Skills ({len(extra)})</div>
        <div class="skill-wrap">
        {"".join(f'<span class="skill-tag skill-extra">{s}</span>' for s in extra) or '<span style="font-size:0.8rem;color:#94a3b8;">None</span>'}
        </div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 3 — Strengths, Weaknesses, Suggestions
    col6, col7, col8 = st.columns(3, gap="medium")

    with col6:
        st.markdown("""<div class="info-card">
        <div class="card-title">💪 Strengths</div>""", unsafe_allow_html=True)
        for s in r.get("strengths", []):
            st.markdown(f'<div class="step-card">✅ {s}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col7:
        st.markdown("""<div class="info-card">
        <div class="card-title">⚠️ Weaknesses</div>""", unsafe_allow_html=True)
        for w in r.get("weaknesses", []):
            st.markdown(f'<div class="step-card" style="border-left-color:#ef4444;">⚠️ {w}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col8:
        st.markdown("""<div class="info-card">
        <div class="card-title">💡 AI Suggestions</div>""", unsafe_allow_html=True)
        for i, s in enumerate(r.get("suggestions", []), 1):
            st.markdown(f'<div class="step-card" style="border-left-color:#f59e0b;">{i}. {s}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align:center;padding:1rem;font-size:0.72rem;color:#94a3b8;">
    Analysis generated at {datetime.now().strftime("%I:%M %p, %B %d %Y")} · Powered by Google Gemini 2.5 Flash · Axorvian Internship Task 3
    </div>
    """, unsafe_allow_html=True)