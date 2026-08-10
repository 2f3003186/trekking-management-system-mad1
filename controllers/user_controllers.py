from flask import render_template, request, flash, redirect
from model import db, User, Staff, Trek, StaffAssignments, Booking
from main import app

@app.route('/user/dashboard/<int:user_id>', methods=["GET", "POST"])
def user_dashboard(user_id):
    return render_template("/user/dashboard.html")