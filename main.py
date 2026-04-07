#!/usr/bin/env python3
"""
PawPal+ CLI Demo -- Phase 3
Demonstrates: HH:MM time sorting, pet/status filtering,
recurring task auto-scheduling, and conflict detection.
"""

from datetime import datetime
from pawpal_system import Owner, Pet, Task, Scheduler

TODAY = datetime.now().strftime("%Y-%m-%d")
SEP = "=" * 60


def print_task(idx: int, task: Task) -> None:
    time_label = f" @ {task.time}" if task.time else ""
    print(f"  {idx}. [{task.time_preference.capitalize()}{time_label}] "
          f"{task.description} -- {task.pet.name} "
          f"(P{task.get_priority()}, {task.get_duration()} min)")


def main():
    # ------------------------------------------------------------------ #
    # Setup                                                                #
    # ------------------------------------------------------------------ #
    owner = Owner(
        name="Alice",
        preferences={"available_time": 240, "preferred_times": ["morning", "evening"]}
    )

    buddy = Pet(name="Buddy", species="Dog", age=3, special_needs=["high energy"], tasks=[])
    whiskers = Pet(name="Whiskers", species="Cat", age=5, special_needs=["indoor only"], tasks=[])
    owner.add_pet(buddy)
    owner.add_pet(whiskers)

    # Tasks added OUT OF ORDER on purpose to prove sorting works
    buddy.add_task(Task(
        description="Evening walk",
        duration=30, priority=5,
        time_preference="evening", time="18:00",
        recurring="daily", pet=buddy
    ))
    buddy.add_task(Task(
        description="Play fetch",
        duration=20, priority=3,
        time_preference="morning", time="09:30",
        recurring="daily", pet=buddy
    ))
    buddy.add_task(Task(
        description="Morning walk",
        duration=30, priority=5,
        time_preference="morning", time="07:00",
        recurring="daily", pet=buddy
    ))
    whiskers.add_task(Task(
        description="Feed Whiskers",
        duration=10, priority=4,
        time_preference="morning", time="08:00",
        recurring="daily", pet=whiskers
    ))
    whiskers.add_task(Task(
        description="Change litter box",
        duration=15, priority=3,
        time_preference="afternoon", time="13:00",
        recurring="daily", pet=whiskers
    ))
    whiskers.add_task(Task(
        description="Brush coat",
        duration=10, priority=2,
        time_preference="evening",
        recurring="weekly",
        start_date="2026-04-07",
        pet=whiskers
    ))

    scheduler = Scheduler(owner)

    # ------------------------------------------------------------------ #
    # Step 2a -- Sort by HH:MM time                                       #
    # ------------------------------------------------------------------ #
    print(SEP)
    print(f"  PawPal+ Demo -- {TODAY}")
    print(SEP)

    all_tasks = owner.get_all_tasks()
    sorted_by_time = scheduler.sort_by_time(all_tasks)

    print("\n[SORT] All tasks ordered by time (HH:MM):\n")
    for i, t in enumerate(sorted_by_time, 1):
        print_task(i, t)

    # ------------------------------------------------------------------ #
    # Step 2b -- Filter by pet name and by status                         #
    # ------------------------------------------------------------------ #
    print("\n[FILTER] Buddy's tasks only:\n")
    for i, t in enumerate(scheduler.filter_tasks(pet_name="Buddy"), 1):
        print_task(i, t)

    print("\n[FILTER] Pending (incomplete) tasks:\n")
    for i, t in enumerate(scheduler.filter_tasks(completed=False), 1):
        print_task(i, t)

    # ------------------------------------------------------------------ #
    # Step 2c -- Daily schedule (sorted + conflict-checked)               #
    # ------------------------------------------------------------------ #
    print(f"\n[SCHEDULE] Today's plan ({TODAY}):\n")
    daily_plan = scheduler.generate_daily_plan(TODAY)
    total = sum(t.get_duration() for t in daily_plan)
    for i, t in enumerate(daily_plan, 1):
        print_task(i, t)
    print(f"\n  Total time: {total} minutes")

    # ------------------------------------------------------------------ #
    # Step 3 -- Mark complete -> auto-schedule next occurrence            #
    # ------------------------------------------------------------------ #
    morning_walk = next(t for t in buddy.get_tasks() if t.description == "Morning walk")

    print(f"\n[RECURRING] Completing '{morning_walk.description}' on {TODAY}...")
    next_task = scheduler.mark_task_complete(morning_walk, TODAY)

    print(f"  Marked complete: {morning_walk.description} (completed={morning_walk.completed})")
    if next_task:
        print(f"  Auto-created next: '{next_task.description}' due {next_task.due_date}")

    print("\n[FILTER] Completed tasks:\n")
    for i, t in enumerate(scheduler.filter_tasks(completed=True), 1):
        print(f"  {i}. {t.description} ({t.pet.name}) [completed]")

    print("\n[FILTER] Pending tasks (next occurrence visible):\n")
    for i, t in enumerate(scheduler.filter_tasks(completed=False), 1):
        due = f" [due {t.due_date}]" if t.due_date else ""
        print(f"  {i}. {t.description} ({t.pet.name}){due}")

    # ------------------------------------------------------------------ #
    # Step 4 -- Conflict detection                                        #
    # Two tasks deliberately share the same time slot to trigger a warning#
    # ------------------------------------------------------------------ #
    print(f"\n[CONFLICT TEST] Adding two tasks at 08:00...\n")

    # Buddy gets a grooming task at 08:00 -- same time as Whiskers' feeding
    buddy.add_task(Task(
        description="Groom Buddy",
        duration=15, priority=3,
        time_preference="morning", time="08:00",
        recurring="daily", pet=buddy
    ))

    active_tasks = scheduler.filter_tasks(completed=False)
    conflicts = scheduler.detect_conflicts(active_tasks)

    if conflicts:
        for msg in conflicts:
            print(f"  {msg}")
    else:
        print("  No conflicts found.")

    print(f"\n{SEP}\n")


if __name__ == "__main__":
    main()
