import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO
import os
import shutil
from fpdf import FPDF

from auth import load_users, authenticate
from data import init_shift_data, add_shift, load_shift_data, save_shift_data
from admin_panel import admin_controls

# --- טוען משתמשים ---
users_data = load_users()

# --- הגדרות דף ראשי + תפריט צד ---
st.set_page_config(page_title="מעקב משמרות", layout="wide")
st.sidebar.image("https://img.icons8.com/clouds/100/calendar.png", width=60)
st.sidebar.title("תפריט ניווט")

# --- תפריט ניווט ---
menu = st.sidebar.radio("בחר פעולה", ["📊 דשבורד", "📄 דוחות PDF", "⚙️ ניהול (Admin Only)"])

# --- טופס התחברות ---
def check_login():
    st.sidebar.header("🔐 התחברות")
    username = st.sidebar.text_input("שם משתמש")
    password = st.sidebar.text_input("סיסמה", type="password")
    if st.sidebar.button("התחבר"):
        user = authenticate(username, password, users_data)
        if user:
            st.session_state["user"] = username
            st.session_state["role"] = user["role"]
            st.success(f"שלום {username}!")
        else:
            st.error("שם משתמש או סיסמה שגויים")

# --- אימות ---
if "user" not in st.session_state:
    check_login()
    st.stop()

# --- אתחול נתונים ---
def init_data():
    if "shift_data" not in st.session_state:
        st.session_state.shift_data = load_shift_data()
    if "broadcast_message" not in st.session_state:
        st.session_state.broadcast_message = ""

init_data()

# --- ייצוא דוח PDF ---
def generate_pdf_report(df, username, title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"משתמש: {username}", ln=True)
    pdf.ln(5)

    summary = df['סוג'].value_counts()
    total_hours = 0
    total_vacation = 0
    for k, v in summary.items():
        if k == "חופשה":
            converted = v * 2.14
            total_vacation += converted
            pdf.cell(200, 10, txt=f"{k}: {v} ימים → {converted:.2f} ימי חופש", ln=True)
        elif k == "משמרת":
            converted = v * 24
            total_hours += converted
            pdf.cell(200, 10, txt=f"{k}: {v} ימים → {converted} שעות עבודה", ln=True)
        elif k == "יום עיון":
            converted = v * 6
            total_hours += converted
            pdf.cell(200, 10, txt=f"{k}: {v} ימים → {converted} שעות עיון", ln=True)
        elif k == "אימון":
            converted = v * 3
            total_hours += converted
            pdf.cell(200, 10, txt=f"{k}: {v} ימים → {converted} שעות אימון", ln=True)
        else:
            pdf.cell(200, 10, txt=f"{k}: {v} ימים", ln=True)

    pdf.ln(5)
    pdf.cell(200, 10, txt=f"סה\"כ שעות כוללות: {total_hours}", ln=True)
    pdf.cell(200, 10, txt=f"סה\"כ ימי חופש מחושבים: {total_vacation:.2f}", ln=True)

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# --- עמוד דוחות PDF ---
if menu == "📄 דוחות PDF":
    st.title("📄 הפקת דוחות PDF")
    if st.session_state.role == "admin":
        all_users = st.session_state.shift_data['משתמש'].unique()
        selected_user = st.selectbox("בחר משתמש לדוח", sorted(all_users))
        date_range = st.date_input("טווח תאריכים", value=(date.today().replace(day=1), date.today()))
        selected_df = st.session_state.shift_data.copy()
        selected_df = selected_df[(selected_df['משתמש'] == selected_user) &
                                  (selected_df['תאריך'] >= pd.to_datetime(date_range[0])) &
                                  (selected_df['תאריך'] <= pd.to_datetime(date_range[1]))]

        if not selected_df.empty:
            if st.button("📥 הפק והורד דוח PDF עבור משתמש"):
                pdf_file = generate_pdf_report(selected_df, selected_user, f"דוח פעילות - {selected_user}")
                st.download_button("📄 הורד PDF", data=pdf_file, file_name=f"report_{selected_user}.pdf")

    if st.session_state.role == "user":
        user_df = st.session_state.shift_data.copy()
        user_df = user_df[user_df['משתמש'] == st.session_state.user]
        date_range = st.date_input("טווח תאריכים לדוח אישי", value=(date.today().replace(day=1), date.today()))
        user_df = user_df[(user_df['תאריך'] >= pd.to_datetime(date_range[0])) &
                          (user_df['תאריך'] <= pd.to_datetime(date_range[1]))]

        if not user_df.empty:
            st.subheader("📄 הפקת דוח אישי")
            if st.button("📥 הפק והורד דוח PDF אישי"):
                pdf_file = generate_pdf_report(user_df, st.session_state.user, "דוח פעילות אישי")
                st.download_button("📄 הורד PDF", data=pdf_file, file_name=f"report_{st.session_state.user}.pdf")

# --- עמוד ניהול ---
elif menu == "⚙️ ניהול (Admin Only)" and st.session_state.role == "admin":
    st.title("⚙️ ניהול מערכת")
    admin_controls(users_data)

# --- דשבורד ---
elif menu == "📊 דשבורד":
    st.title("📊 דשבורד - סיכום חודשי")

    df = st.session_state.shift_data.copy()
    df = df[df['משתמש'] == st.session_state.user]

    current_month = date.today().strftime('%Y-%m')
    month_df = df[df['תאריך'].dt.strftime('%Y-%m') == current_month]

    st.markdown(f"### נתונים לחודש {current_month}")
    col1, col2, col3 = st.columns(3)
    col4 = st.columns(1)[0]

    shifts = month_df[month_df['סוג'] == 'משמרת'].shape[0]
    vacation_days = month_df[month_df['סוג'] == 'חופשה'].shape[0] * 2.14
    study_hours = month_df[month_df['סוג'] == 'יום עיון'].shape[0] * 6
    training_hours = month_df[month_df['סוג'] == 'אימון'].shape[0] * 3

    col1.metric("🕒 שעות משמרות", shifts * 24)
    col2.metric("🌴 ימי חופש", f"{vacation_days:.2f}")
    col3.metric("📘 שעות עיון", study_hours)
    col4.metric("🏋️ שעות אימון", training_hours)

    st.markdown("---")
    st.dataframe(month_df.sort_values("תאריך"))
