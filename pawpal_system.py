from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class Task:
    description: str
    duration: int  # in minutes
    priority: int  # 1-5, higher number = higher priority
    time_preference: str  # e.g., 'morning', 'evening'
    recurring: str  # e.g., 'daily', 'weekly'
    pet: 'Pet'  # forward reference
    completed: bool = False

    def is_due(self, date: str) -> bool:
        """Check if the task is due on the given date based on recurring pattern."""
        # Simple implementation: daily tasks are always due
        # weekly could check day of week, but for now assume daily
        if self.recurring == 'daily':
            return True
        # For weekly, assume due on Mondays for simplicity
        from datetime import datetime
        day = datetime.fromisoformat(date).weekday()  # 0=Monday
        return self.recurring == 'weekly' and day == 0

    def get_duration(self) -> int:
        """Return the task duration in minutes."""
        return self.duration

    def get_priority(self) -> int:
        """Return the task priority level (1-5)."""
        return self.priority

    def mark_complete(self) -> None:
        """Mark the task as completed."""
        self.completed = True

@dataclass
class Pet:
    name: str
    species: str
    age: int
    special_needs: List[str]
    tasks: List[Task]

    def add_task(self, task: Task) -> None:
        """Add a task to the pet and establish bidirectional relationship."""
        self.tasks.append(task)
        task.pet = self  # maintain bidirectional relationship

    def get_tasks(self) -> List[Task]:
        """Return all tasks associated with this pet."""
        return self.tasks

    def get_info(self) -> Dict:
        """Return a dictionary with the pet's information."""
        return {
            'name': self.name,
            'species': self.species,
            'age': self.age,
            'special_needs': self.special_needs
        }

class Owner:
    def __init__(self, name: str, preferences: Dict):
        self.name = name
        self.preferences = preferences
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's pet list."""
        self.pets.append(pet)

    def get_pets(self) -> List[Pet]:
        """Return all pets owned by this owner."""
        return self.pets

    def update_preferences(self, prefs: Dict) -> None:
        """Update the owner's preferences with the provided dictionary."""
        self.preferences.update(prefs)

    def get_all_tasks(self) -> List[Task]:
        """Retrieve all tasks from all pets owned by this owner."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def generate_daily_plan(self, date: str) -> List[Task]:
        """Generate a prioritized daily plan for the given date."""
        all_tasks = self.owner.get_all_tasks()
        due_tasks = [task for task in all_tasks if task.is_due(date) and not task.completed]
        sorted_tasks = self.sort_by_priority(due_tasks)
        resolved_tasks = self.resolve_conflicts(sorted_tasks)
        return resolved_tasks

    def resolve_conflicts(self, tasks: List[Task]) -> List[Task]:
        """Resolve scheduling conflicts and return feasible task list."""
        # Simple implementation: just return sorted tasks
        # In a real system, check for time overlaps and prioritize
        # For now, assume all tasks can fit
        return tasks

    def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks in descending order by priority."""
        return sorted(tasks, key=lambda t: t.get_priority(), reverse=True)