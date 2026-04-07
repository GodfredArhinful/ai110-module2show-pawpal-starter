from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class Task:
    description: str
    duration: int  # in minutes
    priority: int  # 1-5
    time_preference: str  # e.g., 'morning', 'evening'
    recurring: str  # e.g., 'daily', 'weekly'
    pet: 'Pet'  # forward reference

    def is_due(self, date: str) -> bool:
        # For now, assume daily tasks are always due
        # TODO: implement recurring logic
        return self.recurring == 'daily'

    def get_duration(self) -> int:
        return self.duration

    def get_priority(self) -> int:
        return self.priority

@dataclass
class Pet:
    name: str
    species: str
    age: int
    special_needs: List[str]
    tasks: List[Task]

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)
        task.pet = self  # maintain bidirectional relationship

    def get_tasks(self) -> List[Task]:
        return self.tasks

    def get_info(self) -> Dict:
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
        self.pets.append(pet)

    def get_pets(self) -> List[Pet]:
        return self.pets

    def update_preferences(self, prefs: Dict) -> None:
        self.preferences.update(prefs)

    def get_all_tasks(self) -> List[Task]:
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def generate_daily_plan(self, date: str) -> List[Task]:
        pass

    def resolve_conflicts(self, tasks: List[Task]) -> List[Task]:
        pass

    def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        pass