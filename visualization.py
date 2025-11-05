
# visualization.py
import matplotlib.pyplot as plt
import pandas as pd
from typing import List
import math

def _ensure_fig():
    fig, ax = plt.subplots(figsize=(7, 3.5))
    return fig, ax

class Visualization:
    @staticmethod
    def create_timeline_chart(required_skills: List[str],
                              skills_db: pd.DataFrame,
                              weekly_hours: int = 5) -> plt.Figure:
        """
        Gantt-like timeline: Each skill gets estimated_hours (from skills_db)
        and laid out sequentially into weeks. weekly_hours = user's available hours/week.
        required_skills: list of skill names (strings).
        skills_db: dataframe with columns ['name','estimated_hours']
        """
        # Map required_skills to estimated hours (fallback to 12 hours)
        hours_list = []
        skills_db_local = skills_db.copy() if skills_db is not None else pd.DataFrame()
        if 'name' in skills_db_local.columns:
            skills_db_local['name_lower'] = skills_db_local['name'].str.lower()
        for s in required_skills:
            hrs = 12
            if not skills_db_local.empty and 'name_lower' in skills_db_local.columns:
                row = skills_db_local[skills_db_local['name_lower'] == s.lower()]
                if not row.empty:
                    try:
                        val = row.iloc[0].get('estimated_hours')
                        hrs = int(val) if pd.notna(val) else 12
                    except Exception:
                        hrs = 12
            hours_list.append((s, hrs))

        # Build week ranges
        bars = []
        current_week = 0
        for name, hrs in hours_list:
            weeks_needed = max(1, math.ceil(hrs / max(1, weekly_hours)))
            bars.append((name, current_week, weeks_needed))
            current_week += weeks_needed

        # plot horizontal bars
        fig, ax = plt.subplots(figsize=(10, max(2, 0.6 * len(bars))))
        y_pos = range(len(bars))
        for i, (name, start_w, dur_w) in enumerate(bars):
            ax.barh(i, dur_w, left=start_w, height=0.6)
            ax.text(start_w + dur_w / 2, i, f"{name} ({dur_w} wk)", va='center', ha='center', fontsize=9, color='white')

        ax.set_yticks(list(y_pos))
        ax.set_yticklabels([b[0] for b in bars])
        ax.set_xlabel("Weeks")
        ax.set_title("Learning timeline (approx.)")
        ax.invert_yaxis()
        plt.tight_layout()
        return fig

    @staticmethod
    def create_skill_gap_chart(user_skills: List[str],
                               required_skills: List[str]) -> plt.Figure:
        """
        Pie chart: percentage of required skills user already knows vs to learn.
        """
        req_set = {s.lower() for s in required_skills}
        user_set = {s.lower() for s in user_skills}

        have = len(req_set & user_set)
        to_learn = max(0, len(req_set) - have)
        labels = []
        sizes = []
        if have > 0:
            labels.append("Have")
            sizes.append(have)
        if to_learn > 0:
            labels.append("To learn")
            sizes.append(to_learn)
        if not labels:
            fig, ax = _ensure_fig()
            ax.text(0.5, 0.5, "No required skills", ha='center', va='center')
            ax.axis('off')
            return fig

        fig, ax = plt.subplots(figsize=(4, 4))
        ax.pie(sizes, labels=labels, autopct="%1.0f", startangle=90)
        ax.set_title("Skill gap")
        ax.axis('equal')
        plt.tight_layout()
        return fig

    @staticmethod
    def create_weekly_progress_chart(required_skills: List[str],
                                     skills_db: pd.DataFrame,
                                     user_skills: List[str],
                                     weekly_hours: int = 5,
                                     weeks_to_plot: int = 8) -> plt.Figure:
        """
        Cumulative planned hours vs actual (placeholder actual = 0).
        """
        total_to_learn_hours = 0
        user_lower = {u.lower() for u in user_skills}
        skills_db_local = skills_db.copy() if skills_db is not None else pd.DataFrame()
        if 'name' in skills_db_local.columns:
            skills_db_local['name_lower'] = skills_db_local['name'].str.lower()

        for s in required_skills:
            if s.lower() in user_lower:
                continue
            hrs = 12
            if not skills_db_local.empty and 'name_lower' in skills_db_local.columns:
                row = skills_db_local[skills_db_local['name_lower'] == s.lower()]
                if not row.empty:
                    try:
                        val = row.iloc[0].get('estimated_hours')
                        hrs = int(val) if pd.notna(val) else 12
                    except Exception:
                        hrs = 12
            total_to_learn_hours += hrs

        planned_weekly = max(1, int(weekly_hours))
        weeks = list(range(1, weeks_to_plot + 1))
        cumulative_planned = []
        cumulative_hours = 0
        for w in weeks:
            cumulative_hours += planned_weekly
            cumulative_planned.append(min(cumulative_hours, total_to_learn_hours))

        cumulative_actual = [0 for _ in weeks]

        fig, ax = plt.subplots(figsize=(8, 3.5))
        ax.plot(weeks, cumulative_planned, marker='o', label='Planned cumulative hours')
        ax.plot(weeks, cumulative_actual, marker='o', label='Actual cumulative hours')
        ax.set_xlabel("Week")
        ax.set_ylabel("Cumulative hours")
        ax.set_title("Weekly learning progress (example)")
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.3)
        plt.tight_layout()
        return fig

    @staticmethod
    def create_skill_category_chart(skills_df: pd.DataFrame,
                                    required_skills: List[str]) -> plt.Figure:
        """
        Horizontal bar chart: counts of skill categories for required_skills if available in skills_df.
        """
        if skills_df is None or skills_df.empty:
            fig, ax = _ensure_fig()
            ax.text(0.5, 0.5, "No skills DB", ha='center', va='center')
            ax.axis('off')
            return fig

        mapping = {}
        skills_df_local = skills_df.copy()
        if 'name' in skills_df_local.columns:
            skills_df_local['name_lower'] = skills_df_local['name'].str.lower()
        for s in required_skills:
            row = skills_df_local[skills_df_local['name_lower'] == s.lower()] if 'name_lower' in skills_df_local.columns else pd.DataFrame()
            if not row.empty:
                cat = row.iloc[0].get('category') or "Other"
            else:
                cat = "Other"
            mapping[s] = cat

        df = pd.DataFrame(list(mapping.items()), columns=['skill', 'category'])
        if df.empty:
            fig, ax = _ensure_fig()
            ax.text(0.5, 0.5, "No mapping available", ha='center', va='center')
            ax.axis('off')
            return fig

        grouped = df.groupby('category').size().sort_values()
        fig, ax = plt.subplots(figsize=(6, 3 + 0.4 * len(grouped)))
        grouped.plot(kind='barh', ax=ax)
        ax.set_xlabel("Number of required skills")
        ax.set_ylabel("Category")
        ax.set_title("Required skills by category")
        plt.tight_layout()
        return fig
