
import streamlit as st
from textwrap import shorten
import re
from datetime import date

st.set_page_config(page_title="Easy Apply Copilot – Pallavi", page_icon="✅", layout="wide")

# ------------------ Utilities ------------------
KEYWORDS_DE = {
    "data engineer","data engineering","etl","elt","pipeline","pipelines","airflow","composer",
    "gcp","google cloud","bigquery","dataflow","pub/sub","pubsub","cloud run","cloud functions",
    "dbt","spark","kafka","terraform","orchestration","warehouse","lakehouse","modeling","partition","clustering"
}

KEYWORDS_BA = {
    "business analyst","product analyst","ba","stakeholder","requirements","user stories","acceptance criteria",
    "uat","jira","confluence","tableau","power bi","sql","excel","process","workflow","dashboard","kpi","insights"
}

def clean(text:str)->str:
    return re.sub(r'\s+',' ',text).strip().lower()

def score(text:str, vocab:set)->int:
    t = " " + clean(text) + " "
    return sum(1 for w in vocab if f" {w} " in t)

def classify_role(jd:str)->str:
    s_de = score(jd, KEYWORDS_DE)
    s_ba = score(jd, KEYWORDS_BA)
    if s_de > s_ba: return "DE"
    if s_ba > s_de: return "BA"
    return "BA" if any(w in jd.lower() for w in ["requirement","dashboard","stakeholder"]) else "DE"

def extract_company_role(jd:str):
    company = None
    role = None
    m = re.search(r"(data engineer|business analyst|product analyst|cloud data engineer)", jd, re.I)
    if m: role = m.group(1).title()
    m2 = re.search(r"at\s+([A-Z][A-Za-z0-9&\-\.\s]{2,})", jd)
    if m2:
        company = m2.group(1).strip().rstrip(".")
    return company, role

def top_keywords(jd:str, role:str, n:int=6):
    # simple frequency-based highlight from predefined sets
    words = re.findall(r"[a-zA-Z][a-zA-Z\-\+/\.]{2,}", jd.lower())
    freq = {}
    pool = KEYWORDS_DE if role=="DE" else KEYWORDS_BA
    for w in words:
        if w in pool:
            freq[w] = freq.get(w,0)+1
    ordered = sorted(freq.items(), key=lambda x: (-x[1], x[0]))
    return [k for k,_ in ordered[:n]]

def make_summary(role:str, kws:list)->str:
    if role=="DE":
        base = ("Cloud-focused Data Engineer with hands-on GCP experience (BigQuery, Cloud Storage, Cloud Functions/Run) "
                "building reliable ETL/ELT pipelines and analytics layers. I optimize cost and performance with partitioning/clustering, "
                "and deliver production-ready data assets for BI/ML. Comfort with {}.").format(", ".join(kws[:3]) if kws else "SQL and orchestration")
    else:
        base = ("Business Analyst skilled in stakeholder communication, requirements via interviews/workshops, and data-backed decisions. "
                "Advanced in SQL, Excel, and dashboards (Tableau/Looker Studio); experienced with user stories, acceptance criteria, and UAT. "
                "Familiar with {}.").format(", ".join(kws[:3]) if kws else "JIRA/Confluence")
    return base

def make_bullets(role:str, kws:list)->list:
    if role=="DE":
        base = [
            "Built and maintained GCP-based pipelines (BigQuery + Cloud Storage + Cloud Functions/Run) for automated ingestion and transformation.",
            "Improved query performance and reduced costs via partitioning, clustering, and SQL tuning in BigQuery.",
            "Delivered validated, analytics-ready tables to BI tools (Tableau/Looker Studio) with robust data quality checks.",
            "Containerized micro-tasks and adopted Git-based workflows to ensure reliable, repeatable deployments.",
            "Collaborated with stakeholders to define SLAs and monitoring, aligning pipelines with reporting/ML needs."
        ]
    else:
        base = [
            "Captured requirements through interviews/workshops; translated them into clear user stories and acceptance criteria.",
            "Analyzed data with SQL/Excel to validate assumptions and provide actionable insights and KPIs.",
            "Built Tableau/Looker Studio dashboards to communicate trends and support stakeholder decisions.",
            "Coordinated UAT: wrote test cases, triaged issues, and drove sign-off with cross-functional teams.",
            "Maintained transparent tracking in JIRA/Confluence and presented updates to non-technical audiences."
        ]
    if kws:
        base[-1] += f" (Keywords: {', '.join(kws[:4])})."
    return base

def make_fit_blurb(role:str, kws:list)->str:
    if role=="DE":
        text = "GCP data engineer—BigQuery pipelines, cost/perf tuning, and automated ELT. Ready to deliver analytics-ready tables fast."
    else:
        text = "BA with strong stakeholder comms, SQL/Tableau, user stories & UAT. I translate needs into clear, testable outcomes."
    return shorten(text, width=200, placeholder="…")

def make_cover_letter(company:str, role_title:str, role:str, kws:list, contact:dict)->str:
    company = company or "[Company]"
    role_title = role_title or ("Data Engineer" if role=="DE" else "Business Analyst")
    opening = f"Dear Hiring Team at {company},"
    para1 = (f"I’m excited to apply for the {role_title} role. With a background spanning "
             f"{'cloud-native data engineering on GCP (BigQuery, Cloud Storage, Cloud Functions/Run)' if role=='DE' else 'stakeholder-facing analysis, SQL, and dashboarding (Tableau/Looker Studio)'},"
             " I deliver reliable, actionable outcomes that teams can trust.")
    if role=="DE":
        para2 = ("At MTSU and Innova Solutions, I built automated ELT to BigQuery, implemented partitioning/clustering to cut costs, "
                 "and shipped analytics-ready datasets powering BI and ML use cases. I’m comfortable with production hygiene—version control, checks, and monitoring.")
    else:
        para2 = ("In recent projects, I captured requirements via interviews/workshops, translated them into user stories and acceptance criteria, "
                 "validated data with SQL/Excel, and delivered dashboards that supported decision-making. I also coordinated UAT and presented insights to non-technical stakeholders.")
    para3 = (f"I’d welcome the chance to discuss how I can contribute to your roadmap. "
             f"Thank you for your time and consideration.\n\nSincerely,\n{contact.get('name','Pallavi Suram')}\n"
             f"{contact.get('location','Murfreesboro, TN')}\n{contact.get('email','')}\n{contact.get('phone','')}")
    return "\n\n".join([opening, para1, para2, para3])

# ------------------ UI ------------------
st.title("Easy Apply Copilot — Manual, Fast & ATS-Friendly")

with st.sidebar:
    st.header("Your Details")
    name = st.text_input("Name", value="Pallavi Suram")
    email = st.text_input("Email", value="surampallavigayathri0508@gmail.com")
    phone = st.text_input("Phone", value="(615) 938-2740")
    location = st.text_input("Location", value="Murfreesboro, TN")
    st.caption("These appear in your cover letter.")

st.markdown("Paste a job description below. The Copilot will classify the role, highlight keywords, and generate tailored text to paste into LinkedIn’s Easy Apply fields.")

jd = st.text_area("Job Description", height=300, placeholder="Paste the full job description here...")

colA, colB = st.columns(2)
with colA:
    if st.button("Analyze & Generate", type="primary", use_container_width=True):
        if not jd.strip():
            st.error("Please paste a job description first.")
        else:
            role = classify_role(jd)
            company, role_title = extract_company_role(jd)
            kws = top_keywords(jd, role, n=6)
            st.session_state["analysis"] = {
                "role": role,
                "company": company,
                "role_title": role_title,
                "kws": kws
            }

with colB:
    st.info("Tip: Keep this fully manual to comply with LinkedIn’s rules. No bots, no auto-submission—just copy & paste.")

if "analysis" in st.session_state:
    data = st.session_state["analysis"]
    role = data["role"]
    company = data["company"]
    role_title = data["role_title"]
    kws = data["kws"]

    st.subheader("Recommended Resume")
    st.write(f"**Use:** {'Business Analyst' if role=='BA' else 'Data Engineer'} resume")
    st.caption("You can still swap if you prefer — this is based on keywords in the JD.")

    st.subheader("Top Matched Keywords")
    if kws:
        st.write(", ".join(kws))
    else:
        st.write("No strong matches — the JD might be very generic.")

    st.subheader("3‑Sentence Summary")
    summary = make_summary(role, kws)
    st.text_area("Summary", value=summary, height=120)

    st.subheader("Five Bullets to Paste")
    bullets = make_bullets(role, kws)
    st.text_area("Bullets", value="\n".join([f"• {b}" for b in bullets]), height=160)

    st.subheader("≤200‑Character ‘Why I’m a Fit’")
    fit = make_fit_blurb(role, kws)
    st.text_input("Fit blurb", value=fit)

    st.subheader("Short Cover Letter")
    contact = {"name": name, "email": email, "phone": phone, "location": location}
    cover = make_cover_letter(company, role_title, role, kws, contact)
    st.text_area("Cover letter", value=cover, height=240)

    # Quick Answers bank
    st.subheader("Quick Answers (Optional)")
    col1, col2 = st.columns(2)
    with col1:
        work_auth = st.text_input("Work authorization", value="F-1 student; currently on CPT. Eligible for OPT starting Dec 2025.")
        sponsorship = st.text_input("Sponsorship", value="Will require visa sponsorship for long-term employment.")
        relocate = st.text_input("Relocation", value="Open to relocation or remote.")
    with col2:
        start_date = st.text_input("Earliest start date", value="Two weeks’ notice (or per OPT start date).")
        salary = st.text_input("Salary expectation (optional)", value="Negotiable based on role and location.")
        travel = st.text_input("Travel availability (optional)", value="Up to 10–20% as needed.")

    qa_block = f"""Quick Answers:
- Work authorization: {work_auth}
- Sponsorship: {sponsorship}
- Relocation: {relocate}
- Earliest start date: {start_date}
- Salary: {salary}
- Travel: {travel}
"""

    st.text_area("Copy block", value=qa_block, height=140)

    # Download outputs as a single .txt
    full_text = f"""== Suggested Resume ==
{'Business Analyst' if role=='BA' else 'Data Engineer'}

== Top Keywords ==
{", ".join(kws) if kws else "None detected"}

== Summary ==
{summary}

== Bullets ==
{chr(10).join([f"- {b}" for b in bullets])}

== 200-char Fit ==
{fit}

== Cover Letter ==
{cover}

== Quick Answers ==
{qa_block}
Generated on {date.today().isoformat()}
"""
    st.download_button("Download All Outputs (.txt)", data=full_text, file_name="easy_apply_outputs.txt", mime="text/plain")
else:
    st.caption("Paste a job description and click ‘Analyze & Generate’ to get started.")
