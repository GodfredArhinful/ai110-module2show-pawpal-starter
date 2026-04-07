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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
