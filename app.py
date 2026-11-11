"""Streamlit interface:  streamlit run app.py"""
import sys
from dataclasses import replace
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from roadmap.data_loader import load_dataset  # noqa: E402
from roadmap.pipeline import build_roadmap, with_unavailable  # noqa: E402
from roadmap.scenarios import run_all  # noqa: E402

st.set_page_config(page_title="Career Roadmap Optimizer", layout="wide")


@st.cache_data
def base_data():
    return load_dataset(Path(__file__).parent / "data")


data = base_data()
skill_label = {sid: f"{s.name} ({sid})" for sid, s in data.skills.items()}

# ---- Inputs ---------------------------------------------------------------
st.sidebar.header("Student profile")
current = st.sidebar.multiselect(
    "Current skills", options=list(data.skills), default=sorted(data.student_skills),
    format_func=skill_label.get)

st.sidebar.header("Resource availability")
already_off = [r.resource_id for r in data.resources if r.unavailable]
st.sidebar.caption("Unavailable in the dataset: " + (", ".join(already_off) or "none"))
extra_off = st.sidebar.multiselect(
    "Mark more resources unavailable",
    options=[r.resource_id for r in data.resources if not r.unavailable],
    format_func=lambda rid: next(f"{rid} - {r.name}" for r in data.resources if r.resource_id == rid))

if not current:
    st.warning("Select at least one current skill.")
    st.stop()

run_data = with_unavailable(replace(data, student_skills=set(current)), set(extra_off))
rm = build_roadmap(run_data)
a, b = rm.part_a, rm.part_b

# ---- Summary --------------------------------------------------------------
st.title("Career Roadmap Optimization System")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total career value", b.total_value)
c2.metric("Hours used", f"{sum(b.hours_used.values())}/{sum(b.budgets.values())}")
c3.metric("Learning hours (Part A)", a.total_hours)
c4.metric("Unreachable skills", len(a.unreachable_skills))

# ---- Part B: roadmap ------------------------------------------------------
st.header("Month-by-month roadmap")
cols = st.columns(len(b.schedule))
for col, (month, acts) in zip(cols, b.schedule.items()):
    with col:
        st.subheader(f"Month {month}")
        st.progress(b.hours_used[month] / b.budgets[month] if b.budgets[month] else 0.0,
                    text=f"{b.hours_used[month]}/{b.budgets[month]} h")
        for x in acts:
            st.markdown(f"**{x.name}**  \n{x.type} · {x.hours} h · value {x.career_value}  \n"
                        f"unlocks *{data.skills[x.skill_unlocked].name}*")
        if not acts:
            st.caption("No activity fits")

excluded = (
    [{"Activity": x.name, "Hours": x.hours, "Reason": f"skill {data.skills[x.skill_unlocked].name} unreachable"}
     for x in b.ineligible]
    + [{"Activity": x.name, "Hours": x.hours, "Reason": "longer than every month's budget"} for x in b.oversized]
    + [{"Activity": x.name, "Hours": x.hours, "Reason": "did not fit in the optimal plan"} for x in b.unscheduled])
if excluded:
    st.subheader("Excluded activities")
    st.dataframe(excluded, hide_index=True, width="stretch")

# ---- Part A: resources ----------------------------------------------------
st.header("Learning resources (Kruskal MST)")
st.dataframe(
    [{"ID": r.resource_id, "Resource": r.name, "Connects": f"{data.skills[r.skill_a].name} - "
      f"{data.skills[r.skill_b].name}", "Hours": r.hours} for r in a.chosen_resources],
    hide_index=True, width="stretch")
left, right = st.columns(2)
left.markdown("**Reachable skills:** " + ", ".join(skill_label[s] for s in sorted(a.reachable_skills)))
right.markdown("**Unreachable skills:** "
               + (", ".join(skill_label[s] for s in sorted(a.unreachable_skills)) or "none"))
with st.expander("Kruskal step-by-step trace"):
    st.code("\n".join(a.trace))

# ---- Tests ----------------------------------------------------------------
with st.expander("Test scenarios (disconnected skills, over-demand, oversized, updates)"):
    ok, text = run_all(data)
    (st.success if ok else st.error)("All tests passed" if ok else "Some tests failed")
    st.code(text)
