
import streamlit as st
from auth import save_users

def admin_controls(users_data):
    st.subheader("📢 שליחת הודעת תפוצה")
    message = st.text_area("תוכן ההודעה")
    if st.button("שלח הודעה"):
        st.session_state.broadcast_message = message
        st.success("ההודעה נשלחה לכלל המשתמשים")

    st.subheader("👥 ניהול משתמשים")
    st.markdown("#### משתמשים קיימים:")
    for uname, info in users_data.items():
        col1, col2, col3 = st.columns([3, 3, 2])
        with col1:
            st.write(f"{uname} ({info['role']})")
        with col2:
            new_role = st.selectbox(f"הרשאה ל-{uname}", ["user", "admin"], index=["user", "admin"].index(info['role']), key=f"role_{uname}")
        with col3:
            if st.button(f"מחק {uname}", key=f"del_{uname}"):
                if uname != "admin":
                    users_data.pop(uname)
                    save_users(users_data)
                    st.experimental_rerun()
        if new_role != info["role"]:
            users_data[uname]["role"] = new_role
            save_users(users_data)

    st.markdown("#### הוספת משתמש חדש:")
    new_user = st.text_input("שם משתמש חדש")
    new_pass = st.text_input("סיסמה חדשה", type="password")
    new_role = st.selectbox("הרשאת משתמש", ["user", "admin"])
    if st.button("הוסף משתמש"):
        if new_user and new_pass:
            from hashlib import md5
            users_data[new_user] = {
                "password": md5(new_pass.encode()).hexdigest(),
                "role": new_role
            }
            save_users(users_data)
            st.success("המשתמש נוסף!")
            st.experimental_rerun()
        else:
            st.error("יש למלא שם וסיסמה")
