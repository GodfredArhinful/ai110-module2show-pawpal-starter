import streamlit as st
from datetime import datetime
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

# Initialize session state for persistent data
if "owner" not in st.session_state:
    st.session_state.owner = None

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner Setup")

# Create or retrieve owner from session state
col1, col2 = st.columns([3, 1])
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
with col2:
    if st.button("Initialize Owner"):
        st.session_state.owner = Owner(name=owner_name, preferences={})
        st.success(f"Owner '{owner_name}' created!")

if st.session_state.owner:
    st.info(f"✅ Current owner: **{st.session_state.owner.name}**")
else:
    st.warning("Please initialize an owner first.")

st.divider()

if st.session_state.owner:
    st.subheader("Manage Pets")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        new_pet_name = st.text_input("Pet name", value="Mochi")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])
    with col3:
        age = st.number_input("Age (years)", min_value=0, max_value=50, value=2)
    
    if st.button("Add Pet"):
        new_pet = Pet(
            name=new_pet_name,
            species=species,
            age=age,
            special_needs=[],
            tasks=[]
        )
        st.session_state.owner.add_pet(new_pet)
        st.success(f"Pet '{new_pet_name}' added!")
        st.rerun()
    
    # Display current pets
    if st.session_state.owner.get_pets():
        st.subheader("Your Pets")
        for pet in st.session_state.owner.get_pets():
            with st.expander(f"🐾 {pet.name} ({pet.species.capitalize()})"):
                info = pet.get_info()
                st.write(f"**Age:** {info['age']} years")
                st.write(f"**Tasks scheduled:** {len(pet.get_tasks())}")
    else:
        st.info("No pets yet. Add one above!")
else:
    st.warning("⚠️ Create an owner first to manage pets.")

st.divider()

if st.session_state.owner and st.session_state.owner.get_pets():
    st.subheader("Add Tasks")
    
    # Select which pet gets the task
    pet_names = [pet.name for pet in st.session_state.owner.get_pets()]
    selected_pet_name = st.selectbox("Select pet for task", pet_names)
    selected_pet = next(p for p in st.session_state.owner.get_pets() if p.name == selected_pet_name)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_title = st.text_input("Task description", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=30)
    with col3:
        priority = st.selectbox("Priority", [1, 2, 3, 4, 5], index=4)
    with col4:
        recurring = st.selectbox("Recurring", ["daily", "weekly"])
    
    col5, col6 = st.columns(2)
    with col5:
        time_pref = st.selectbox("Time preference", ["morning", "afternoon", "evening"])
    with col6:
        specific_time = st.text_input("Specific time (HH:MM, optional)", placeholder="08:30", help="Leave empty to use time preference only")
    
    if st.button("Add Task"):
        new_task = Task(
            description=task_title,
            duration=int(duration),
            priority=int(priority),
            time_preference=time_pref,
            recurring=recurring,
            pet=selected_pet,
            time=specific_time if specific_time else None
        )
        selected_pet.add_task(new_task)
        st.success(f"Task '{task_title}' added to {selected_pet_name}!")
        st.rerun()
    
    st.divider()
    
    st.subheader("Today's Schedule")
    st.caption("Generate a prioritized daily plan based on all your pets' tasks.")
    
    if st.button("Generate Schedule"):
        scheduler = Scheduler(st.session_state.owner)
        today = datetime.now().strftime("%Y-%m-%d")
        daily_plan = scheduler.generate_daily_plan(today)
        conflicts = scheduler.detect_conflicts(daily_plan)
        
        if conflicts:
            st.warning("⚠️ **Schedule Conflicts Detected:**")
            for conflict in conflicts:
                st.write(f"- {conflict}")
            st.divider()
        
        if daily_plan:
            st.success(f"✅ Generated schedule for {today}")
            
            # Display schedule in a table format
            schedule_data = []
            total_duration = 0
            
            for idx, task in enumerate(daily_plan, 1):
                time_display = task.time if task.time else task.time_preference.capitalize()
                schedule_data.append({
                    "Order": idx,
                    "Time": time_display,
                    "Task": task.description,
                    "Pet": task.pet.name,
                    "Duration": f"{task.get_duration()} min",
                    "Priority": f"{task.get_priority()}/5"
                })
                total_duration += task.get_duration()
            
            st.table(schedule_data)
            st.metric("Total Time Needed", f"{total_duration} minutes")
            
            # Task completion section
            st.subheader("Mark Tasks Complete")
            st.caption("Complete tasks to schedule their next recurrence.")
            
            completed_tasks = []
            for task in daily_plan:
                if st.button(f"✅ Complete: {task.description}", key=f"complete_{task.description}_{id(task)}"):
                    next_task = scheduler.mark_task_complete(task, today)
                    completed_tasks.append(task.description)
                    if next_task:
                        st.info(f"📅 Next '{task.description}' scheduled for {next_task.due_date}")
            
            if completed_tasks:
                st.success(f"Completed: {', '.join(completed_tasks)}")
                if st.button("🔄 Regenerate Schedule"):
                    st.rerun()
                    
        else:
            st.info("No tasks due today.")

else:
    st.warning("⚠️ Set up an owner and add pets first.")

st.divider()

st.markdown("""
---
## How This Works

**Session State Magic:** Your Owner object persists across page refreshes using `st.session_state`. 
Think of it as Streamlit's long-term memory!

**Data Flow:**
1. Create an Owner → stored in session state
2. Add Pets to the Owner → automatically linked
3. Add Tasks to Pets → each pet tracks its own tasks
4. Generate Schedule → Scheduler reads all pets' tasks and creates a prioritized plan

**Example:** Click "Initialize Owner", add a pet, then add some tasks. 
The data stays even when you refresh the page!
""")
