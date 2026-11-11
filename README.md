# Career Roadmap Optimization System

CT-363 Design and Analysis of Algorithms — Complex Engineering Problem (NED University).

Two coupled decisions from one skill-and-resource dataset:

| Part | Paradigm | Algorithm | File |
|------|----------|-----------|------|
| A | Greedy | Kruskal's MST (Union-Find) | `src/roadmap/part_a_kruskal.py` |
| B | Dynamic Programming | Multiple 0/1 Knapsack | `src/roadmap/part_b_knapsack.py` |
| C | Integration | A → B pipeline | `src/roadmap/pipeline.py` |

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

## Run

```bash
python main.py                         # full roadmap
python main.py --unavailable R01,R05   # recompute with resources disabled
pytest                                 # tests
```

## Data (`data/`)

| File | Columns |
|------|---------|
| `skills.csv` | skill_id, name, relevance (1–10), demand (1–10) |
| `resources.csv` | resource_id, name, skill_a, skill_b, hours, unavailable (0/1) |
| `activities.csv` | activity_id, name, type (course/project/internship), hours, career_value, skill_unlocked |
| `months.csv` | month, hour_budget |
| `student.csv` | skill_id (the student's current skills) |

Target size: 20 skills, 30 resources, 15 activities, 6 months.

## Team

Hamna Ali Khan (Lead) · Amna Mohsin · Tayyaba Ahmed · Javeria Irfan Ali
