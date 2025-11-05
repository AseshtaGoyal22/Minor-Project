# app.py
import streamlit as st
import pandas as pd
import re
import difflib
from typing import List, Dict, Tuple
from database import DatabaseManager
from visualization import Visualization

st.set_page_config(page_title="Career Roadmap (Interactive)", layout="wide")

# -------------------------
# Helpers & DB
# -------------------------
@st.cache_resource
def get_db():
    return DatabaseManager()

db = get_db()

def normalize_text(s: str) -> str:
    if not s:
        return ""
    s = s.lower()
    s = re.sub(r"[^\w, ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def to_token_set(s: str) -> set:
    s = normalize_text(s)
    if not s:
        return set()
    parts = []
    for seg in s.split(","):
        seg = seg.strip()
        if not seg:
            continue
        parts.append(seg)
        for w in seg.split():
            parts.append(w)
    tokens = {p for p in (t.strip() for t in parts) if p}
    return tokens

def fuzzy_match_token(token: str, candidates: List[str], cutoff: float = 0.78) -> bool:
    if not candidates:
        return False
    matches = difflib.get_close_matches(token, candidates, n=1, cutoff=cutoff)
    return len(matches) > 0

# -------------------------
# Scoring logic
# -------------------------
def score_career(career: Dict,
                 user_skill_tokens: set,
                 user_interest_tokens: set,
                 selected_skill_names: List[str],
                 preferred_roles: set,
                 preferred_industries: set,
                 candidates_for_fuzzy: List[str]) -> Tuple[float, Dict]:
    req_tokens = to_token_set(career.get("required_skills", ""))
    title_desc_tokens = to_token_set(career.get("title", "") + " " + career.get("description", ""))

    skill_matches = sorted(list(req_tokens & (user_skill_tokens | set(n.lower() for n in selected_skill_names))))
    interest_matches = sorted(list((title_desc_tokens | req_tokens) & user_interest_tokens))
    role_matches = sorted(list(preferred_roles & to_token_set(career.get("title", ""))))
    industry_matches = sorted(list(preferred_industries & title_desc_tokens))

    fuzzy_matches = []
    for ut in (list(user_skill_tokens | user_interest_tokens)):
        if ut in skill_matches or ut in interest_matches:
            continue
        if fuzzy_match_token(ut, list(req_tokens | title_desc_tokens | set(candidates_for_fuzzy)), cutoff=0.78):
            fuzzy_matches.append(ut)

    w_skill = 3.0
    w_selected_skill = 3.0
    w_interest = 1.5
    w_role = 2.0
    w_industry = 1.5
    w_fuzzy = 0.6

    score = (len(skill_matches) * w_skill) + (len(interest_matches) * w_interest) + \
            (len(role_matches) * w_role) + (len(industry_matches) * w_industry) + \
            (len(fuzzy_matches) * w_fuzzy)

    selected_skill_matches = sorted(list(set([n.lower() for n in selected_skill_names]) & req_tokens))
    score += len(selected_skill_matches) * w_selected_skill

    max_possible = max(1, (len(req_tokens) * w_skill + 4 * w_role + 3 * w_industry + 3 * w_interest))
    percent = min(100.0, (score / max_possible) * 100.0)

    details = {
        "skill_matches": skill_matches,
        "selected_skill_matches": selected_skill_matches,
        "interest_matches": interest_matches,
        "role_matches": role_matches,
        "industry_matches": industry_matches,
        "fuzzy_matches": fuzzy_matches,
        "raw_score": score,
        "max_possible": max_possible
    }
    return percent, details

def recommend_careers_advanced(user_skills_str: str,
                               user_interests_str: str,
                               selected_skill_names: List[str],
                               preferred_roles_str: str,
                               preferred_industries_str: str,
                               top_n: int = 6) -> List[Dict]:
    user_skill_tokens = to_token_set(user_skills_str)
    user_interest_tokens = to_token_set(user_interests_str)
    preferred_roles = to_token_set(preferred_roles_str)
    preferred_industries = to_token_set(preferred_industries_str)

    careers = db.get_career_paths()
    skills_db = db.get_all_skills()
    skill_names_db = [s["name"].lower() for s in skills_db] if skills_db else []
    candidates_for_fuzzy = skill_names_db + [c.get("title","").lower() for c in careers]

    scored = []
    for c in careers:
        pct, details = score_career(c, user_skill_tokens, user_interest_tokens,
                                    selected_skill_names, preferred_roles, preferred_industries,
                                    candidates_for_fuzzy)
        scored.append({
            "id": c["id"],
            "title": c["title"],
            "description": c["description"],
            "duration_weeks": c.get("duration_weeks"),
            "difficulty_level": c.get("difficulty_level"),
            "salary_range": c.get("salary_range"),
            "match_percent": round(pct, 1),
            "details": details,
            "required_skills": c.get("required_skills", "")
        })

    scored.sort(key=lambda x: (-x["match_percent"], x.get("duration_weeks") or 0))
    return scored[:top_n]

# -------------------------
# Sidebar (detailed profile)
# -------------------------
st.sidebar.header("Create / Save profile (detailed)")
with st.sidebar.form("user_form_detailed"):
    name = st.text_input("Name")
    email = st.text_input("Email")
    career_interests = st.text_area("Career interests (comma separated)", help="e.g., data, AI, web")
    all_skills = db.get_all_skills()
    skill_options = [s["name"] for s in all_skills]
    selected_skills = st.multiselect("Select skills you know (from DB)", options=skill_options)
    other_skills = st.text_input("Other skills (comma separated)")
    available_hours = st.selectbox("Available hours per week", ["<5", "5-10", "10-20", "20+"])
    # convert available_hours to numeric weekly_hours for timeline/planning UI
    weekly_hours_map = {"<5": 3, "5-10": 7, "10-20": 12, "20+": 20}
    experience_years = st.slider("Years of experience", min_value=0, max_value=20, value=0)
    education_level = st.selectbox("Education level", ["High School", "Diploma", "Bachelor's", "Master's", "PhD", "Other"])
    preferred_roles = st.text_input("Preferred roles (comma)", help="e.g., backend developer, data engineer")
    preferred_industries = st.text_input("Preferred industries (comma)")
    work_mode = st.selectbox("Preferred work mode", ["Remote", "Hybrid", "On-site", "No preference"])
    projects = st.text_area("Notable projects (short)")
    certifications = st.text_input("Certifications (comma separated)")
    submit_save = st.form_submit_button("Save profile & Recommend")

if submit_save:
    if not name or not email:
        st.sidebar.error("Name and Email are required to save profile.")
    else:
        try:
            db.insert_user(
                name=name.strip(),
                email=email.strip(),
                career_interests=career_interests.strip() or "N/A",
                current_skills=", ".join(selected_skills) + (", " + other_skills.strip() if other_skills.strip() else ""),
                available_hours=available_hours,
                experience_level=str(experience_years),
                additional_info=f"education:{education_level};work_mode:{work_mode};projects:{projects};certs:{certifications}"
            )
            st.sidebar.success("Profile saved.")
            st.session_state["latest_profile"] = {
                "name": name, "email": email, "skills": selected_skills, "other_skills": other_skills,
                "interests": career_interests
            }
        except Exception as e:
            st.sidebar.error(f"Error saving profile: {e}")

# -------------------------
# Main area (live inputs)
# -------------------------
st.title("Personalized Career Roadmap")
st.write("Provide more detail to get better recommendations and interactive charts.")

col_main, col_side = st.columns([3, 1])
with col_main:
    st.header("Your inputs")
    latest = st.session_state.get("latest_profile", None)
    live_selected = st.multiselect("Select your known skills (optional)", options=skill_options, default=(latest["skills"] if latest else []))
    live_other_skills = st.text_input("Other skills (comma separated)", value=(latest["other_skills"] if latest else ""))
    live_interests = st.text_area("Interests (comma separated)", value=(latest["interests"] if latest else ""))
    live_preferred_roles = st.text_input("Preferred roles (comma separated)")
    live_preferred_industries = st.text_input("Preferred industries (comma separated)")
    weekly_hours_control = st.selectbox("How many hours per week can you study?", ["3", "5", "7", "10", "15"], index=2)
    run_reco = st.button("Recommend careers (advanced)")

with col_side:
    st.header("Tips to improve results")
    st.write("- Pick skills from the list so matching is exact.")
    st.write("- Add other skills and project names to help fuzzy matching.")
    st.write("- Add preferred roles/industries to bias results to what you want.")

# -------------------------
# Run recommendation and show results + visuals
# -------------------------
if run_reco:
    combined_skills_str = ", ".join(live_selected) + (", " + live_other_skills if live_other_skills.strip() else "")
    recs = recommend_careers_advanced(combined_skills_str, live_interests, live_selected,
                                     live_preferred_roles, live_preferred_industries, top_n=8)

    if not recs:
        st.info("No careers found in database.")
    else:
        st.header("Top recommended careers")
        skills_db = db.get_all_skills()
        skills_df = pd.DataFrame(skills_db) if skills_db else pd.DataFrame(columns=["id","name","category","estimated_hours"])
        if 'estimated_hours' in skills_df.columns:
            skills_df['estimated_hours'] = pd.to_numeric(skills_df['estimated_hours'], errors='coerce')

        for i, r in enumerate(recs, 1):
            st.subheader(f"{i}. {r['title']}  —  {r['match_percent']}% match")
            st.progress(int(r['match_percent']))
            st.write(f"**Duration:** {r.get('duration_weeks')} weeks • **Difficulty:** {r.get('difficulty_level')} • **Salary:** {r.get('salary_range')}")
            det = r["details"]
            if det["skill_matches"] or det["selected_skill_matches"]:
                st.write("**Exact skill matches:**", ", ".join(det["skill_matches"] + det["selected_skill_matches"]))
            if det["interest_matches"]:
                st.write("**Interest matches:**", ", ".join(det["interest_matches"]))
            if det["role_matches"]:
                st.write("**Preferred role matches:**", ", ".join(det["role_matches"]))
            if det["industry_matches"]:
                st.write("**Industry matches:**", ", ".join(det["industry_matches"]))
            if det["fuzzy_matches"]:
                st.write("**Fuzzy matches (close):**", ", ".join(det["fuzzy_matches"]))

            # Suggested next skills
            req_set = to_token_set(r["required_skills"])
            user_set = to_token_set(combined_skills_str) | to_token_set(live_interests)
            to_learn = sorted(list(req_set - user_set))
            if to_learn:
                st.write("**Suggested skills to learn next:**", ", ".join(to_learn[:10]))

            st.write(r["description"])

            # ========== Visualizations for this career ==========
            with st.expander("Show learning visuals for this career"):
                # parse required_skills into list
                required_skills_text = r.get("required_skills", "")
                required_skills = [s.strip() for s in re.split(r'[,\n]+', required_skills_text) if s.strip()]

                # user skill list
                user_skill_list = [tok.strip() for tok in re.split(r'[,\n]+', combined_skills_str) if tok.strip()]

                # get weekly_hours numeric
                try:
                    weekly_hours_val = int(weekly_hours_control)
                except Exception:
                    weekly_hours_val = 5

                # Timeline
                fig_tl = Visualization.create_timeline_chart(required_skills, skills_df, weekly_hours=weekly_hours_val)
                st.pyplot(fig_tl)

                # Skill gap
                fig_gap = Visualization.create_skill_gap_chart(user_skill_list, required_skills)
                st.pyplot(fig_gap)

                # Weekly progress
                fig_progress = Visualization.create_weekly_progress_chart(required_skills, skills_df, user_skill_list, weekly_hours=weekly_hours_val, weeks_to_plot=10)
                st.pyplot(fig_progress)

                # Skills by category
                fig_cat = Visualization.create_skill_category_chart(skills_df, required_skills)
                st.pyplot(fig_cat)

            st.write("---")

# -------------------------
# Bottom: DB stats & sample data
# -------------------------
st.header("Database & sample data")
stats = db.get_database_stats()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Users", stats["users"])
c2.metric("Career Paths", stats["career_paths"])
c3.metric("Skills", stats["skills"])
c4.metric("Roadmaps", stats["roadmaps"])

st.subheader("Sample career paths")
career_paths = db.get_sample_career_paths(limit=10)
if career_paths:
    st.dataframe(pd.DataFrame(career_paths)[["id","title","duration_weeks","required_skills"]])
else:
    st.info("No career paths found.")

st.subheader("Skills table")
skills = db.get_all_skills()
skills_df_bottom = pd.DataFrame(skills) if skills else pd.DataFrame(columns=["id","name","category","estimated_hours"])
st.dataframe(skills_df_bottom[["id","name","category","estimated_hours"]].fillna(""))
