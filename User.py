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

def book_seat(bus_number, travel_date, travel_time, username):
    booking_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    travel_date = datetime.combine(travel_date, datetime.min.time())
    bus=buses_collection.find_one({'BusNumber':bus_number})
    if user_interaction_collection.find_one({'Username':username,'BusNumber':bus_number,'TravelDate':travel_date,'TravelTime':travel_date,'IsCancelled':False}) :
        st.warning("Seat Already Booked")
    elif bus['TotalSeats']==bus['OccupiedSeats']:
        st.error("No Seats Available")
    else:
        if user_interaction_collection.find_one({'Username':username,'BusNumber':bus_number,'TravelDate': travel_date,
                'TravelTime': travel_time,'IsCancelled':True}) :
            user_interaction_collection.update_one(
                {'Username': username,
                'BusNumber': bus_number,
                'TravelTime': travel_time
                },
                {"$set" : {'TravelDate': travel_date,'BookingTime': booking_time,
                "CancellingTime": "",
                "IsCancelled":False}})
        else :
            user_interaction_collection.insert_one({
                'Username': username,
                'BusNumber': bus_number,
                'TravelDate': travel_date,
                'TravelTime': travel_time,
                'BookingTime': booking_time,
                'CancellingTime': "",
                'IsCancelled':False
            })

        buses_collection.update_one({'BusNumber': bus_number}, {'$inc': {'OccupiedSeats': 1}})
        st.success("Booked Seat Successfully")

def cancel_seat(bus_number, travel_date, travel_time, username):
    travel_date = datetime.combine(travel_date, datetime.min.time())
    cancelling_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if user_interaction_collection.find_one({'Username':username,'BusNumber':bus_number,'TravelDate':travel_date,'TravelTime':travel_time,'IsCancelled':False}) :
        user_interaction_collection.update_one({
            'Username': username,
            'BusNumber': bus_number,
            'TravelDate': travel_date,
            'TravelTime': travel_time
        },{"$set": {"CancellingTime": cancelling_time,'IsCancelled':True}})
        buses_collection.update_one({'BusNumber': bus_number}, {'$inc': {'OccupiedSeats': -1}})
        st.success("Cancelled Seat Successfully")
    else :
        st.error("You Have no seats to Cancel")