import streamlit as st
import hashlib
import random
import numpy as np
import pymongo
from datetime import datetime

np.random.seed(1)

# Connect to MongoDB
client = pymongo.MongoClient("mongodb+srv://jinang2110:jinu2110@cluster0.3aodk9n.mongodb.net/?retryWrites=true&w=majority&appName=cluster0",server_api=pymongo.server_api.ServerApi('1'))
db = client["Bus_Booking_System"]
users_collection = db["Users_info"]
Admin_collection = db["Admin_access"]
buses_collection = db["Bus_info"]
user_interaction_collection=db["User_interaction"]

def register(username, password,email):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    user = users_collection.find_one({"username": username})

    if user or email=="" or username=="" or password=="":
        return False
    else:
        user_data = {"username": username, "password": hashed_password, "Email":email}
        users_collection.insert_one(user_data)
        st.write("User created successfully.")
        return True     

def login(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    user = users_collection.find_one({"username": username, "password": hashed_password})
    if user:
        st.success("Login successful.")
        return True
    else:
        st.write("Invalid username or password.")
        return False

def Adminlogin(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    user = Admin_collection.find_one({"username": username, "password": hashed_password})
    if user:
        st.success("Login successful.")
        return True
    else:
        st.write("Invalid username or password.")
        return False