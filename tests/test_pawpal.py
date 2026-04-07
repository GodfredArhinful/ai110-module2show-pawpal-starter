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
