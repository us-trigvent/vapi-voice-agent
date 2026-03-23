import streamlit as st
import datetime as dt
import requests
from datetime import datetime
st.title("America Hospital Appointemnt Booking Portal")
base_url = st.text_input("Backend URL", "http://localhost:4444").rstrip("/")


st.header("Schedule Appointment")
patient_name = st.text_input("Patient Name", key="sched_name")
reason = st.text_input("Reason", key="sched_reason")
start_date = st.date_input("Start Date", key="sched_date")
start_time = st.time_input("Start Time", key="sched_time")

if st.button("Schedule"):
    # Combine date and time to match the expected backend format [5]
    start_datetime = datetime.combine(start_date, start_time).isoformat()
    
    # Data contract: patient_name, reason, and start_time [5, 6]
    payload = {
        "patient_name": patient_name,
        "reason": reason,
        "start_time": start_datetime
    }
    
    try:
        response = requests.post(f"{base_url}/schedule-appointment/", json=payload)
        if response.status_code == 200:
            st.success("Appointment Scheduled Successfully!") 
            st.json(response.json()) # Display return details like Appointment ID [8, 9]
        else:
            st.error(f"Error: {response.status_code}")
    except Exception as e:
        st.error(f"Connection failed: {e}")

# --- SECTION 2: CANCEL APPOINTMENT --- [10]
st.header("Cancel Appointment")
cancel_name = st.text_input("Patient Name to Cancel", key="cancel_name")
cancel_date = st.date_input("Date of Appointment", key="cancel_date")

if st.button("Cancel Appointment"):
    # Data contract: patient_name and date [10, 11]
    payload = {
        "patient_name": cancel_name,
        "date": str(cancel_date)
    }
    
    try:
        response = requests.post(f"{base_url}/cancel-appointment/", json=payload)
        if response.status_code == 200:
            cancel_count = response.json().get("cancelled_count", 0) 
            if cancel_count > 0:
                st.success(f"Successfully cancelled {cancel_count} appointment(s).") 
            else:
                st.warning("No matching appointment found to cancel.")
        else:
            st.error("Failed to cancel appointment.")
    except Exception as e:
        st.error(f"Connection failed: {e}")

# --- SECTION 3: CHECK APPOINTMENTS --- [12]
st.header("Check Appointments")
check_date = st.date_input("Date to Check", key="check_date")

if st.button("Check Appointments"):
    # Data contract: Only requires the date [3, 12]
    params = {"date": str(check_date)}
    
    try:
        # This uses a GET request to retrieve data [15, 16]
        response = requests.get(f"{base_url}/list-appointments/", params=params)
        if response.status_code == 200:
            appointments = response.json()
            if appointments:
                st.write(f"Appointments for {check_date}:")
                st.table(appointments) 
            else:
                st.info("No appointments found for this date.")
        else:
            st.error("Could not load appointments.")
    except Exception as e:
        st.error(f"Connection failed: {e}")