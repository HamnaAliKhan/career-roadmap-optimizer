"""Streamlit interface:  streamlit run app.py"""
import sys
from dataclasses import replace
from html import escape
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from roadmap.data_loader import load_dataset  # noqa: E402
from roadmap.pipeline import build_roadmap, with_unavailable  # noqa: E402
from roadmap.scenarios import run_all  # noqa: E402
from roadmap.ui_theme import CSS, variables  # noqa: E402

st.set_page_config(page_title="Career Roadmap Optimizer", page_icon="🧭", layout="wide")


def html(markup: str) -> None:
    """Render raw HTML. Lines are joined so Markdown never treats indentation as code."""
    st.markdown(" ".join(line.strip() for line in markup.splitlines() if line.strip()),
                unsafe_allow_html=True)


@st.cache_data
def base_data():
    return load_dataset(Path(__file__).parent / "data")


data = base_data()
skill_name = {sid: s.name for sid, s in data.skills.items()}
resource_by_id = {r.resource_id: r for r in data.resources}

# ---- Theme toggle -----------------------------------------------------------
if "dark" not in st.session_state:
    try:
        st.session_state.dark = st.context.theme.type == "dark"
    except Exception:
        st.session_state.dark = False

with st.sidebar:
    html('<div class="brand">🧭 Roadmap Optimizer</div>'
         '<div class="brand-sub">Kruskal MST + Multiple Knapsack DP</div>')
    st.toggle("🌙 Dark mode", key="dark")

st.markdown(variables(st.session_state.dark), unsafe_allow_html=True)
st.markdown(CSS, unsafe_allow_html=True)

# ---- Inputs -----------------------------------------------------------------
with st.sidebar:
    st.markdown("**Student profile**")
    current = st.multiselect("Current skills", options=list(data.skills),
                             default=sorted(data.student_skills),
                             format_func=lambda s: f"{skill_name[s]} ({s})")
    st.markdown("**Resource availability**")
    already_off = [r.resource_id for r in data.resources if r.unavailable]
    extra_off = st.multiselect(
        "Mark more resources unavailable",
        options=[r.resource_id for r in data.resources if not r.unavailable],
        format_func=lambda rid: f"{rid} · {resource_by_id[rid].name}")
    st.caption("Already unavailable in the dataset: " + (", ".join(already_off) or "none"))

if not current:
    st.warning("Select at least one current skill in the sidebar to build a roadmap.")
    st.stop()

run_data = with_unavailable(replace(data, student_skills=set(current)), set(extra_off))
rm = build_roadmap(run_data)
a, b = rm.part_a, rm.part_b

# ---- Hero + metrics ---------------------------------------------------------
known = "".join(f'<span class="chip accent">{escape(skill_name[s])}</span>' for s in sorted(current))
html(f"""
<div class="hero">
  <div class="eyebrow">CT-363 · Design and Analysis of Algorithms</div>
  <h1>Your six-month career roadmap</h1>
  <p>The cheapest learning path to every reachable skill, and the highest-value mix of
     courses, projects and internships that fits each month's hours.</p>
  <div class="chips">{known}</div>
</div>
""")

used, budget = sum(b.hours_used.values()), sum(b.budgets.values())
metrics = [
    ("t-accent", "Total career value", b.total_value, f"{sum(len(x) for x in b.schedule.values())} activities scheduled"),
    ("t-course", "Hours used", f"{used}/{budget}", f"{round(100 * used / budget) if budget else 0}% of the semester budget"),
    ("t-project", "Learning hours", a.total_hours, f"{len(a.chosen_resources)} resources in the MST"),
    ("t-rose", "Unreachable skills", len(a.unreachable_skills), f"{len(a.reachable_skills)} of {len(data.skills)} reachable"),
]
html('<div class="metrics">' + "".join(
    f'<div class="metric {tone}"><div class="label">{label}</div><div class="value">{value}</div>'
    f'<div class="sub">{sub}</div></div>' for tone, label, value, sub in metrics) + "</div>")

tab_plan, tab_learn, tab_skills, tab_tests = st.tabs(["Roadmap", "Learning path", "Skills", "Tests"])

# ---- Roadmap ----------------------------------------------------------------
with tab_plan:
    html('<div class="legend"><span class="t-course"><i class="dot"></i>Course</span>'
         '<span class="t-project"><i class="dot"></i>Project</span>'
         '<span class="t-internship"><i class="dot"></i>Internship</span></div>')
    cards = []
    for month, acts in b.schedule.items():
        cap = b.budgets[month]
        pct = 100 * b.hours_used[month] / cap if cap else 0
        items = "".join(
            f'<div class="act t-{escape(x.type)}"><div class="act-top"><span class="pill">{escape(x.type)}</span>'
            f'<span class="act-val">+{x.career_value} value</span></div>'
            f'<div class="act-name">{escape(x.name)}</div>'
            f'<div class="act-meta">{x.hours} h · unlocks {escape(skill_name[x.skill_unlocked])}</div></div>'
            for x in acts) or '<div class="empty">Free month: nothing else fits</div>'
        cards.append(f'<div class="month"><div class="month-head"><span class="month-name">Month {month}</span>'
                     f'<span class="month-hours">{b.hours_used[month]} / {cap} h</span></div>'
                     f'<div class="bar"><div style="width:{pct:.0f}%"></div></div>{items}</div>')
    html('<div class="months">' + "".join(cards) + "</div>")

    excluded = (
        [(x, "t-rose", f"Skill {skill_name[x.skill_unlocked]} is unreachable") for x in b.ineligible]
        + [(x, "t-internship", "Longer than every month's budget") for x in b.oversized]
        + [(x, "t-muted", "Did not fit in the optimal plan") for x in b.unscheduled])
    if excluded:
        html('<div class="section-title">Excluded activities</div>')
        html('<div class="list">' + "".join(
            f'<div class="row {tone}"><span class="id">{x.activity_id}</span>'
            f'<div><div class="main">{escape(x.name)}</div><div class="sub">{x.hours} h · value {x.career_value}</div></div>'
            f'<span class="pill">{escape(reason)}</span></div>' for x, tone, reason in excluded) + "</div>")

# ---- Learning path ----------------------------------------------------------
with tab_learn:
    html(f'<div class="section-title">Minimum spanning tree · {a.total_hours} learning hours</div>'
         '<div class="section-note">The cheapest set of resources that connects your current skills '
         'to every skill you can reach.</div>')
    html('<div class="list">' + "".join(
        f'<div class="row"><span class="id">{r.resource_id}</span>'
        f'<div><div class="main">{escape(r.name)}</div>'
        f'<div class="sub">{escape(skill_name[r.skill_a])} ↔ {escape(skill_name[r.skill_b])}</div></div>'
        f'<span class="right">{r.hours} h</span></div>' for r in a.chosen_resources)
        + ("" if a.chosen_resources else '<div class="row"><span></span><div class="sub">No resources needed.</div></div>')
        + "</div>")
    off = [r.resource_id for r in run_data.resources if r.unavailable]
    html('<div class="section-title">Unavailable resources</div><div class="chips">'
         + "".join(f'<span class="chip rose">{rid} · {escape(resource_by_id[rid].name)}</span>' for rid in off)
         + "</div>")
    st.write("")
    with st.expander("Kruskal step-by-step trace"):
        html('<div class="trace">' + "".join(
            f'<div class="{"take" if t.startswith("take") else "skip"}">'
            f'{"✓" if t.startswith("take") else "·"} {escape(t)}</div>' for t in a.trace) + "</div>")

# ---- Skills -----------------------------------------------------------------
with tab_skills:
    def skill_chips(ids, tone):
        return '<div class="chips">' + "".join(
            f'<span class="chip {tone}">{escape(skill_name[s])} '
            f'<small>R{data.skills[s].relevance} · D{data.skills[s].demand}</small></span>'
            for s in sorted(ids, key=lambda s: -data.skills[s].relevance)) + "</div>"

    html(f'<div class="section-title">Reachable skills ({len(a.reachable_skills)})</div>'
         '<div class="section-note">R = relevance, D = demand (1–10). Sorted by relevance.</div>'
         + skill_chips(a.reachable_skills, "sage"))
    html(f'<div class="section-title">Unreachable skills ({len(a.unreachable_skills)})</div>'
         + (skill_chips(a.unreachable_skills, "rose") if a.unreachable_skills
            else '<div class="section-note">Every skill is reachable.</div>'))
    unlocked = {x.skill_unlocked for acts in b.schedule.values() for x in acts}
    html(f'<div class="section-title">Unlocked by the roadmap ({len(unlocked)})</div>'
         + skill_chips(unlocked, "accent"))

# ---- Tests ------------------------------------------------------------------
with tab_tests:
    ok, text = run_all(data)
    tone = "t-project" if ok else "t-rose"
    html(f'<div class="banner {tone}">{"✓ All test scenarios passed" if ok else "✗ Some test scenarios failed"}'
         '</div><div class="section-note">Run on the original dataset: disconnected skills, hours '
         'over-demand, oversized activity, and recomputing when resources become unavailable.</div>')
    blocks = []
    for block in text.split("\n\n")[:-1]:
        title, *checks = block.split("\n")
        rows = "".join(
            f'<div class="check {"t-project" if "[PASS]" in c else "t-rose"}">'
            f'<span class="mark">{"✓" if "[PASS]" in c else "✗"}</span>'
            f'<span>{escape(c.split("] ", 1)[-1])}</span></div>' for c in checks)
        blocks.append(f'<div class="test"><h4>{escape(title)}</h4>{rows}</div>')
    html("".join(blocks))
