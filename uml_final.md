```mermaid
classDiagram
    class Owner {
        +name: str
        +preferences: Dict
        +pets: List[Pet]
        +__init__(name, preferences)
        +add_pet(pet)
        +get_pets() List[Pet]
        +update_preferences(prefs)
        +get_all_tasks() List[Task]
        +get_tasks_for_pet(pet_name) List[Task]
        +get_tasks_by_status(completed) List[Task]
    }

    class Pet {
        +name: str
        +species: str
        +age: int
        +special_needs: List[str]
        +tasks: List[Task]
        +__init__(name, species, age, special_needs, tasks)
        +add_task(task)
        +get_tasks() List[Task]
        +get_info() Dict
    }

    class Task {
        +description: str
        +duration: int
        +priority: int
        +time_preference: str
        +recurring: str
        +pet: Pet
        +completed: bool
        +skipped: bool
        +start_date: Optional[str]
        +due_date: Optional[str]
        +time: Optional[str]
        +__init__(...)
        +is_due(date) bool
        +get_duration() int
        +get_priority() int
        +mark_complete()
    }

    class Scheduler {
        +owner: Owner
        +__init__(owner)
        +generate_daily_plan(date) List[Task]
        +sort_by_time(tasks) List[Task]
        +filter_tasks(pet_name, completed) List[Task]
        +detect_conflicts(tasks) List[str]
        +mark_task_complete(task, date) Optional[Task]
        +resolve_conflicts(tasks) List[Task]
        +sort_by_priority(tasks) List[Task]
        +sort_by_time_then_priority(tasks) List[Task]
    }

    Owner ||--o{ Pet : owns
    Pet ||--o{ Task : has
    Task --> Pet : belongs_to
    Scheduler --> Owner : manages
    Scheduler --> Task : processes
```</content>
<parameter name="filePath">c:\Users\godfr\Desktop\ai110-module2show-pawpal-starter\uml_final.md