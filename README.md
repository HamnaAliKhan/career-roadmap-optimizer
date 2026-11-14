<div align="center">

# Career Roadmap Optimization System

### A six-month, skills-based learning roadmap

A Python and Streamlit decision-support system for finding cost-effective learning
resources and scheduling courses, projects, and internships within monthly hour budgets.
The system recommends a plan; students choose what to pursue.

[About](#about) · [Features](#features) · [Setup](#getting-started) ·
[How it works](#algorithm-methodology) · [Tests](#tests) · [License](#license)

</div>

## About

The **Career Roadmap Optimization System** is an educational project for
**CT-363 Design and Analysis of Algorithms**, a Complex Engineering Problem (CEP)
at the Department of Computer Science and Information Technology, NED University of
Engineering and Technology.

Given a student's existing skills, learning-resource connections, and monthly
availability, it builds a month-by-month plan. It first finds a low-hour set of
resources connecting the student's skills to reachable skills, then schedules eligible
activities to maximize career value without exceeding any month's budget.

The supplied dataset and student profiles are project examples. The roadmap is an
algorithmic recommendation, not a guarantee of employment or professional career advice.

## Features

- **Interactive Streamlit app:** edit a student profile, select unavailable resources,
  and explore the recomputed plan.
- **Command-line interface:** print a roadmap, list skills and resources, run scenarios,
  or inspect Kruskal's decisions.
- **Kruskal minimum spanning tree:** chooses available skill-to-skill resources by hours,
  with deterministic relevance and demand tie-breakers.
- **Multiple 0/1 knapsack:** assigns eligible activities across months to maximize total
  career value while respecting each monthly budget and scheduling each activity at most once.
- **Foundations-first sequencing:** arranges the selected activities around skill depth
  and learning prerequisites without changing the selected set or its value.
- **Explainable results:** reports reachable and unreachable skills, selected learning
  resources, hours, total career value, and excluded activities with reasons.
- **Live resource-availability updates:** marking a resource unavailable recomputes the
  reachable skills, learning path, and activity schedule.
- **Ready-made student profiles:** try different starting skills without editing CSVs.
- **Built-in scenarios and tests:** cover disconnected skills, hour over-demand, oversized
  activities, and unavailable resources.

## Tech stack

Python · Streamlit · pytest · CSV

## Algorithm methodology

```text
Student skills + CSV dataset
             │
             ▼
 Available resources form a graph of skills
             │
             ▼
 Part A: Kruskal MST + Union-Find
             │
             ▼
 Reachable skills and minimum-hour resource tree
             │
             ▼
 Part B: Multiple 0/1 Knapsack
             │
             ▼
 Highest-value activities within each month's budget
             │
             ▼
 Foundations-first roadmap 
```

### Part A — Greedy minimum spanning tree

Skills are graph nodes and learning resources are weighted edges, with resource hours
as the weight. Resources marked unavailable are removed from the graph. Kruskal's
algorithm processes the remaining edges from least to most hours, using combined skill
relevance, combined demand, and resource ID to break ties. Union-Find detects cycles.
The connected component containing the student's known skills determines reachability.

### Part B — Dynamic programming multiple knapsack

Each activity is an item with hours as its weight and career value as its value. Each
month is a separate knapsack with its own hour capacity. A memoized dynamic program
chooses the highest-value combination while ensuring an activity is placed in no more
than one month. Activities tied to unreachable skills, already-known skills, or hours
greater than every monthly budget are excluded and reported.

### Part C — Integrated roadmap

Part A's reachable skills determine which activities Part B may schedule. The pipeline
adds the study-first resources for each activity, then orders the chosen activities so
foundations and prerequisites come first while preserving monthly budgets and total
career value.

## Getting started

### Requirements

- Python 3.10 or later
- The packages listed in `requirements.txt`

### Install

Create and activate a virtual environment from the project root.

**Windows (PowerShell)**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Run the Streamlit app

```bash
streamlit run app.py
```

Open the local address printed in the terminal. Choose a starting profile or select
skills in the sidebar. You can also mark additional resources unavailable to recalculate
the plan.

### Run the command-line interface

```bash
python main.py                         # use data/student.csv
python main.py --skills python,git     # override starting skills
python main.py --unavailable R11,R12  # disable resources and recompute
python main.py --trace                 # include Kruskal's edge trace
python main.py --tests                 # run proposal scenarios
python main.py --list-skills
python main.py --list-resources
```

Skill input accepts skill IDs or unambiguous names. For example, `S01,S02` or
`python,git`.

## Dataset

The default dataset is in `data/`:

| File | Records | Purpose |
|---|---:|---|
| `skills.csv` | 20 | Skill names, categories, levels, relevance, demand, topics, and tips |
| `resources.csv` | 30 | Learning resources linking skills, with hours and availability |
| `activities.csv` | 15 | Courses, projects, and internships with hours, value, and unlocked skill |
| `months.csv` | 6 | Distinct monthly hour budgets: 40, 55, 30, 60, 45, and 50 |
| `student.csv` | — | Default starting skills: Python, Git & GitHub, and SQL |
| `students/*.csv` | 8 | Ready-made starting-skill profiles |

Optional descriptive columns (such as topics, tips, providers, and deliverables) have
defaults when omitted. To add a profile, add a CSV containing a `skill_id` column in
`data/students/`.

## Tests

Run the unit-test suite:

```bash
python -m pytest -q
```

Run the proposal scenarios and see their checks:

```bash
python main.py --tests
```

The scenarios check that unreachable skills and their activities are reported, monthly
budgets and one-activity/one-month scheduling are respected under demand, oversized
activities are excluded, and disabling resources triggers a valid recomputation.

## Project structure

```text
app.py                       Streamlit application
main.py                      Command-line interface
requirements.txt             Python dependencies
data/                        Dataset and student profiles
src/roadmap/
  data_loader.py             CSV loading, parsing, and validation
  models.py                  Shared data models
  part_a_kruskal.py          Part A: Kruskal and Union-Find
  part_b_knapsack.py         Part B: multiple knapsack dynamic programming
  pipeline.py                Part C: integrate graph and scheduling results
  sequencing.py              Foundations-first activity ordering
  report.py                  Roadmap summaries and syllabus helpers
  scenarios.py               Proposal scenario checks
  ui_theme.py                Streamlit theme and component styles
tests/                       Unit tests for loading, algorithms, and pipeline
```

## Team

- **Hamna Ali Khan** · [GitHub](https://github.com/HamnaAliKhan)
- **Amna Mohsin** · [GitHub](https://github.com/amna-mohsin)
- **Tayyaba Ahmed** · [GitHub](https://github.com/tayyaba-ahmed)
- **Javeria Irfan Ali** · [GitHub](https://github.com/javeriairfanali)

## License

This project is licensed under the MIT License. See [`LICENSE`](LICENSE) for details.
The license applies to project-authored materials; third-party dependencies remain
subject to their respective licenses.

## Academic use

Developed for educational use as a CT-363 Complex Engineering Problem. If you reuse
or adapt the project, credit the team and follow your institution's academic-integrity
requirements.
