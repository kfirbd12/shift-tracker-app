import pandas as pd
from datetime import date

def init_shift_data():
    return pd.DataFrame(columns=["תאריך", "סוג", "הערות", "משתמש"])

def add_shift(data, date_input, shift_type, notes, user):
    new_row = {
        "תאריך": date_input,
        "סוג": shift_type,
        "הערות": notes,
        "משתמש": user
    }
    return pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)
import os

SHIFT_FILE = "shifts.csv"

def save_shift_data(df):
    df.to_csv(SHIFT_FILE, index=False)

def load_shift_data():
    import pandas as pd
    if os.path.exists(SHIFT_FILE):
        df = pd.read_csv(SHIFT_FILE, parse_dates=["תאריך"])
        return df
    return init_shift_data()