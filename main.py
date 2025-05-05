st.sidebar.image("https://img.icons8.com/clouds/100/calendar.png", width=60)
st.sidebar.title("תפריט ניווט")
menu = st.sidebar.radio("בחר פעולה", ["📊 דשבורד", "📆 לוח שנה", "📄 דוחות PDF", "⚙️ ניהול (Admin Only)"])

from datetime import date
import calendar

today = date.today()
year = today.year
month = today.month
cal = calendar.monthcalendar(year, month)

if menu == \"📆 לוח שנה\":
    st.sidebar.markdown("---")
    st.sidebar.subheader("➕ הוסף אירוע")
    with st.sidebar.form("add_event_form"):
        selected_day = st.date_input("תאריך")
        event_type = st.selectbox("סוג אירוע", ["משמרת", "חופשה", "יום עיון", "אימון"])
        note = st.text_input("הערה (לא חובה)", "")
        submit = st.form_submit_button("הוסף אירוע")
        if submit:
            new_event = pd.DataFrame([{
                'תאריך': pd.to_datetime(selected_day),
                'משתמש': st.session_state.user,
                'סוג': event_type,
                'הערה': note
            }])
            st.session_state.shift_data = pd.concat([st.session_state.shift_data, new_event], ignore_index=True)
            save_shift_data(st.session_state.shift_data)
            st.success("האירוע נוסף!")
    st.title("📆 לוח שנה אינטראקטיבי")

    import pandas as pd
    if 'shift_data' not in st.session_state:
        st.session_state.shift_data = pd.DataFrame({
            'תאריך': pd.to_datetime(['2024-05-10', '2024-05-15', '2024-05-10', '2024-06-01']),
            'משתמש': ['user1', 'user1', 'user2', 'user1'],
            'סוג': ['משמרת', 'חופשה', 'אימון', 'משמרת'],
        })
    if 'user' not in st.session_state:
        st.session_state.user = 'user1'

    def save_shift_data(df):
        st.session_state.shift_data = df

    def get_color(event_type):
        return {
            "משמרת": "#d1e7dd",
            "חופשה": "#fde2e2",
            "יום עיון": "#fff3cd",
            "אימון": "#e2e3f3"
        }.get(event_type, "#f8f9fa")

    def delete_event(event_index):
        try:
            if event_index in st.session_state.shift_data.index:
                st.session_state.shift_data = st.session_state.shift_data.drop(event_index)
                save_shift_data(st.session_state.shift_data)
                st.success("האירוע נמחק בהצלחה!")
            else:
                st.error(f"שגיאה: לא ניתן למצוא את האירוע עם אינדקס {event_index}.")
        except Exception as e:
            st.error(f"שגיאה במחיקת אירוע: {e}")

    calendar_df = st.session_state.shift_data.copy()
    calendar_df['תאריך'] = pd.to_datetime(calendar_df['תאריך'], errors='coerce')
    calendar_df = calendar_df.dropna(subset=['תאריך'])
    calendar_df = calendar_df[
        (calendar_df['משתמש'] == st.session_state.user) &
        (calendar_df['תאריך'].dt.month == month) &
        (calendar_df['תאריך'].dt.year == year)
    ]

    st.markdown("| יום א' | יום ב' | יום ג' | יום ד' | יום ה' | יום ו' | שבת |")
    st.markdown("|---|---|---|---|---|---|---|")

    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.markdown("&nbsp;")
                else:
                    st.markdown(f"<strong>{day}</strong>", unsafe_allow_html=True)
                    day_events = calendar_df[calendar_df['תאריך'].dt.day == day]
                    if not day_events.empty:
                        for idx, event_data in day_events.iterrows():
                            bg_color = get_color(event_data['סוג'])
                            button_key = f"del_{idx}"
                            with st.container():
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
                                    st.button(
                                        "🗑️",
                                        key=button_key,
                                        help=f"מחק אירוע '{event_data['סוג']}' בתאריך {event_data['תאריך'].strftime('%d/%m')}",
                                        on_click=delete_event,
                                        args=(idx,)
                                    )
                    else:
                        st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
