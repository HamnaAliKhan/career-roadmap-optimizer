"""Builders for small hand-made datasets used in the tests."""
from roadmap.models import Activity, Dataset, Month, Resource, Skill


def skill(sid, relevance=5, demand=5):
    return Skill(sid, sid, relevance, demand)


def res(rid, a, b, hours, unavailable=False):
    return Resource(rid, rid, a, b, hours, unavailable)


def act(aid, hours, value, sid):
    return Activity(aid, aid, "course", hours, value, sid)


def dataset(skills, resources=(), activities=(), budgets=(10,), student=("A",)):
    return Dataset(
        skills={s.skill_id: s for s in skills},
        resources=list(resources),
        activities=list(activities),
        months=[Month(i + 1, b) for i, b in enumerate(budgets)],
        student_skills=set(student),
    )
