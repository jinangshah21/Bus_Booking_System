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


def add_bus(bus_number, source, destination, time, available_days, total_seats):
    bus = buses_collection.find_one({"BusNumber": bus_number,"Source":source,"Destination":destination,"Time":time})
    if bus:
        st.write("Bus already exists.")
        return False
    else:
        bus_data = {"BusNumber": bus_number, "Source": source, "Destination": destination, "Time": time, "AvailableDays": available_days, "OccupiedSeats": 0, "TotalSeats": total_seats}
        buses_collection.insert_one(bus_data)
        st.write("Bus added successfully.")
        return True

def update_bus(bus_number, source, destination, time, available_days, total_seats):
    bus = buses_collection.find_one({"BusNumber": bus_number})
    if bus:
        if source :
            buses_collection.update_one({"BusNumber": bus_number}, {"$set": {"Source": source}})
        if destination :
            buses_collection.update_one({"BusNumber": bus_number}, {"$set": {"Destination": destination}})
        if time :
            buses_collection.update_one({"BusNumber": bus_number}, {"$set": {"Time": time}})
        if available_days :
            buses_collection.update_one({"BusNumber": bus_number}, {"$set": {"AvailableDays": available_days}})
        if total_seats :
            buses_collection.update_one({"BusNumber": bus_number}, {"$set": {"TotalSeats": total_seats}})    
        st.write("Bus updated successfully.")
        return True
    else:
        st.error("Bus does not exist.")
        return False

def delete_bus(bus_number):
    bus = buses_collection.find_one({"BusNumber": bus_number})
    if bus:
        buses_collection.delete_one({"BusNumber": bus_number})
        st.write("Bus deleted successfully.")
        return True
    else:
        st.error("Bus does not exist.")
        return False