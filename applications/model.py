from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True)
    role = db.Column(db.String, nullable=False)
    ph_num = db.Column(db.String, unique=True)
    time_created = db.Column(db.DateTime, default=datetime.now)

    bookings = db.relationship("Booking", back_populates="user")

class Staff(db.Model):
    __tablename__ = "staff"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    status = db.Column(db.String, nullable=False, default="Pending")

    assigned_trek = db.relationship("StaffAssignments", back_populates="staff")

class StaffAssignments(db.Model):
    __tablename__ = "staff_assignments"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    staff_id = db.Column(db.Integer, db.ForeignKey("staff.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("trek.id"), nullable=False)

    staff = db.relationship("Staff", back_populates="assigned_trek")
    trek = db.relationship("Trek", back_populates="assigned_staff")

class Trek(db.Model):
    __tablename__ = "trek"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    difficulty = db.Column(db.String, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, default="Open")
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

    bookings = db.relationship("Booking", back_populates="trek")
    assigned_staff = db.relationship("StaffAssignments", back_populates="trek")


class Booking(db.Model):
    __tablename__ = "booking"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("trek.id"), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String, default="Booked")

    trek = db.relationship("Trek", back_populates="bookings")
    user = db.relationship("User", back_populates="bookings")



