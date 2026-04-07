# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## Features

PawPal+ includes intelligent scheduling algorithms that go beyond simple task lists:

- **Smart Time Sorting**: Tasks are automatically ordered by specific times (HH:MM), then by time preference slots (morning → afternoon → evening), with priority as tiebreaker
- **Conflict Detection**: Identifies and warns about tasks scheduled at the exact same time
- **Capacity Management**: Respects daily time budgets and time slot limits (morning: 180min, afternoon: 120min, evening: 180min)
- **Recurring Task Auto-Scheduling**: Daily and weekly tasks automatically create their next occurrence when completed
- **Multi-Pet Support**: Manage care schedules for multiple pets simultaneously
- **Priority-Based Planning**: High-priority tasks are scheduled first within their time constraints

## 📸 Demo

<a href="/course_images/ai110/pawpal_demo.png" target="_blank"><img src='/course_images/ai110/pawpal_demo.png' title='PawPal+ App Demo' width='' alt='PawPal+ App Demo' class='center-block' /></a>

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

The scheduler goes beyond a simple priority sort.  Four algorithms work together
to build a realistic daily plan:

| Feature | Method | Description |
|---|---|---|
| **Time sorting** | `Scheduler.sort_by_time()` | Orders tasks by their explicit HH:MM `time` field, then by broad slot (morning → afternoon → evening), then by priority descending as a tiebreaker. Tasks added in any order come out chronologically correct. |
| **Filtering** | `Scheduler.filter_tasks()` | Returns tasks matching a pet name, completion status, or both. Useful for "show me only Buddy's pending tasks". |
| **Conflict detection** | `Scheduler.detect_conflicts()` | Groups tasks by their HH:MM time and returns a warning string for every group with more than one task. The scheduler keeps running — warnings are surfaced to the caller rather than raising an exception. |
| **Recurring auto-scheduling** | `Scheduler.mark_task_complete()` | When a recurring task is marked done, a new Task is automatically created with a `due_date` of today + 1 day (daily) or today + 7 days (weekly), using Python's `timedelta`. The original task is kept for history. |

### Example

```python
scheduler = Scheduler(owner)
plan = scheduler.generate_daily_plan("2026-04-07")

# surface any time clashes before showing the plan
for warning in scheduler.detect_conflicts(plan):
    print(warning)

# complete a task and auto-schedule its next occurrence
next_task = scheduler.mark_task_complete(plan[0], "2026-04-07")
print(f"Next: {next_task.description} due {next_task.due_date}")
```

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Testing PawPal+

Run the automated test suite using:
```bash
python -m pytest
```

The test suite covers:
- Task completion and addition to pets
- Daily plan generation with priority sorting
- Time-based sorting (chronological order with priority tiebreakers)
- Recurrence logic for daily and weekly tasks
- Conflict detection for overlapping task times
- Conflict resolution based on slot capacities and daily time budgets
- Edge cases like pets with no tasks

**Confidence Level**: ⭐⭐⭐⭐⭐ (5/5 stars) - All core scheduling behaviors are thoroughly tested with both happy paths and edge cases. The system reliably handles task sorting, recurrence, and conflict resolution.
