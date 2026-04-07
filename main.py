#!/usr/bin/env python3
"""
PawPal+ CLI Demo Script
A temporary testing ground to verify the scheduling logic works correctly.
"""

from datetime import datetime
from pawpal_system import Owner, Pet, Task, Scheduler

def main():
    # Create an Owner
    owner = Owner(
        name="Alice",
        preferences={"available_time": 120, "preferred_times": ["morning", "evening"]}
    )
    
    # Create Pets
    buddy = Pet(
        name="Buddy",
        species="Dog",
        age=3,
        special_needs=["high energy", "needs frequent walks"],
        tasks=[]
    )
    
    whiskers = Pet(
        name="Whiskers",
        species="Cat",
        age=5,
        special_needs=["indoor only"],
        tasks=[]
    )
    
    # Add pets to owner
    owner.add_pet(buddy)
    owner.add_pet(whiskers)
    
    # Create Tasks for Buddy
    task1 = Task(
        description="Morning walk",
        duration=30,
        priority=5,
        time_preference="morning",
        recurring="daily",
        pet=buddy
    )
    
    task2 = Task(
        description="Evening walk",
        duration=30,
        priority=5,
        time_preference="evening",
        recurring="daily",
        pet=buddy
    )
    
    task3 = Task(
        description="Play fetch",
        duration=20,
        priority=3,
        time_preference="morning",
        recurring="daily",
        pet=buddy
    )
    
    # Create Tasks for Whiskers
    task4 = Task(
        description="Feed Whiskers",
        duration=10,
        priority=4,
        time_preference="morning",
        recurring="daily",
        pet=whiskers
    )
    
    task5 = Task(
        description="Change litter box",
        duration=15,
        priority=3,
        time_preference="evening",
        recurring="daily",
        pet=whiskers
    )
    
    # Add tasks to pets
    buddy.add_task(task1)
    buddy.add_task(task2)
    buddy.add_task(task3)
    whiskers.add_task(task4)
    whiskers.add_task(task5)
    
    # Create a Scheduler
    scheduler = Scheduler(owner)
    
    # Generate today's schedule
    today = datetime.now().strftime("%Y-%m-%d")
    daily_plan = scheduler.generate_daily_plan(today)
    
    # Print the schedule
    print("=" * 60)
    print(f"🐾 PawPal+ Daily Schedule for {today}")
    print(f"Owner: {owner.name}")
    print("=" * 60)
    
    if not daily_plan:
        print("No tasks scheduled for today.")
    else:
        total_duration = 0
        for idx, task in enumerate(daily_plan, 1):
            print(f"\n{idx}. {task.description}")
            print(f"   Pet: {task.pet.name}")
            print(f"   Duration: {task.get_duration()} minutes")
            print(f"   Priority: {task.get_priority()}/5")
            print(f"   Time preference: {task.time_preference}")
            print(f"   Recurring: {task.recurring}")
            total_duration += task.get_duration()
    
    print("\n" + "=" * 60)
    print(f"Total time needed today: {total_duration} minutes")
    print("=" * 60)
    
    # Print pet overview
    print("\n📋 Pet Overview:")
    for pet in owner.get_pets():
        info = pet.get_info()
        print(f"\n  {info['name']} ({info['species']})")
        print(f"    Age: {info['age']} years")
        print(f"    Special needs: {', '.join(info['special_needs'])}")
        print(f"    Tasks scheduled: {len(pet.get_tasks())}")

if __name__ == "__main__":
    main()
