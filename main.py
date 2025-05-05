import streamlit as st
import pandas as pd
import calendar # נניח שזה מיובא

# --- הגדרות ראשוניות (להחליף בערכים האמיתיים שלך) ---
# נניח ש- st.session_state.shift_data ו- st.session_state.user כבר קיימים
# נניח ש- month ו- year מוגדרים (למשל, מבחירת המשתמש)
# נניח ש- save_shift_data היא פונקציה ששומרת את ה-DataFrame
# נניח ש- cal הוא אובייקט לוח שנה (למשל, מ- calendar.monthcalendar(year, month))

# Example placeholder values (replace with your actual logic)
if 'shift_data' not in st.session_state:
    # Sample data for demonstration
    st.session_state.shift_data = pd.DataFrame({
        'תאריך': pd.to_datetime(['2024-05-10', '2024-05-15', '2024-05-10', '2024-06-01']),
        'משתמש': ['user1', 'user1', 'user2', 'user1'],
        'סוג': ['משמרת', 'חופשה', 'אימון', 'משמרת'],
        # Add other relevant columns
    })
if 'user' not in st.session_state:
    st.session_state.user = 'user1' # Example user

# Assume month and year are selected elsewhere, e.g., using st.selectbox
month = 5 # Example month (May)
year = 2024 # Example year

# Placeholder for the save function
def save_shift_data(df):
    print("Saving data...") # Replace with your actual saving mechanism
    st.session_state.shift_data = df # Update session state

# Placeholder for calendar object
cal = calendar.monthcalendar(year, month)

# --- Sidebar Navigation ---
st.sidebar.image("https://img.icons8.com/clouds/100/calendar.png", width=60)
st.sidebar.title("תפריט ניווט")
menu_options = ["📊 דשבורד", "📆 לוח שנה", "📄 דוחות PDF", "⚙️ ניהול (Admin Only)"]
# Use query params to keep track of the menu selection for robustness after rerun
if 'menu_selection' not in st.query_params:
     # Set default if not in query params
     st.query_params.menu_selection = menu_options[0]

# Get current selection from query params
current_selection = st.query_params.menu_selection

# Find the index of the current selection for the radio button
try:
    current_index = menu_options.index(current_selection)
except ValueError:
    current_index = 0 # Default to first option if not found

# Update query params when radio button changes
def update_menu_selection():
    st.query_params.menu_selection = st.session_state.menu_radio # Get value from radio

menu = st.sidebar.radio(
    "בחר פעולה",
    menu_options,
    index=current_index,
    key='menu_radio', # Assign a key to the radio button
    on_change=update_menu_selection # Update query param on change
)


# --- Calendar View ---
if menu == "📆 לוח שנה":
    st.title("📆 לוח שנה אינטראקטיבי")

    # --- Function to get color based on event type (defined outside the loop) ---
    def get_color(event_type):
        """Returns a background color based on the event type."""
        return {
            "משמרת": "#d1e7dd",  # Light green
            "חופשה": "#fde2e2",  # Light red
            "יום עיון": "#fff3cd", # Light yellow
            "אימון": "#e2e3f3"   # Light purple
        }.get(event_type, "#f8f9fa") # Default light gray

    # --- Function to handle event deletion ---
    def delete_event(event_index):
        """Deletes an event from the shift_data DataFrame."""
        try:
            # Ensure the index exists before attempting to drop
            if event_index in st.session_state.shift_data.index:
                st.session_state.shift_data = st.session_state.shift_data.drop(event_index)
                save_shift_data(st.session_state.shift_data) # Save the updated data
                st.success("האירוע נמחק בהצלחה!")
                # No explicit rerun needed here, Streamlit reruns automatically
                # after callback execution if session state is modified.
                # However, if you face issues with refresh, uncomment st.rerun()
                # st.rerun()
            else:
                st.error(f"שגיאה: לא ניתן למצוא את האירוע עם אינדקס {event_index}.")
        except Exception as e:
            st.error(f"שגיאה במחיקת אירוע: {e}")

    # --- Ensure datetime type and filter data ---
    calendar_df = st.session_state.shift_data.copy()
    calendar_df['תאריך'] = pd.to_datetime(calendar_df['תאריך'], errors='coerce')
    calendar_df = calendar_df.dropna(subset=['תאריך'])

    # Filter for the current user and selected month/year
    calendar_df = calendar_df[
        (calendar_df['משתמש'] == st.session_state.user) &
        (calendar_df['תאריך'].dt.month == month) &
        (calendar_df['תאריך'].dt.year == year)
    ]

    # --- Display Calendar Header ---
    st.markdown("| יום א' | יום ב' | יום ג' | יום ד' | יום ה' | יום ו' | שבת |")
    st.markdown("|---|---|---|---|---|---|---|") # Separator line

    # --- Display Calendar Grid ---
    for week in cal:
        cols = st.columns(7) # Create 7 columns for the days of the week
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.markdown("&nbsp;") # Empty cell for days outside the month
                else:
                    # Display the day number
                    st.markdown(f"<strong>{day}</strong>", unsafe_allow_html=True)

                    # Find events for the current day
                    day_events = calendar_df[calendar_df['תאריך'].dt.day == day]

                    if not day_events.empty:
                        # Display each event for the day
                        for idx, event_data in day_events.iterrows():
                            bg_color = get_color(event_data['סוג'])
                            # Use the original DataFrame index (idx) for the key and deletion
                            button_key = f"del_{idx}"

                            # Create a container for better layout
                            with st.container():
                                # Use columns for event text and delete button
                                col1, col2 = st.columns([0.8, 0.2])
                                with col1:
                                    st.markdown(
                                        f"""<div style='background-color:{bg_color};
                                                    padding: 3px 5px;
                                                    border-radius: 5px;
                                                    margin: 2px 0;
                                                    font-size: 0.9em;'>
                                            {event_data['סוג']}
                                        </div>""",
                                        unsafe_allow_html=True
                                    )
                                with col2:
                                    # Delete button with callback
                                    st.button(
                                        "🗑️",
                                        key=button_key,
                                        help=f"מחק אירוע '{event_data['סוג']}' בתאריך {event_data['תאריך'].strftime('%d/%m')}",
                                        on_click=delete_event,
                                        args=(idx,) # Pass the original index to the callback
                                    )
                    else:
                        # Add some space if there are no events to maintain alignment
                         st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)


# --- Other Menu Options ---
elif menu == "📊 דשבורד":
    st.title("📊 דשבורד")
    st.write("כאן יוצג סיכום חודשי / סטטיסטיקות.")
    # Add dashboard elements here

elif menu == "📄 דוחות PDF":
    st.title("📄 דוחות PDF")
    st.write("כאן תוכל להפיק דוחות PDF לפי טווח תאריכים.")
    # Add PDF generation logic here

elif menu == "⚙️ ניהול (Admin Only)":
    st.title("⚙️ ניהול משתמשים")
    st.write("כאן מנהל המערכת יוכל להוסיף / לערוך / למחוק משתמשים.")
    # Add admin management features here
