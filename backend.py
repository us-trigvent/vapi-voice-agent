from database import init_db, get_db, Appointment
from pydantic import BaseModel
import datetime as dt
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
import uvicorn
init_db()

class AppointmentRequest(BaseModel):
    patient_name: str
    reason:str
    start_time: dt.datetime

class AppointmentResponse(BaseModel):
    id: int
    patient_name: str
    cancelled:bool
    created_at:dt.datetime
    reason:str | None
    start_time: dt.datetime


class CancelAppointmentRequest(BaseModel):
    patient_name: str
    date: dt.date

class CancelAppointmentResponse(BaseModel):
    cancelled_count: int

app = FastAPI()

@app.post("/schedule-appointment/")
def schedule_appointment(request: AppointmentRequest,db: Session = Depends(get_db)):
    new_appointment = Appointment(
        patient_name = request.patient_name,
        reason=request.reason,
        start_time=request.start_time,
    )
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    new_appointment_return_obj = AppointmentResponse(
    id=new_appointment.id,
    patient_name=new_appointment.patient_name,
    reason=new_appointment.reason,
    start_time=new_appointment.start_time,
    cancelled=new_appointment.cancelled,
    created_at=new_appointment.created_at
)
    return new_appointment_return_obj

@app.post("/cancel-appointment/")
def cancel_appointment(request:CancelAppointmentRequest,db:Session=Depends(get_db)):
    start_dt  =dt.datetime.combine(request.date,dt.time.min)
    end_dt = start_dt + dt.timedelta(days=1)

    result = db.execute(
        select(Appointment)
        .where(Appointment.patient_name == request.patient_name)
        .where(Appointment.start_time>=start_dt)
        .where(Appointment.start_time<=end_dt)
        .where(Appointment.cancelled == False)
    )
    appointments = result.scalars().all()
    if not appointments: 
        raise HTTPException(status_code=404, detail="No matching appointment for the detials found in our system")
    
    for appointment in appointments:
        appointment.cancelled = True

    db.commit()

    return CancelAppointmentResponse(cancelled_count=len(appointments))

@app.get("/list-appointments/")
def list_appointments(date: dt.date, db: Session = Depends(get_db)):
    start_dt = dt.datetime.combine(date, dt.time.min)
    end_dt = start_dt + dt.timedelta(days=1)

    result = db.execute(
        select(Appointment)
        .where(Appointment.cancelled == False)
        .where(Appointment.start_time >= start_dt)
        .where(Appointment.start_time < end_dt)
        .order_by(Appointment.start_time.asc())
    )

    appointments = result.scalars().all()

    return [
        {
            "id": a.id,
            "patient_name": a.patient_name,
            "reason": a.reason,
            "start_time": str(a.start_time),
            "cancelled": a.cancelled,
            "created_at": str(a.created_at),
        }
        for a in appointments
    ]

if __name__ == "__main__":
    uvicorn.run("backend:app", host="127.0.0.1", port=4444, reload=True)