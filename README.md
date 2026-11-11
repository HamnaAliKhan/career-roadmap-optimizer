# Career Roadmap Optimization System

CT-363 Design and Analysis of Algorithms — Complex Engineering Problem, NED University.

From one skill-and-resource dataset the system decides:

| Part | Paradigm | Algorithm | What it decides | File |
|------|----------|-----------|-----------------|------|
| A | Greedy | Kruskal's MST + Union-Find | Cheapest set of learning resources connecting the student's current skills to every reachable skill | `src/roadmap/part_a_kruskal.py` |
| B | Dynamic Programming | Multiple 0/1 Knapsack | Which activity goes in which month, within each month's hours, for the highest career value | `src/roadmap/part_b_knapsack.py` |
| C | Integration | A → B pipeline | Skills reachable in A decide which activities B may schedule | `src/roadmap/pipeline.py` |

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
```

## Run

```bash
python main.py                          # roadmap for data/student.csv
python main.py --skills S01,S05         # roadmap for a different student
python main.py --unavailable R11,R12    # recompute when resources become unavailable
python main.py --trace                  # also print Kruskal's step-by-step decisions
python main.py --tests                  # print the test scenarios with their output
streamlit run app.py                    # web interface
pytest                                  # unit tests
```

## Dataset (`data/`)

| File | Rows | Columns |
|------|------|---------|
| `skills.csv` | 20 | skill_id, name, relevance (1–10), demand (1–10) |
| `resources.csv` | 30 | resource_id, name, skill_a, skill_b, hours, unavailable (0/1) |
| `activities.csv` | 15 | activity_id, name, type, hours, career_value, skill_unlocked |
| `months.csv` | 6 | month, hour_budget (all different) |
| `student.csv` | — | skill_id (the student's current skills) |

Built-in test cases: Embedded C / VHDL are disconnected (R29 unavailable), R21/R23 tie at 6 h,
A11 (80 h) exceeds every month, and eligible activities need 380 h against 280 h of budget.

## Constraints implemented

- Each month's activities stay within that month's hours.
- Each activity is scheduled in at most one month.
- Unavailable resources are never used.
- An activity is allowed only if its skill is reachable from the student's current skills.
- An activity longer than every month's limit is excluded and reported.
- Equal-hour resources: the one linking higher-relevance skills is chosen (sum of both skills'
  relevance). If relevance is also equal, the one linking higher-demand skills wins.

## Complexity

- **Part A:** O(E log E) — sorting the edges dominates; Union-Find with path compression and union by rank is near O(1) per operation.
- **Part B:** O(n · S · m), where n = activities, m = months, S = distinct remaining-hours states (at most ∏(budgetₘ + 1)). Pseudo-polynomial, like 0/1 knapsack. Storing states sorted, and zeroing capacity too small for any remaining activity, keeps S small (≈27,000 states for this dataset).

## Team

Hamna Ali Khan (Lead) · Amna Mohsin · Tayyaba Ahmed · Javeria Irfan Ali
