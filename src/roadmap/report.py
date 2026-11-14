"""Turns a Roadmap into readable text and into the week-by-week syllabus the app shows."""
import textwrap
from dataclasses import dataclass

from .pipeline import PlanMonth, Roadmap

WEEKS_PER_MONTH = 4.3
WEEKS = 4
WIDTH = 78


@dataclass(frozen=True)
class Task:
    kind: str      # study | learn | build | revise | career
    text: str
    key: str       # stable id, used for checklist state


def skill_names(rm: Roadmap, ids) -> str:
    return ", ".join(rm.data.skills[s].name for s in sorted(ids)) or "none"


def resource_line(r) -> str:
    provider = f" - {r.provider}" if r.provider else ""
    return f"{r.resource_id} {r.name}{provider}, {r.hours} h"


def plural(n: int, singular: str, plural_form: str | None = None) -> str:
    return f"{n} {singular if n == 1 else (plural_form or singular + 's')}"


def per_week(hours: int) -> int:
    return round(hours / WEEKS_PER_MONTH)


# --------------------------------------------------------------------------- syllabus
def _spread(tasks: list[Task], weights: list[float]) -> list[list[Task]]:
    """Split tasks, in order, over the weeks so each week carries a similar amount of work."""
    total = sum(weights) or 1.0
    weeks: list[list[Task]] = [[] for _ in range(WEEKS)]
    done = 0.0
    for task, w in zip(tasks, weights):
        mid = (done + w / 2) / total
        weeks[min(WEEKS - 1, int(mid * WEEKS))].append(task)
        done += w
    return weeks


def revision_skills(rm: Roadmap, month: int) -> list[str]:
    """Skills worth revising in an unscheduled month: what was unlocked earlier, else what the student knows."""
    earlier = [it.skill.skill_id for m in rm.months if m.month < month for it in m.items]
    ids = list(dict.fromkeys(earlier)) or sorted(rm.data.student_skills)
    return ids[-3:]


def revision_plan(rm: Roadmap, month: PlanMonth) -> list[list[Task]]:
    """A month with no scheduled activity is a revision and career-preparation month, with real tasks.

    Several such months differ from each other: each one revises other key points and focuses on a
    different career theme (portfolio, interviews, growth).
    """
    nth = sum(1 for m in rm.months if m.month < month.month and not m.items)   # 0 for the first one
    skills = [rm.data.skills[s] for s in revision_skills(rm, month.month)]
    k = f"m{month.month}-rev"
    names = ", ".join(s.name for s in skills) or "your skills"
    tasks: list[Task] = []
    for s in skills:
        n = len(s.topics)
        picked = [s.topics[(3 * nth + i) % n] for i in range(min(3, n))]
        tasks.append(Task("revise", f"Revise {s.name}: redo one exercise on each of {', '.join(picked)}", f"{k}-{s.skill_id}"))
    themes = [
        [("github", "Pin your three best repositories on GitHub and give each a clear README"),
         ("post", f"Write a short post or notes page explaining something you built with {names}"),
         ("cv", f"Update your CV: add the projects and skills you gained ({names})")],
        [("questions", f"Answer 5 interview questions out loud on {names}"),
         ("explain", "Explain your best project to a friend in 3 minutes: problem, approach, result"),
         ("mock", "Do a mock interview or a pair-programming session with a friend")],
        [("oss", "Find a beginner-friendly open-source issue in a project you use and read its contribution guide"),
         ("linkedin", "Update your LinkedIn profile with your skills and one project link"),
         ("plan", "Write down the next skill you want to deepen and one measurable goal for it")],
    ]
    for key, text in themes[nth % len(themes)]:
        tasks.append(Task("career", text, f"{k}-{key}"))
    tasks.append(Task("career", "Review the month: list what you finished and what to repeat", f"{k}-review"))
    return _spread(tasks, [1.0] * len(tasks))


def weekly_plan(month: PlanMonth, rm: Roadmap | None = None) -> list[list[Task]]:
    """The month's syllabus split over its weeks, specific to each course, project or internship.

    For each activity in order: study its learning resources first, then work through the modules of
    that activity, then hand in its deliverable. A month with no activity gets a revision plan.
    """
    if not month.items:
        return revision_plan(rm, month) if rm is not None else [[] for _ in range(WEEKS)]
    tasks: list[Task] = []
    weights: list[float] = []
    for it in month.items:
        x, k = it.activity, f"m{month.month}-{it.activity.activity_id}"
        mine: list[Task] = []
        for r in it.prep:
            provider = f", {r.provider}" if r.provider else ""
            mine.append(Task("study", f"Study first: {r.name} ({r.hours} h{provider})", f"{k}-r-{r.resource_id}"))
        for i, module in enumerate(x.syllabus):
            mine.append(Task("learn", f"{x.name}, module {i + 1}: {module}", f"{k}-m-{i}"))
        mine.append(Task("build", f"Hand in: {x.deliverable or x.name}", f"{k}-b"))
        tasks += mine
        weights += [x.hours / len(mine)] * len(mine)
    return _spread(tasks, weights)


def revision_summary(rm: Roadmap, month: PlanMonth) -> str:
    names = ", ".join(rm.data.skills[s].name for s in revision_skills(rm, month.month)) or "your skills"
    return (f"No new course fits this month, so its {month.budget} hours go to revision and career "
            f"preparation: lock in {names}, show your work, and practise interviews.")


# --------------------------------------------------------------------------- summaries
def excluded_lines(rm: Roadmap) -> list[tuple[object, str]]:
    """(activity, reason) for every activity that is not in the plan."""
    b, sk = rm.part_b, rm.data.skills
    out = []
    for a in b.already_known:
        out.append((a, f"you already know {sk[a.skill_unlocked].name}"))
    for a in b.ineligible:
        out.append((a, f"{sk[a.skill_unlocked].name} is unreachable from your skills"))
    for a in b.oversized:
        out.append((a, f"needs {a.hours} h, more than any single month ({max(b.budgets.values())} h)"))
    for a in b.unscheduled:
        out.append((a, f"eligible, but did not fit in the best plan ({a.hours} h)"))
    return out


def summary_lines(rm: Roadmap) -> list[str]:
    a, b = rm.part_a, rm.part_b
    used, budget = sum(b.hours_used.values()), sum(b.budgets.values())
    count = sum(len(m.items) for m in rm.months)
    unlocked = {i.activity.skill_unlocked for m in rm.months for i in m.items}
    prep = sum(m.prep_hours for m in rm.months)
    return [
        f"TOTAL CAREER VALUE : {b.total_value}  ({plural(count, 'activity', 'activities')})",
        f"Hours scheduled    : {used}/{budget}  (+{prep} h of study-first resources)",
        f"Skills unlocked    : {skill_names(rm, unlocked)}",
        f"Learning path      : {a.total_hours} h across {plural(len(a.chosen_resources), 'resource')} (minimum spanning tree)",
        f"Unreachable skills : {len(a.unreachable_skills)} ({skill_names(rm, a.unreachable_skills)})",
    ]


def format_roadmap(rm: Roadmap) -> str:
    data, a = rm.data, rm.part_a
    line, thin = "=" * WIDTH, "-" * WIDTH

    def field(label: str, text: str, indent: int = 6) -> list[str]:
        pad = " " * indent
        return textwrap.wrap(f"{label:<12}: {text}", WIDTH, initial_indent=pad,
                             subsequent_indent=pad + " " * 14)

    out = [line, "CAREER ROADMAP", line, f"You already know: {skill_names(rm, data.student_skills)}", ""]
    out += summary_lines(rm) + [""]

    out += ["MONTH-BY-MONTH PLAN  (Part B: Multiple 0/1 Knapsack, foundations first)", thin]
    for m in rm.months:
        head = f"Month {m.month}   {m.hours_used}/{m.budget} h"
        if m.items:
            head += f"   (about {per_week(m.hours_used)} h/week)"
        out.append(head)
        if not m.items:
            out += textwrap.wrap(revision_summary(rm, m), WIDTH, initial_indent="   ", subsequent_indent="   ")
        for it in m.items:
            x = it.activity
            out.append(f"   [{x.type}] {x.activity_id}  {x.name}  -  {x.hours} h, value {x.career_value}")
            out += field("Unlocks", f"{it.skill.name} ({it.skill.level_name}, {it.skill.category})")
            if x.deliverable:
                out += field("Deliverable", x.deliverable)
            if it.skill.tip:
                out += field("Tip", it.skill.tip)
        out.append("   Syllabus")
        for w, tasks in enumerate(weekly_plan(m, rm), 1):
            if tasks:
                out.append(f"      Week {w}")
                for task in tasks:
                    out += textwrap.wrap(task.text, WIDTH, initial_indent="        - ", subsequent_indent="          ")
        out.append("")

    out += ["LEARNING PATH  (Part A: Greedy, Kruskal minimum spanning tree)", thin]
    for r in a.chosen_resources:
        out.append(f"  {r.resource_id}  {r.name:<38} {data.skills[r.skill_a].name} <-> {data.skills[r.skill_b].name}  {r.hours} h")
    out.append(f"  Total learning hours: {a.total_hours}")
    out.append(f"  Reachable skills ({len(a.reachable_skills)}): {skill_names(rm, a.reachable_skills)}")
    if a.skipped_unavailable:
        out.append("  Unavailable resources (never used): " + ", ".join(r.resource_id for r in a.skipped_unavailable))
    if rm.extra_resources:
        out.append("  On the path but not needed by a scheduled activity: "
                   + ", ".join(r.resource_id for r in rm.extra_resources))
    out.append("")

    ex = excluded_lines(rm)
    out += ["EXCLUDED ACTIVITIES", thin]
    out += [f"  {x.activity_id} {x.name}: {why}" for x, why in ex] if ex else ["  none"]
    out += ["", line]
    return "\n".join(out)
