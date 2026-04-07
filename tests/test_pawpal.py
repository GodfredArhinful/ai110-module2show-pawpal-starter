import pytest
from pawpal_system import Owner, Pet, Task, Scheduler


def test_task_completion():
    """Verify that calling mark_complete() changes the task's completion status."""
    # Create a pet and task
    pet = Pet(
        name="Buddy",
        species="Dog",
        age=3,
        special_needs=[],
        tasks=[]
    )
    
    task = Task(
        description="Morning walk",
        duration=30,
        priority=5,
        time_preference="morning",
        recurring="daily",
        pet=pet,
        completed=False
    )
    
    # Initially, task should not be completed
    assert task.completed is False, "Task should not be completed initially"
    
    # Mark task as complete
    task.mark_complete()
    
    # Verify it's now marked as completed
    assert task.completed is True, "Task should be completed after calling mark_complete()"


def test_task_addition_to_pet():
    """Verify that adding a task to a Pet increases that pet's task count."""
    # Create a pet with no tasks
    pet = Pet(
        name="Whiskers",
        species="Cat",
        age=5,
        special_needs=["indoor only"],
        tasks=[]
    )
    
    # Initially, pet should have 0 tasks
    assert len(pet.get_tasks()) == 0, "Pet should have 0 tasks initially"
    
    # Create and add a task
    task = Task(
        description="Feed Whiskers",
        duration=10,
        priority=4,
        time_preference="morning",
        recurring="daily",
        pet=pet
    )
    
    pet.add_task(task)
    
    # Verify task count increased to 1
    assert len(pet.get_tasks()) == 1, "Pet should have 1 task after adding one"
    
    # Add a second task and verify count increased again
    task2 = Task(
        description="Clean litter box",
        duration=15,
        priority=3,
        time_preference="evening",
        recurring="daily",
        pet=pet
    )
    
    pet.add_task(task2)
    
    # Verify task count increased to 2
    assert len(pet.get_tasks()) == 2, "Pet should have 2 tasks after adding two"


def test_scheduler_generates_plan():
    """Verify that Scheduler generates a daily plan with sorted tasks."""
    # Create owner with pets and tasks
    owner = Owner(name="Alice", preferences={})
    
    pet = Pet(
        name="Buddy",
        species="Dog",
        age=2,
        special_needs=[],
        tasks=[]
    )
    owner.add_pet(pet)
    
    # Add tasks with different priorities
    low_priority = Task(
        description="Low priority task",
        duration=10,
        priority=1,
        time_preference="morning",
        recurring="daily",
        pet=pet
    )
    
    high_priority = Task(
        description="High priority task",
        duration=20,
        priority=5,
        time_preference="morning",
        recurring="daily",
        pet=pet
    )
    
    pet.add_task(low_priority)
    pet.add_task(high_priority)
    
    # Generate schedule
    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan("2026-04-07")
    
    # Verify plan contains both tasks
    assert len(plan) == 2, "Plan should contain 2 tasks"
    
    # Verify tasks are sorted by priority (high first)
    assert plan[0].get_priority() == 5, "First task should have highest priority"
    assert plan[1].get_priority() == 1, "Second task should have lower priority"


def test_sorting_by_time():
    """Verify tasks are sorted by specific time, then priority."""
    owner = Owner(name="Alice", preferences={})
    pet = Pet(name="Buddy", species="Dog", age=2, special_needs=[], tasks=[])
    owner.add_pet(pet)
    
    # Tasks with specific times
    task1 = Task(description="Early task", duration=10, priority=3, time_preference="morning", recurring="daily", pet=pet, time="08:00")
    task2 = Task(description="Late task", duration=10, priority=5, time_preference="morning", recurring="daily", pet=pet, time="10:00")
    task3 = Task(description="Same time high priority", duration=10, priority=5, time_preference="morning", recurring="daily", pet=pet, time="08:00")
    
    pet.add_task(task1)
    pet.add_task(task2)
    pet.add_task(task3)
    
    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan("2026-04-07")
    
    # Should be sorted by time: 08:00 tasks first, then 10:00
    assert plan[0].time == "08:00" and plan[0].priority == 5, "First should be high priority at 08:00"
    assert plan[1].time == "08:00" and plan[1].priority == 3, "Second should be lower priority at 08:00"
    assert plan[2].time == "10:00", "Third should be at 10:00"


def test_recurrence_logic():
    """Verify marking a daily task complete creates next occurrence."""
    owner = Owner(name="Alice", preferences={})
    pet = Pet(name="Buddy", species="Dog", age=2, special_needs=[], tasks=[])
    owner.add_pet(pet)
    
    task = Task(description="Daily walk", duration=30, priority=5, time_preference="morning", recurring="daily", pet=pet, time="08:00")
    pet.add_task(task)
    
    scheduler = Scheduler(owner)
    
    # Initially, task should be due
    plan = scheduler.generate_daily_plan("2026-04-07")
    assert len(plan) == 1, "Task should be in plan initially"
    
    # Mark complete
    next_task = scheduler.mark_task_complete(task, "2026-04-07")
    
    # Task should be completed
    assert task.completed == True, "Original task should be completed"
    
    # Next task should be created for next day
    assert next_task is not None, "Next task should be created"
    assert next_task.due_date == "2026-04-08", "Next task should be due tomorrow"
    assert next_task.completed == False, "Next task should not be completed"
    
    # Next day plan should include the new task
    plan_next = scheduler.generate_daily_plan("2026-04-08")
    assert len(plan_next) == 1, "Next day's plan should have the recurring task"


def test_conflict_detection():
    """Verify Scheduler flags duplicate times."""
    owner = Owner(name="Alice", preferences={})
    pet = Pet(name="Buddy", species="Dog", age=2, special_needs=[], tasks=[])
    owner.add_pet(pet)
    
    task1 = Task(description="Task 1", duration=30, priority=5, time_preference="morning", recurring="daily", pet=pet, time="08:00")
    task2 = Task(description="Task 2", duration=30, priority=4, time_preference="morning", recurring="daily", pet=pet, time="08:00")
    
    pet.add_task(task1)
    pet.add_task(task2)
    
    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan("2026-04-07")
    conflicts = scheduler.detect_conflicts(plan)
    
    assert len(conflicts) == 1, "Should detect one conflict"
    assert "conflict at 08:00" in conflicts[0], "Conflict message should mention the time"


def test_conflict_resolution():
    """Verify tasks exceeding capacity are skipped."""
    owner = Owner(name="Alice", preferences={"available_time": 60})  # Only 60 minutes total
    pet = Pet(name="Buddy", species="Dog", age=2, special_needs=[], tasks=[])
    owner.add_pet(pet)
    
    task1 = Task(description="Task 1", duration=30, priority=5, time_preference="morning", recurring="daily", pet=pet)
    task2 = Task(description="Task 2", duration=40, priority=4, time_preference="morning", recurring="daily", pet=pet)
    
    pet.add_task(task1)
    pet.add_task(task2)
    
    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan("2026-04-07")
    
    # Only first task should fit (30 <= 60), second should be skipped (40 > 30 remaining)
    assert len(plan) == 1, "Only one task should fit in the plan"
    assert plan[0].description == "Task 1", "First task should be included"
    assert task2.skipped == True, "Second task should be skipped"


def test_pet_with_no_tasks():
    """Verify handling of pet with no tasks."""
    owner = Owner(name="Alice", preferences={})
    pet = Pet(name="Buddy", species="Dog", age=2, special_needs=[], tasks=[])
    owner.add_pet(pet)
    
    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan("2026-04-07")
    
    assert len(plan) == 0, "Plan should be empty for pet with no tasks"


def test_weekly_recurrence():
    """Verify weekly tasks recur on correct weekday."""
    owner = Owner(name="Alice", preferences={})
    pet = Pet(name="Buddy", species="Dog", age=2, special_needs=[], tasks=[])
    owner.add_pet(pet)
    
    # Start on Monday 2026-04-07
    task = Task(description="Weekly grooming", duration=60, priority=4, time_preference="afternoon", recurring="weekly", pet=pet, start_date="2026-04-07")
    pet.add_task(task)
    
    scheduler = Scheduler(owner)
    
    # Should be due on Monday
    plan_mon = scheduler.generate_daily_plan("2026-04-07")
    assert len(plan_mon) == 1, "Task should be due on Monday"
    
    # Should not be due on Tuesday
    plan_tue = scheduler.generate_daily_plan("2026-04-08")
    assert len(plan_tue) == 0, "Task should not be due on Tuesday"
    
    # Mark complete and check next Monday
    scheduler.mark_task_complete(task, "2026-04-07")
    plan_next_mon = scheduler.generate_daily_plan("2026-04-14")
    assert len(plan_next_mon) == 1, "Task should recur on next Monday"
