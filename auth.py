
import hashlib
import json

USERS_FILE = "users.json"

def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "admin": {"password": hashlib.md5("1234".encode()).hexdigest(), "role": "admin"},
            "user1": {"password": hashlib.md5("abcd".encode()).hexdigest(), "role": "user"},
        }

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def authenticate(username, password, users_data):
    hashed = hashlib.md5(password.encode()).hexdigest()
    if username in users_data and users_data[username]["password"] == hashed:
        return users_data[username]
    return None
