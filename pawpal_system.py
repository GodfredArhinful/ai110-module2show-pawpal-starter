from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict

# Time slot ordering: morning first, then afternoon, then evening
SLOT_ORDER = {"morning": 0, "afternoon": 1, "evening": 2}

# Available minutes per time slot
SLOT_CAPACITY = {"morning": 180, "afternoon": 120, "evening": 180}


@dataclass
class Task:
    """
    Represents a single pet care task.

    Attributes:
        description:     Human-readable label for the task.
        duration:        How long the task takes, in minutes.
        priority:        Importance level from 1 (low) to 5 (high).
        time_preference: Broad time of day: 'morning', 'afternoon', or 'evening'.
        recurring:       Repeat cadence: 'daily' or 'weekly'.
        pet:             The Pet this task belongs to.
        completed:       True once the task has been performed.
        skipped:         True when conflict resolution dropped the task from a plan.
        start_date:      ISO date string; weekly tasks repeat on this weekday.
        due_date:        Explicit next due date (ISO format); overrides recurring logic.
        time:            Specific clock time within the day, e.g. "08:30" (HH:MM).
    """

    description: str
    duration: int
    priority: int
    time_preference: str
    recurring: str
    pet: 'Pet'
    completed: bool = False
    skipped: bool = False
    start_date: Optional[str] = None
    due_date: Optional[str] = None
    time: Optional[str] = None

    def is_due(self, date: str) -> bool:
        """
        Return True if this task should appear in the plan for the given date.

        If ``due_date`` is set the task is due only on that exact date.
        Otherwise the recurring pattern is used: daily tasks are always due;
        weekly tasks fire on the same weekday as ``start_date`` (Monday if
        ``start_date`` is not set).
        """
        if self.due_date:
            return self.due_date == date
        if self.recurring == 'daily':
            return True
        if self.recurring == 'weekly':
            check_day = datetime.fromisoformat(date).weekday()
            if self.start_date:
                origin_day = datetime.fromisoformat(self.start_date).weekday()
                return check_day == origin_day
            return check_day == 0  # fallback: Mondays
        return False

    def get_duration(self) -> int:
        """Return the task duration in minutes."""
        return self.duration

    def get_priority(self) -> int:
        """Return the task priority level (1–5)."""
        return self.priority

    def mark_complete(self) -> None:
        """Mark the task as completed."""
        self.completed = True


@dataclass
class Pet:
    """
    Represents a pet owned by an Owner.

    Attributes:
        name:          The pet's name.
        species:       Species string, e.g. 'Dog', 'Cat'.
        age:           Age in years.
        special_needs: Free-text list of care notes.
        tasks:         All Task objects associated with this pet.
    """

    name: str
    species: str
    age: int
    special_needs: List[str]
    tasks: List[Task]

    def add_task(self, task: Task) -> None:
        """Append a task and point task.pet back to this Pet."""
        self.tasks.append(task)
        task.pet = self

    def get_tasks(self) -> List[Task]:
        """Return all tasks associated with this pet."""
        return self.tasks

    def get_info(self) -> Dict:
        """Return a plain dict summary of the pet's attributes."""
        return {
            'name': self.name,
            'species': self.species,
            'age': self.age,
            'special_needs': self.special_needs,
        }


class Owner:
    """
    Represents the pet owner and acts as the top-level data container.

    Attributes:
        name:        Owner's display name.
        preferences: Dict of scheduling preferences, e.g.
                     ``{"available_time": 120}``.
        pets:        All Pet objects belonging to this owner.
    """

    def __init__(self, name: str, preferences: Dict):
        self.name = name
        self.preferences = preferences
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's collection."""
        self.pets.append(pet)

    def get_pets(self) -> List[Pet]:
        """Return all pets owned by this owner."""
        return self.pets

    def update_preferences(self, prefs: Dict) -> None:
        """Merge *prefs* into the owner's existing preferences."""
        self.preferences.update(prefs)

    def get_all_tasks(self) -> List[Task]:
        """Return a flat list of every task across all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def get_tasks_for_pet(self, pet_name: str) -> List[Task]:
        """Return all tasks for a named pet (case-insensitive). Empty list if not found."""
        for pet in self.pets:
            if pet.name.lower() == pet_name.lower():
                return pet.get_tasks()
        return []

    def get_tasks_by_status(self, completed: bool) -> List[Task]:
        """Return all tasks whose ``completed`` field matches *completed*."""
        return [t for t in self.get_all_tasks() if t.completed == completed]


class Scheduler:
    """
    Generates and manages the daily task plan for an Owner.

    Responsibilities:
      - Collect due tasks from all pets.
      - Sort them by clock time, then slot, then priority.
      - Detect time conflicts and surface human-readable warnings.
      - Enforce per-slot and daily time budgets (conflict resolution).
      - Auto-schedule the next occurrence when a recurring task is completed.
    """

    def __init__(self, owner: Owner):
        self.owner = owner

    def generate_daily_plan(self, date: str) -> List[Task]:
        """
        Build a sorted, conflict-resolved task list for *date*.

        Steps:
          1. Collect all tasks that are due and not yet completed.
          2. Sort by HH:MM time, then slot, then priority.
          3. Drop tasks that exceed the daily budget or slot capacity.

        Returns the accepted task list. Call :meth:`detect_conflicts` separately
        to retrieve any time-clash warnings.
        """
        all_tasks = self.owner.get_all_tasks()
        due_tasks = [t for t in all_tasks if t.is_due(date) and not t.completed]
        sorted_tasks = self.sort_by_time(due_tasks)
        return self.resolve_conflicts(sorted_tasks)

    # ------------------------------------------------------------------
    # Sorting
    # ------------------------------------------------------------------

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """
        Sort *tasks* chronologically using the HH:MM ``time`` field as the
        primary key and priority (descending) as the tiebreaker.

        Tasks without an explicit ``time`` are placed after timed tasks in
        the same broad slot by using a large slot-based offset (slot index
        multiplied by 10 000 minutes).

        This two-branch approach was chosen over a single-expression lambda
        because the explicit ``if`` makes the fallback logic readable at a
        glance, even though a lambda would be marginally shorter.
        """
        def sort_key(t: Task):
            if t.time:
                h, m = map(int, t.time.split(":"))
                return (h * 60 + m, -t.get_priority())
            return (SLOT_ORDER.get(t.time_preference, 99) * 10_000, -t.get_priority())

        return sorted(tasks, key=sort_key)

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> List[Task]:
        """
        Return tasks matching the supplied filters.

        Args:
            pet_name:  Case-insensitive pet name. ``None`` includes all pets.
            completed: ``True``/``False`` to filter by status. ``None`` includes both.

        Returns:
            A list of matching Task objects (may be empty).
        """
        tasks = self.owner.get_all_tasks()
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet.name.lower() == pet_name.lower()]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks

    # ------------------------------------------------------------------
    # Step 4: Conflict detection
    # ------------------------------------------------------------------

    def detect_conflicts(self, tasks: List[Task]) -> List[str]:
        """
        Identify tasks that share an exact HH:MM ``time`` value.

        This is a lightweight, non-crashing strategy: it groups tasks by
        their clock time and returns a warning string for every group that
        contains more than one task.  The scheduler continues normally;
        it is the caller's responsibility to display the warnings.

        Args:
            tasks: The task list to inspect (typically the output of
                   :meth:`generate_daily_plan` or :meth:`filter_tasks`).

        Returns:
            A list of warning strings, one per conflicting time slot.
            Empty list means no conflicts were found.

        Note:
            Only tasks with an explicit ``time`` field are checked.
            Tasks that share only a ``time_preference`` slot (e.g. two
            "morning" tasks without a specific clock time) are not flagged
            here; their capacity is managed by :meth:`resolve_conflicts`.
        """
        timed: Dict[str, List[Task]] = defaultdict(list)
        for task in tasks:
            if task.time:
                timed[task.time].append(task)

        warnings = []
        for time_str, group in timed.items():
            if len(group) > 1:
                details = ", ".join(
                    f"'{t.description}' ({t.pet.name})" for t in group
                )
                warnings.append(f"WARNING: conflict at {time_str} -- {details}")
        return warnings

    # ------------------------------------------------------------------
    # Step 3: Recurring task auto-scheduling
    # ------------------------------------------------------------------

    def mark_task_complete(self, task: Task, date: str) -> Optional[Task]:
        """
        Mark *task* complete and create its next occurrence using ``timedelta``.

        Recurrence rules:
          - ``'daily'``  → next ``due_date`` = *date* + 1 day
          - ``'weekly'`` → next ``due_date`` = *date* + 7 days
          - any other    → marks complete, returns ``None``

        The new Task is added directly to the same pet so it appears in
        future calls to :meth:`generate_daily_plan`.

        Args:
            task: The task to complete.
            date: The ISO date string on which the task was performed.

        Returns:
            The newly created Task for the next occurrence, or ``None`` for
            non-recurring tasks.
        """
        task.mark_complete()

        if task.recurring == 'daily':
            delta = timedelta(days=1)
        elif task.recurring == 'weekly':
            delta = timedelta(weeks=1)
        else:
            return None

        next_date = (datetime.fromisoformat(date) + delta).strftime("%Y-%m-%d")

        next_task = Task(
            description=task.description,
            duration=task.duration,
            priority=task.priority,
            time_preference=task.time_preference,
            recurring=task.recurring,
            pet=task.pet,
            completed=False,
            skipped=False,
            start_date=task.start_date,
            due_date=next_date,
            time=task.time,
        )
        task.pet.add_task(next_task)
        return next_task

    # ------------------------------------------------------------------
    # Conflict resolution: enforce slot capacity and daily time budget
    # ------------------------------------------------------------------

    def resolve_conflicts(self, tasks: List[Task]) -> List[Task]:
        """
        Accept tasks that fit within the owner's ``available_time`` budget
        and each slot's minute capacity.  Tasks that would overflow either
        limit are marked ``skipped=True`` and excluded from the result.

        Args:
            tasks: Pre-sorted task list (output of :meth:`sort_by_time`).

        Returns:
            The subset of tasks that fit within all constraints.
        """
        available_time = self.owner.preferences.get("available_time", float("inf"))
        slot_used: Dict[str, int] = {slot: 0 for slot in SLOT_CAPACITY}
        total_used = 0
        accepted: List[Task] = []

        for task in tasks:
            slot = task.time_preference
            slot_remaining = SLOT_CAPACITY.get(slot, 0) - slot_used.get(slot, 0)
            budget_remaining = available_time - total_used

            if task.get_duration() <= slot_remaining and task.get_duration() <= budget_remaining:
                slot_used[slot] = slot_used.get(slot, 0) + task.get_duration()
                total_used += task.get_duration()
                task.skipped = False
                accepted.append(task)
            else:
                task.skipped = True

        return accepted

    # ------------------------------------------------------------------
    # Backward-compatibility aliases
    # ------------------------------------------------------------------

    def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority descending (kept for backward compatibility)."""
        return sorted(tasks, key=lambda t: t.get_priority(), reverse=True)

    def sort_by_time_then_priority(self, tasks: List[Task]) -> List[Task]:
        """Alias for :meth:`sort_by_time` (kept for backward compatibility)."""
        return self.sort_by_time(tasks)
