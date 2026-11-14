"""Streamlit interface:  streamlit run app.py"""
import sys
from dataclasses import replace
from html import escape
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from roadmap.data_loader import list_presets, load_dataset, read_student_file  # noqa: E402
from roadmap.pipeline import build_roadmap, with_unavailable  # noqa: E402
from roadmap.report import (excluded_lines, per_week, plural, revision_summary,  # noqa: E402
                            weekly_plan)
from roadmap.scenarios import run_scenarios  # noqa: E402
from roadmap.ui_theme import CSS, variables  # noqa: E402

DATA_DIR = Path(__file__).parent / "data"

st.set_page_config(page_title="Career Roadmap Optimizer", page_icon="🧭", layout="wide")


def html(markup: str) -> None:
    """Render raw HTML. Lines are joined so Markdown never treats indentation as code."""
    st.markdown(" ".join(line.strip() for line in markup.splitlines() if line.strip()),
                unsafe_allow_html=True)


# ---- Cached computation ------------------------------------------------------
# The dataset, each roadmap and the test scenarios are computed once and reused on every click.
# The signature changes when a CSV in data/ is edited, so edits still show up.
def data_signature() -> tuple:
    return tuple((p.name, p.stat().st_mtime_ns) for p in sorted(DATA_DIR.rglob("*.csv")))


@st.cache_resource(show_spinner=False)
def get_data(sig: tuple):
    return load_dataset(DATA_DIR)


@st.cache_resource(show_spinner=False)
def get_presets(sig: tuple) -> dict:
    return {label: frozenset(read_student_file(path)) for label, path in list_presets(DATA_DIR).items()}


@st.cache_resource(show_spinner=False)
def get_roadmap(sig: tuple, skills: tuple, off: tuple):
    data = replace(get_data(sig), student_skills=set(skills))
    return build_roadmap(with_unavailable(data, set(off)))


@st.cache_resource(show_spinner=False)
def get_scenarios(sig: tuple):
    return run_scenarios(get_data(sig))


sig = data_signature()
data = get_data(sig)
presets = get_presets(sig)
skill_name = {sid: s.name for sid, s in data.skills.items()}
resource_by_id = {r.resource_id: r for r in data.resources}

# ---- Navigation state ----------------------------------------------------------
st.session_state.setdefault("view", 0)         # 0 = overview, n = the page of month n


def open_month(n: int) -> None:
    st.session_state.view = n


def go_home() -> None:
    st.session_state.view = 0


# ---- Theme + sidebar -----------------------------------------------------------
if "dark" not in st.session_state:
    st.session_state.dark = False   # always open in light mode; the toggle switches to dark

with st.sidebar:
    html('<div class="brand">🧭 Roadmap Optimizer</div>'
         '<div class="brand-sub">Kruskal MST + Multiple Knapsack DP</div>')
    st.toggle("🌙 Dark mode", key="dark")

st.markdown(variables(st.session_state.dark), unsafe_allow_html=True)
st.markdown(CSS, unsafe_allow_html=True)

CUSTOM = "Custom"
if "skills" not in st.session_state:
    st.session_state.skills = sorted(data.student_skills)
    match = [label for label, ids in presets.items() if ids == frozenset(data.student_skills)]
    st.session_state.preset = match[0] if match else CUSTOM


def apply_preset() -> None:
    label = st.session_state.preset
    if label in presets:
        st.session_state.skills = sorted(presets[label])


with st.sidebar:
    st.markdown("**Student Profile**")
    st.selectbox("Start from a profile", [CUSTOM, *presets], key="preset", on_change=apply_preset)
    current = st.multiselect("Your skills", options=list(data.skills), key="skills",
                             format_func=lambda s: f"{skill_name[s]} ({s})")
    st.markdown("**Resource Availability**")
    extra_off = st.multiselect(
        "Mark more resources unavailable",
        options=[r.resource_id for r in data.resources if not r.unavailable],
        format_func=lambda rid: f"{rid} · {resource_by_id[rid].name}",
        help="The plan is recomputed straight away.")
    st.caption("Already unavailable in the dataset: "
               + (", ".join(r.resource_id for r in data.resources if r.unavailable) or "none"))

if not current:
    html('<div class="banner t-internship">Pick at least one skill you already know in the sidebar '
         '(or choose a profile) to build your roadmap.</div>')
    st.stop()

rm = get_roadmap(sig, tuple(sorted(current)), tuple(sorted(extra_off)))
a, b = rm.part_a, rm.part_b
run_data = rm.data

used, budget = sum(b.hours_used.values()), sum(b.budgets.values())
n_acts = sum(len(m.items) for m in rm.months)
unlocked = {i.activity.skill_unlocked for m in rm.months for i in m.items}
plans = {m.month: weekly_plan(m, rm) for m in rm.months}


def month_title(m) -> str:
    return " + ".join(it.activity.name for it in m.items) or "Revision and career preparation"


# ======================================================================================
# Month page
# ======================================================================================
def month_page(n: int) -> None:
    m = next(x for x in rm.months if x.month == n)
    st.button("← Back to all months", on_click=go_home, key="back_top")
    chips = "".join(f'<span class="chip accent">{escape(it.skill.name)}</span>' for it in m.items)
    hours = (f"{m.hours_used} of {m.budget} hours · about {per_week(m.hours_used)} h per week"
             + (f" · plus about {m.prep_hours} h of study-first resources" if m.prep_hours else "")
             if m.items else f"{m.budget} hours available · revision month")
    html(f'<div class="hero"><div class="eyebrow">Month {n} of {len(rm.months)}</div>'
         f'<h1>{escape(month_title(m))}</h1><p>{escape(hours)}</p>'
         f'<div class="chips">{chips}</div></div>')
    if not m.items:
        html(f'<div class="callout t-project"><b>This month:</b> {escape(revision_summary(rm, m))}</div>')
        for week in plans[n]:
            for t in week:
                st.markdown(f"- {t.text}")
    for it in m.items:
        x, sk = it.activity, it.skill
        with st.container(border=True):
            html(f'<div class="t-{escape(x.type)}"><div class="act-head"><span class="pill">{escape(x.type)}</span>'
                 f'<span class="act-val">+{x.career_value} career value</span></div>'
                 f'<div class="act-title">{escape(x.name)}</div>'
                 f'<div class="act-sub">{x.hours} h · unlocks {escape(sk.name)} · '
                 f'{escape(sk.level_name.lower())} level, {escape(sk.category)}</div></div>')
            if x.deliverable:
                html(f'<div class="callout t-accent"><b>You will have built:</b> {escape(x.deliverable)}</div>')
            if it.prep:
                html('<div class="block-label">Study first</div>' + "".join(
                    f'<div class="mini"><span>{escape(r.name)}'
                    + (f' · {escape(r.provider)}' if r.provider else "") + f'</span><span>{r.hours} h</span></div>'
                    for r in it.prep))
            if it.reused:
                html('<div class="hint">Already covered earlier in your plan: '
                     + escape(", ".join(r.name for r in it.reused)) + "</div>")
            if x.syllabus:
                html('<div class="block-label">What this covers</div>' + "".join(
                    f'<div class="mini"><span>{i}. {escape(mod)}</span></div>' for i, mod in enumerate(x.syllabus, 1)))
            if sk.tip:
                html(f'<div class="callout t-project"><b>Tip:</b> {escape(sk.tip)}</div>')

    cols = st.columns(2)
    if n > 1:
        cols[0].button(f"← Month {n - 1}", on_click=open_month, args=(n - 1,), key="prev")
    if n < len(rm.months):
        cols[1].button(f"Month {n + 1} →", on_click=open_month, args=(n + 1,), key="next")


if st.session_state.view and st.session_state.view not in {m.month for m in rm.months}:
    go_home()
if st.session_state.view:
    month_page(st.session_state.view)
    st.stop()

# ======================================================================================
# Overview
# ======================================================================================
known = "".join(f'<span class="chip accent">{escape(skill_name[s])}</span>' for s in sorted(current))
html(f"""
<div class="hero">
  <div class="eyebrow">CT-363 · Design and Analysis of Algorithms</div>
  <h1>Your six-month career roadmap</h1>
  <p>Month by month: what to study, what to build, and why. Built from the cheapest learning path
     to every skill you can reach and the highest-value mix of courses, projects and internships
     that fits each month's hours.</p>
  <div class="chips"><span class="chip">You know</span>{known}</div>
</div>
""")

metrics = [
    ("t-accent", "Total career value", b.total_value, f"{plural(n_acts, 'activity', 'activities')} scheduled"),
    ("t-course", "Hours scheduled", f"{used}/{budget}",
     f"{round(100 * used / budget) if budget else 0}% of the six months"),
    ("t-project", "New skills", len(unlocked), "unlocked by the plan"),
    ("t-internship", "Learning path", f"{a.total_hours} h", f"{plural(len(a.chosen_resources), 'resource')} in the tree"),
    ("t-rose", "Unreachable skills", len(a.unreachable_skills), f"{len(a.reachable_skills)} of {len(data.skills)} reachable"),
]
html('<div class="metrics">' + "".join(
    f'<div class="metric {tone}"><div class="label">{label}</div><div class="value">{value}</div>'
    f'<div class="sub">{sub}</div></div>' for tone, label, value, sub in metrics) + "</div>")

tab_plan, tab_learn, tab_skills, tab_tests = st.tabs(
    ["🗺️ Roadmap", "📚 Learning path", "🧩 Skills", "✅ Tests"])

# ---- Roadmap ----------------------------------------------------------------
with tab_plan:
    if n_acts == 0:
        st.info("No new courses are available for your skills with the current resources, so every month "
                "is revision and career preparation.")
    html('<div class="legend"><span class="t-course"><i class="dot"></i>Course</span>'
         '<span class="t-project"><i class="dot"></i>Project</span>'
         '<span class="t-internship"><i class="dot"></i>Internship</span>'
         '<span class="t-muted"><i class="dot"></i>Revision</span></div>')
    html('<div class="section-note">Open a month to see its activities, study resources and deliverables.</div>')
    for row in range(0, len(rm.months), 3):
        # keyed container: ui_theme.py gives the cards in a row equal heights so the buttons line up
        cols = st.container(key=f"month-row-{row}").columns(3)
        for col, m in zip(cols, rm.months[row:row + 3]):
            pct = 100 * m.hours_used / m.budget if m.budget else 0
            items = "".join(
                f'<div class="act t-{escape(it.activity.type)}"><div class="act-top">'
                f'<span class="pill">{escape(it.activity.type)}</span>'
                f'<span class="act-val">+{it.activity.career_value} value</span></div>'
                f'<div class="act-name">{escape(it.activity.name)}</div>'
                f'<div class="act-meta">{it.activity.hours} h · unlocks {escape(it.skill.name)}</div></div>'
                for it in m.items) or ('<div class="act t-muted"><div class="act-top"><span class="pill">revision</span></div>'
                                       '<div class="act-name">Revision and career preparation</div>'
                                       f'<div class="act-meta">{m.budget} h to consolidate and get job-ready</div></div>')
            with col:
                html(f'<div class="month"><div class="month-head"><span class="month-name">Month {m.month}</span>'
                     f'<span class="month-hours">{m.hours_used} / {m.budget} h</span></div>'
                     f'<div class="bar"><div style="width:{pct:.0f}%"></div></div>{items}</div>')
                st.button(f"Open Month {m.month}", key=f"open{m.month}",
                          on_click=open_month, args=(m.month,))

    excluded = excluded_lines(rm)
    if excluded:
        html('<div class="section-title">Not in your plan</div>')
        html('<div class="list">' + "".join(
            f'<div class="row"><span class="id">{x.activity_id}</span>'
            f'<div><div class="main">{escape(x.name)}</div><div class="sub">{x.hours} h · value {x.career_value}</div></div>'
            f'<span class="reason t-{"rose" if "unreachable" in why else "peach" if "more than any single month" in why else "sage" if "already know" in why else "muted"}">'
            f'{escape(why)}</span></div>' for x, why in excluded) + "</div>")

# ---- Learning path ----------------------------------------------------------
with tab_learn:
    needed = {r.resource_id for m in rm.months for it in m.items for r in it.prep + it.reused}
    html(f'<div class="section-title">Cheapest learning path · {a.total_hours} hours</div>'
         '<div class="section-note">Kruskal\'s minimum spanning tree: the fewest total hours that connect '
         'what you know to every skill you can reach. "Needed" resources are the ones your scheduled '
         'activities rely on.</div>')
    html('<div class="list">' + "".join(
        f'<div class="row compact"><span class="id">{r.resource_id}</span>'
        f'<div><div class="main">{escape(r.name)}</div>'
        f'<div class="sub">{escape(skill_name[r.skill_a])} ↔ {escape(skill_name[r.skill_b])}'
        + (f' · {escape(r.provider)}' if r.provider else "") + '</div></div>'
        f'<span class="tag {"t-project" if r.resource_id in needed else "t-muted"}">'
        f'{"needed" if r.resource_id in needed else "extra"}</span>'
        f'<span class="right">{r.hours} h</span></div>' for r in a.chosen_resources)
        + ("" if a.chosen_resources else '<div class="row"><span></span><div class="sub">No resources needed.</div></div>')
        + "</div>")
    off = [r.resource_id for r in run_data.resources if r.unavailable]
    html('<div class="section-title">Unavailable resources (never used)</div><div class="chips">'
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
            f'<small>relevance {data.skills[s].relevance} · demand {data.skills[s].demand}</small></span>'
            for s in sorted(ids, key=lambda s: -data.skills[s].relevance)) + "</div>"

    html(f'<div class="section-title">Reachable skills ({len(a.reachable_skills)})</div>'
         + skill_chips(a.reachable_skills, "sage"))
    html(f'<div class="section-title">Unreachable skills ({len(a.unreachable_skills)})</div>'
         + (skill_chips(a.unreachable_skills, "rose") if a.unreachable_skills
            else '<div class="section-note">Every skill is reachable.</div>'))
    html(f'<div class="section-title">Unlocked by the roadmap ({len(unlocked)})</div>'
         + (skill_chips(unlocked, "accent") if unlocked else '<div class="section-note">None yet.</div>'))

    html('<div class="section-title">Browse a skill</div>')
    pick = st.selectbox("Skill", list(data.skills), format_func=lambda s: f"{skill_name[s]} ({data.skills[s].category})",
                        label_visibility="collapsed")
    sk = data.skills[pick]
    html(f'<div class="act-sub">{escape(sk.level_name)} level · {escape(sk.category)} · '
         f'relevance {sk.relevance}, demand {sk.demand}</div>')
    for topic in sk.topics:
        st.markdown(f"- {topic}")
    if sk.tip:
        html(f'<div class="callout t-project"><b>Tip:</b> {escape(sk.tip)}</div>')
    for act in data.activities:
        if act.skill_unlocked == pick:
            html(f'<div class="callout t-accent"><b>Activity:</b> {escape(act.name)} · {act.hours} h · '
                 f'value {act.career_value}</div>')

# ---- Tests ------------------------------------------------------------------
with tab_tests:
    results = get_scenarios(sig)
    ok = all(s.ok for s in results)
    html(f'<div class="banner {"t-project" if ok else "t-rose"}">'
         f'{"✓ All test scenarios passed" if ok else "✗ Some test scenarios failed"}</div>'
         '<div class="section-note">Run on the dataset\'s own student profile (data/student.csv), '
         'independent of the sidebar: disconnected skills, hours over-demand, oversized activity, '
         'and recomputing when resources become unavailable.</div>')
    html("".join(
        f'<div class="test"><h4>{escape(s.title)}</h4>' + "".join(
            f'<div class="check {"t-project" if c else "t-rose"}"><span class="mark">{"✓" if c else "✗"}</span>'
            f'<span>{escape(t)}</span></div>' for c, t in s.checks) + "</div>" for s in results))
