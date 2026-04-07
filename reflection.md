# PawPal+ Project Reflection

## 1. System Design

**Core Actions:**

1. Enter basic owner and pet information
2. Add or edit care tasks with details like duration and priority
3. Generate and view a daily schedule/plan based on constraints and priorities

**a. Initial design**

The initial UML design consists of four main classes: Owner, Pet, Task, and Scheduler.

- **Owner**: Represents the pet owner, holding attributes like name and preferences (e.g., available time slots). Responsibilities include managing pets (adding/getting pets) and updating preferences.

- **Pet**: Represents an individual pet, with attributes such as name, species, age, and special needs. It manages tasks associated with the pet (adding/getting tasks) and provides pet information.

- **Task**: Represents a care task, with attributes including description, duration, priority, time preference, and recurring schedule. It can check if the task is due on a given date and provide duration/priority info.

- **Scheduler**: Handles the core logic for scheduling, using the owner and tasks to generate daily plans, resolve conflicts, and sort tasks by priority.

Relationships: Owner has many Pets, Pet has many Tasks, Scheduler uses Owner and manages Tasks.

**b. Design changes**

Yes, the design changed during implementation. 

- Added a `get_all_tasks()` method to the Owner class to collect all tasks from all pets, ensuring the Scheduler can access tasks through the owner rather than maintaining a separate list.
- Modified the Scheduler's `__init__` to only take an Owner parameter, removing the redundant tasks parameter to avoid potential inconsistencies.
- Implemented simple logic in Task's `is_due()`, `get_duration()`, and `get_priority()` methods, as well as Pet's `add_task()`, `get_tasks()`, and `get_info()` methods, and Owner's `add_pet()`, `get_pets()`, and `update_preferences()` methods to establish bidirectional relationships and basic functionality.
- In Pet's `add_task()`, added logic to set `task.pet = self` to maintain the relationship between Task and Pet.

These changes improve data consistency, reduce redundancy, and prepare the skeleton for actual scheduling logic implementation.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers multiple constraints:
- **Time constraints**: Specific HH:MM times take precedence, followed by time preference slots (morning/afternoon/evening)
- **Priority**: Higher priority tasks are scheduled first within their time constraints
- **Capacity limits**: Each time slot has maximum minutes (morning: 180min, afternoon: 120min, evening: 180min)
- **Daily budget**: Owner's available_time preference limits total daily minutes
- **Recurrence patterns**: Daily tasks repeat every day, weekly tasks repeat on the same weekday

Priority was decided as the most important constraint because pet care tasks have varying urgency - feeding and medication are critical, while grooming might be less urgent. Time constraints were prioritized over pure priority when both exist because real-world scheduling requires specific timing for things like medication schedules.

**b. Tradeoffs**

**Exact-time conflict detection vs. overlap detection**

The current `detect_conflicts()` method flags two tasks as conflicting only when
they share an identical HH:MM `time` string (e.g., both at `"08:00"`).  It does
**not** check whether the time windows overlap (e.g., a 30-minute task at 07:45
and a 20-minute task at 08:00 would overlap in reality but are not flagged).

*Why this tradeoff is reasonable here:*  
Implementing true overlap detection requires knowing when each task starts **and**
ends, which means the scheduler would need to assign absolute start times to every
task rather than just slotting them into broad "morning / afternoon / evening"
buckets.  For a household pet-care planner, most users think in discrete
appointment slots ("feed the cat at 8 AM"), not back-to-back blocks, so exact
time matching catches the practically common case (two reminders set to the same
clock time) without the added complexity of a full interval-overlap algorithm.

A natural next step would be to track cumulative start times within each slot and
flag any pair `(task_a, task_b)` where `start_a + duration_a > start_b`.

---

## 3. AI Collaboration

**a. How you used AI**

I used VS Code Copilot extensively throughout the project:
- **Design brainstorming**: Used Copilot Chat to generate initial UML diagram ideas and class structure suggestions
- **Code generation**: Copilot inline suggestions helped write boilerplate code for classes, methods, and test functions
- **Debugging**: Asked Copilot to explain test failures and suggest fixes for logic errors
- **Documentation**: Used Copilot to help write clear docstrings and README sections
- **Testing**: Copilot helped generate comprehensive test cases and explain testing patterns

The most helpful prompts were specific questions about the codebase like "Based on my final implementation, what updates should I make to my initial UML diagram?" and "Why is this test failing, and is the bug in my test code or my pawpal_system.py logic?"

**b. Judgment and verification**

One moment where I rejected an AI suggestion was when Copilot suggested using a simple priority sort for the scheduler instead of the time-based sorting I had designed. The AI suggested sorting purely by priority descending, but I knew the requirements needed time-based ordering first, then priority as tiebreaker. I rejected this because it didn't match the user's need for chronological scheduling.

I verified AI suggestions by:
- Running tests to ensure functionality worked correctly
- Checking that the code matched the system design requirements
- Manually reviewing logic for edge cases
- Testing with real data scenarios to ensure practical usability

---

## 4. Testing and Verification

**a. What you tested**

I tested core scheduling behaviors including:
- Task sorting by time and priority (chronological ordering with priority tiebreakers)
- Recurrence logic (daily/weekly task auto-scheduling when completed)
- Conflict detection (warning about tasks at same HH:MM time)
- Conflict resolution (skipping tasks that exceed capacity/budget limits)
- Edge cases (pets with no tasks, multiple pets, weekly recurrence patterns)

These tests were important because they verify the smart algorithms that differentiate PawPal+ from a simple task list - ensuring tasks appear in the right order, conflicts are caught, and recurring tasks are properly managed.

**b. Confidence**

I am highly confident (5/5 stars) that the scheduler works correctly. All 9 automated tests pass, covering both happy paths and edge cases. The system handles complex scenarios like multi-pet households, time conflicts, and capacity constraints reliably.

If I had more time, I would test:
- Month-long recurrence patterns to ensure weekly tasks work across month boundaries
- Time zone handling for users in different regions
- Integration with calendar APIs for external scheduling
- Performance with very large numbers of tasks/pets
- UI responsiveness with many concurrent users

---

## 5. Reflection

**a. What went well**

I am most satisfied with the intelligent scheduling algorithms. The system successfully implements complex logic for time-based sorting, conflict detection, capacity management, and recurrence handling - going far beyond a simple priority list. The clean separation of concerns between Owner/Pet/Task/Scheduler classes made the codebase maintainable and testable.

**b. What you would improve**

If I had another iteration, I would:
- Add a visual calendar view in the Streamlit UI to show the schedule over multiple days
- Implement drag-and-drop task reordering for manual adjustments
- Add notifications/reminders for upcoming tasks
- Include more sophisticated conflict resolution (suggesting alternative times instead of just skipping)
- Add data persistence so schedules survive app restarts

**c. Key takeaway**

The most important thing I learned is the value of being the "lead architect" when collaborating with AI. While AI tools like Copilot are incredibly powerful for code generation and debugging, they need human direction to ensure the solution matches the actual requirements and maintains design coherence. I learned to use AI as a skilled assistant rather than a replacement for design thinking - asking the right questions, verifying suggestions against requirements, and maintaining the vision for how the system should work.
