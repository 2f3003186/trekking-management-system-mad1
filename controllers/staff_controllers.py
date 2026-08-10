from flask import render_template, request, flash, redirect
from model import db, User, Staff, Trek, StaffAssignments, Booking
from main import app

@app.route('/staff/dashboard/<int:staff_id>', methods=["GET", "POST"])
def staff_dashboard(staff_id):
    return render_template("/staff/dashboard.html")