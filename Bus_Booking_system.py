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

def filter(source, destination, day):
    buses = buses_collection.find({"Source": source, "Destination": destination})
    return list(buses)

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

def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if 'username' not in st.session_state:
        st.session_state.username = " "
    
    if 'mode' not in st.session_state:
        st.session_state.mode=" "
    
    st.title("Bus Booking System")

    if not st.session_state.logged_in:
        st.sidebar.image("img2.jpg", use_column_width=True)
        selected_page = st.sidebar.radio("", ["Admin Login", "User Login", "User Register"])
        # Login/Register Section
        if selected_page=="User Login":
            st.subheader("User Login")
            login_status = st.empty()
            user = st.text_input("Username")
            password = st.text_input("Password", type="password")

            login_button = st.button("Login")

            if login_button:
                if login(user, password):
                    st.session_state.logged_in = True
                    st.session_state.username=user
                    st.session_state.mode="User"
                    login_status.success("Welcome Back ! " + user)
                    st.rerun()
                else:
                    login_status.error("Invalid username or password.")


        elif selected_page=="User Register":
            st.subheader("User Register")
            login_status = st.empty()
            user = st.text_input("Username")
            password = st.text_input("Password", type="password")
            email = st.text_input("Email")

            register_button = st.button("Register")

            if register_button:
                check=register(user, password,email)
                if check:
                    login_status.success("User registered successfully.")
                    st.session_state.logged_in = True
                    st.session_state.username=user
                    st.session_state.mode="User"
                    login_status.success("Welcome Back ! " + user)
                    st.rerun()
                else :
                    login_status.warning("Invalid Username, Password or Email.")

        elif selected_page=="Admin Login":
            st.subheader("Admin Login")
            login_status = st.empty()
            user = st.text_input("Username")
            password = st.text_input("Password", type="password")

            login_button = st.button("Login")

            if login_button:
                if Adminlogin(user, password):
                    st.session_state.logged_in = True
                    st.session_state.username=user
                    st.session_state.mode="Admin"
                    login_status.success("Welcome Back ! " + user)
                    st.rerun()
                else:
                    login_status.error("Invalid username or password.")
    
    else:
        st.subheader(f"Welcome back, {st.session_state.username}!")
        
        if st.session_state.mode=="Admin":
            st.sidebar.image("img2.jpg", use_column_width=True)
            selected_page = st.sidebar.radio("", ["Add Bus", "Update Bus", "Delete Bus"])
           
            if selected_page=="Add Bus":
                st.subheader("Add Bus")
                bus_number = st.text_input("Bus Number")
                source = st.text_input("Source")
                destination = st.text_input("Destination")
                time = st.text_input("Time")
                available_days = st.multiselect("Available Days", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
                total_seats = st.number_input("Total Seats",step=1)

                add_button = st.button("Add Bus")

                if add_button:
                    add_bus(bus_number, source, destination, time, available_days, total_seats)

            elif selected_page=="Update Bus":
                st.subheader("Update Bus")
                bus_number = st.text_input("Bus Number")
                source = st.text_input("Source")
                destination = st.text_input("Destination")
                time = st.text_input("Time")
                available_days = st.multiselect("Available Days", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
                total_seats = st.number_input("Total Seats",step=1)

                update_button = st.button("Update Bus")

                if update_button:
                    update_bus(bus_number, source, destination, time, available_days, total_seats)

            elif selected_page=="Delete Bus":
                st.subheader("Delete Bus")
                bus_number = st.text_input("Bus Number")

                delete_button = st.button("Delete Bus")

                if delete_button:
                    delete_bus(bus_number)

        else :
            st.subheader("Find/Book Bus")
            src = st.text_input("Source")
            dst = st.text_input("Destination")
            travel_date = st.date_input("Select travel date")
            selected_day = travel_date.strftime("%A")
            session_state = st.session_state
            if "game_started" not in session_state:
                session_state.game_started = False
             
            if not st.session_state.game_started :
                find_button = st.button("Filter")
                if find_button:
                    st.session_state.game_started= True
                 

            if st.session_state.game_started:
                buses = filter(src, dst, selected_day)
                if buses:
                    i=2
                    bus=buses[0]
                    st.subheader(f"{(int)(i/2)}. Bus Number: {bus['BusNumber']}")
                    st.write(f"Source: {bus['Source']}")
                    st.write(f"Destination: {bus['Destination']}")
                    st.write(f"Time: {bus['Time']}")
                    st.write(f"Available Seats: {bus['TotalSeats'] - bus['OccupiedSeats']}")

                    book_button = st.button("Book Seat",key=i)
                    if book_button:
                        book_seat(bus['BusNumber'], travel_date, bus['Time'], st.session_state.username)
                        # st.success("Seat booked successfully!")

                    cancel_button = st.button("Cancel Seat",key=i+1)
                    if cancel_button:
                        cancel_seat(bus['BusNumber'], travel_date, bus['Time'], st.session_state.username)
                        # st.success("Seat cancelled successfully!")
                    st.write("------------------------")
                    i=i+2
                    if len(buses)>1:
                        bus=buses[1]
                        st.subheader(f"{(int)(i/2)}. Bus Number: {bus['BusNumber']}")
                        st.write(f"Source: {bus['Source']}")
                        st.write(f"Destination: {bus['Destination']}")
                        st.write(f"Time: {bus['Time']}")
                        st.write(f"Available Seats: {bus['TotalSeats'] - bus['OccupiedSeats']}")

                        book_button = st.button("Book Seat",key=i)
                        if book_button:
                            book_seat(bus['BusNumber'], travel_date, bus['Time'], st.session_state.username)
                            # st.success("Seat booked successfully!")

                        cancel_button = st.button("Cancel Seat",key=i+1)
                        if cancel_button:
                            cancel_seat(bus['BusNumber'], travel_date, bus['Time'], st.session_state.username)
                            # st.success("Seat cancelled successfully!")
                        st.write("------------------------")
                        i=i+2
                    if len(buses)>2:
                        bus=buses[2]
                        st.subheader(f"{(int)(i/2)}. Bus Number: {bus['BusNumber']}")
                        st.write(f"Source: {bus['Source']}")
                        st.write(f"Destination: {bus['Destination']}")
                        st.write(f"Time: {bus['Time']}")
                        st.write(f"Available Seats: {bus['TotalSeats'] - bus['OccupiedSeats']}")

                        book_button = st.button("Book Seat",key=i)
                        if book_button:
                            book_seat(bus['BusNumber'], travel_date, bus['Time'], st.session_state.username)
                            # st.success("Seat booked successfully!")

                        cancel_button = st.button("Cancel Seat",key=i+1)
                        if cancel_button:
                            cancel_seat(bus['BusNumber'], travel_date, bus['Time'], st.session_state.username)
                            # st.success("Seat cancelled successfully!")
                        st.write("------------------------")
                        i=i+2
                    if len(buses)>3:
                        bus=buses[3]
                        st.subheader(f"{(int)(i/2)}. Bus Number: {bus['BusNumber']}")
                        st.write(f"Source: {bus['Source']}")
                        st.write(f"Destination: {bus['Destination']}")
                        st.write(f"Time: {bus['Time']}")
                        st.write(f"Available Seats: {bus['TotalSeats'] - bus['OccupiedSeats']}")

                        book_button = st.button("Book Seat",key=i)
                        if book_button:
                            book_seat(bus['BusNumber'], travel_date, bus['Time'], st.session_state.username)
                            # st.success("Seat booked successfully!")

                        cancel_button = st.button("Cancel Seat",key=i+1)
                        if cancel_button:
                            cancel_seat(bus['BusNumber'], travel_date, bus['Time'], st.session_state.username)
                            # st.success("Seat cancelled successfully!")
                        st.write("------------------------")
                        i=i+2
                    if len(buses)>4:
                        bus=buses[4]
                        st.subheader(f"{(int)(i/2)}. Bus Number: {bus['BusNumber']}")
                        st.write(f"Source: {bus['Source']}")
                        st.write(f"Destination: {bus['Destination']}")
                        st.write(f"Time: {bus['Time']}")
                        st.write(f"Available Seats: {bus['TotalSeats'] - bus['OccupiedSeats']}")

                        book_button = st.button("Book Seat",key=i)
                        if book_button:
                            book_seat(bus['BusNumber'], travel_date, bus['Time'], st.session_state.username)
                            # st.success("Seat booked successfully!")

                        cancel_button = st.button("Cancel Seat",key=i+1)
                        if cancel_button:
                            cancel_seat(bus['BusNumber'], travel_date, bus['Time'], st.session_state.username)
                            # st.success("Seat cancelled successfully!")
                        st.write("------------------------")
                        i=i+2
                else :
                    st.write("No buses found.")

if __name__ == "__main__":
    main()