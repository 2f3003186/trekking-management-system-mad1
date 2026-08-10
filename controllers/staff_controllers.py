from flask import render_template, request, flash, redirect
from model import db, User, Staff, Trek, StaffAssignments, Booking
from main import app
from werkzeug.security import generate_password_hash

@app.route('/staff/dashboard/<int:staff_id>', methods=["GET", "POST"])
def staff_dashboard(staff_id):
    staff_member = Staff.query.get(staff_id)
    if not staff_member:
        flash("Staff profile not found", "error")
        return redirect("/login")

    if staff_member.status == "accepted":
        assigned_treks = staff_member.assigned_treks
        treks = [assignment.trek for assignment in assigned_treks]
        trek_count = len(treks)
        open_trek_count = len([trek for trek in treks if trek.status == "open"])
        user_count = sum(len(trek.bookings) for trek in treks if trek.status != "closed")

        return render_template("/staff/dashboard.html",
                               current_user_name=f"{staff_member.user.name}",
                               current_role="staff",
                               trek_count=trek_count,
                               open_trek_count=open_trek_count,
                               user_count=user_count,
                               treks=treks[:4],
                               staff_id=staff_member.id)
    elif staff_member.status == "blacklisted":
        flash("Request Denied !", "danger")
        return redirect("/login")
    elif staff_member.status == "pending":
        flash("Request Pending !\nContact admin for queries")
        return redirect("/login")

@app.route('/staff/treks/<int:staff_id>')
def start_treks(staff_id):
    sm = Staff.query.get(staff_id)
    treks = [a.trek for a in sm.assigned_treks] if sm else []
    return render_template("/staff/treks.html",
                           current_user_name=f"{sm.user.name}" if sm else "Staff",
                           current_role="staff",
                           treks=treks,
                           staff_id=staff_id)

@app.route('/staff/trek/<int:staff_id>/manage/<int:trek_id>', methods=["GET", "POST"])
def manage_trek(staff_id, trek_id):
    trek = Trek.query.get(trek_id)
    sm = Staff.query.get(staff_id)
    if request.method == "POST" and trek:
        trek.status = request.form.get("status")
        db.session.commit()
        flash("Trek Updated !", "success")
        return redirect(f"/staff/dashboard/{staff_id}")
    return render_template("/staff/manage_trek.html",
                           current_user_name=f"{sm.user.name}" if sm else "Staff",
                           current_role="staff",
                           trek=trek,
                           staff_id=staff_id)

@app.route('/staff/trek/<int:staff_id>/mark_started/<int:trek_id>')
def mark_started(trek_id, staff_id):
    trek = Trek.query.get(trek_id)
    if trek:
        trek.status = "started"
        db.session.commit()
        flash("Trek Updated !", "success")
    return redirect(f"/staff/dashboard/{staff_id}")

@app.route('/staff/trek/<int:staff_id>/mark_completed/<int:trek_id>')
def mark_completed(trek_id, staff_id):
    trek = Trek.query.get(trek_id)
    if trek:
        trek.status = "completed"
        db.session.commit()
        flash("Trek Updated !", "success")
    return redirect(f"/staff/dashboard/{staff_id}")

@app.route('/staff/users/<int:staff_id>')
def participants(staff_id):
    sm = Staff.query.get(staff_id)
    treks = [a.trek for a in sm.assigned_treks]
    return render_template("/staff/participants.html",
                           current_user_name=f"{sm.user.name}",
                           current_role="staff",
                           treks=treks,
                           staff_id=staff_id)

@app.route('/staff/users/<int:staff_id>/cancel/<int:booking_id>')
def cancel_participant(staff_id, booking_id):
    booking = Booking.query.get(booking_id)
    if booking and booking.status == "booked":
        booking.status = "cancelled"
        booking.trek.available_slots += 1
        db.session.commit()
        flash("Participant List Updated Successfully", "success")
    return redirect(f"/staff/users/{staff_id}")

@app.route('/staff/users/<int:staff_id>/restore/<int:booking_id>')
def restore_participant(staff_id, booking_id):
    booking = Booking.query.get(booking_id)
    if booking and booking.status == "cancelled":
        if booking.trek.available_slots > 0:
            booking.status = "booked"
            booking.trek.available_slots -= 1
            db.session.commit()
            flash("Participant List Updated Successfully", "success")
        else:
            flash("Cannot restore booking: No available slots remaining.", "danger")
    return redirect(f"/staff/users/{staff_id}")

@app.route('/staff/profile/<int:staff_id>')
def staff_profile(staff_id):
    sm = Staff.query.get(staff_id)
    user = sm.user if sm else None

    return render_template("/staff/profile.html",
                           current_user_name=f"{user.name}" if user else "Staff",
                           current_role="staff",
                           user=user,
                           staff_id=staff_id)

@app.route('/staff/profile/<int:staff_id>/update', methods=["GET", "POST"])
def update_staff_profile(staff_id):
    sm = Staff.query.get(staff_id)
    user = sm.user if sm else None
    if request.method == "POST" and user:
        try:
            name = request.form.get('name')
            password = request.form.get('password')
            email = request.form.get('email')
            ph_num = request.form.get('ph_num')

            user.name = name
            user.password = generate_password_hash(password) if password else user.password
            user.email = email
            user.ph_num = ph_num

            db.session.commit()
            flash("Updation Successful !", "success")
            return redirect(f"/staff/profile/{staff_id}")

        except Exception as e:
            db.session.rollback()
            flash("Could Not Update Profile", "error")
            return redirect(f"/staff/profile/{staff_id}")

    return render_template("/staff/update_profile.html",
                           current_user_name=f"{user.name}" if user else "Staff",
                           current_role="staff",
                           user=user,
                           staff_id=staff_id)