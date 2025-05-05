st.sidebar.image("https://img.icons8.com/clouds/100/calendar.png", width=60)
st.sidebar.title("תפריט ניווט")
menu = st.sidebar.radio("בחר פעולה", ["📊 דשבורד", "📆 לוח שנה", "📄 דוחות PDF", "⚙️ ניהול (Admin Only)"])

if menu == "📆 לוח שנה":
    st.title("📆 לוח שנה אינטראקטיבי")
    # --- הבטחת טיפוס datetime וסינון ---
    calendar_df = st.session_state.shift_data.copy()
    calendar_df['תאריך'] = pd.to_datetime(calendar_df['תאריך'], errors='coerce')
    calendar_df = calendar_df.dropna(subset=['תאריך'])
    calendar_df = calendar_df[
        (calendar_df['משתמש'] == st.session_state.user) &
        (calendar_df['תאריך'].dt.month == month) &
        (calendar_df['תאריך'].dt.year == year)
    ]

    for week in cal:
        row = "|"
        for day in week:
            if day == 0:
                row += "   |"
            else:
                day_events = calendar_df[calendar_df['תאריך'].dt.day == day]
                if not day_events.empty:
                    def get_color(event_type):
                        return {
                            "משמרת": "#d1e7dd",
                            "חופשה": "#fde2e2",
                            "יום עיון": "#fff3cd",
                            "אימון": "#e2e3f3"
                        }.get(event_type, "#f8f9fa")

                    event_html = ""
                    for i, e in day_events.iterrows():
                        bg = get_color(e['סוג'])
                        btn_key = f"del_{e['תאריך']}_{e['סוג']}_{i}"
                        delete_url = f"?delete={e['תאריך']}&type={e['סוג']}&index={i}"
                        event_html += f"""
                        <div style='background-color:{bg}; padding:2px; border-radius:4px; margin:1px 0;'>
                            {e['סוג']} 
                            <a href='{delete_url}' style='color:red; float:left;' title='מחק'>🗑️</a>
                        </div>
                        """

                    row += f" <strong>{day}</strong><br>{event_html} |"
                else:
                    row += f" {day} |"
        st.markdown(row, unsafe_allow_html=True)

    # מחיקה דרך פרמטרים
    query = st.experimental_get_query_params()
    if "delete" in query and "type" in query and "index" in query:
        try:
            target_date = pd.to_datetime(query["delete"][0])
            target_type = query["type"][0]
            target_index = int(query["index"][0])
            st.session_state.shift_data = st.session_state.shift_data.drop(target_index)
            save_shift_data(st.session_state.shift_data)
            st.success("האירוע נמחק")
            st.experimental_set_query_params()  # נקה URL
            st.experimental_rerun()

elif menu == "📊 דשבורד":
    st.title("📊 דשבורד")
    st.write("כאן יוצג סיכום חודשי / סטטיסטיקות.")

elif menu == "📄 דוחות PDF":
    st.title("📄 דוחות PDF")
    st.write("כאן תוכל להפיק דוחות PDF לפי טווח תאריכים.")

elif menu == "⚙️ ניהול (Admin Only)":
    st.title("⚙️ ניהול משתמשים")
    st.write("כאן מנהל המערכת יוכל להוסיף / לערוך / למחוק משתמשים.")
        except Exception as e:
            st.error("שגיאה במחיקה")
