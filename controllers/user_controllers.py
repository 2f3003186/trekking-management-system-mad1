from datetime import datetime
from flask import render_template, request, flash, redirect
from model import db, User, Staff, Trek, StaffAssignments, Booking
from main import app
from werkzeug.security import generate_password_hash


@app.route('/user/dashboard/<int:user_id>', methods=["GET", "POST"])
def user_dashboard(user_id):
    user = User.query.get(user_id)
    bookings = user.bookings
    locations = list({trek.location for trek in Trek.query.all()})

    query = request.args.get('q', '')
    difficulty = request.args.get('difficulty', '')
    location = request.args.get('location', '')

    treks_query = Trek.query.filter(Trek.status == "open", Trek.available_slots > 0)
    if query:
        treks_query = treks_query.filter(Trek.name.ilike(f'%{query}%'))
    if difficulty:
        treks_query = treks_query.filter(Trek.difficulty == difficulty)
    if location:
        treks_query = treks_query.filter(Trek.location == location)

    available_treks = treks_query.all()
    return render_template(
        "/user/dashboard.html",
        user=user,
        bookings=bookings,
        treks=available_treks,
        locations=locations
    )


@app.route('/user/profile/<int:user_id>')
def user_profile(user_id):
    user = User.query.get(user_id)

    return render_template(
        "/user/profile.html",
        current_user_name=f"{user.name}",
        current_role="user",
        user=user
    )


@app.route('/user/profile/<int:user_id>/update', methods=["GET", "POST"])
def update_user_profile(user_id):
    user = User.query.get(user_id)
    if request.method == "POST":
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
            return redirect(f"/user/profile/{user.id}")

        except Exception as e:
            db.session.rollback()
            flash(f"Could Not Update Profile \n{e}", "error")
            return redirect(f"/user/profile/{user.id}")

    return render_template(
        "/user/update_profile.html",
        current_user_name=f"{user.name}",
        current_role="user",
        user=user
    )


@app.route('/user/treks/<int:user_id>')
def user_treks(user_id):
    user = User.query.get(user_id)
    treks = Trek.query.filter(Trek.status.in_(["open", "started"])).all()

    return render_template(
        "/user/treks.html",
        current_user_name=f"{user.name}",
        current_role="user",
        user=user,
        treks=treks
    )


@app.route('/user/trek/<int:user_id>/<int:trek_id>')
def trek_details(trek_id, user_id):
    trek = Trek.query.get(trek_id)
    user = User.query.get(user_id)

    return render_template(
        "/user/trek.html",
        current_user_name=f"{user.name}",
        current_role="user",
        user=user,
        trek=trek
    )


@app.route('/user/trek/book/<int:user_id>/<int:trek_id>', methods=["POST"])
def book_trek(user_id, trek_id):
    trek = Trek.query.get(trek_id)

    existing = Booking.query.filter_by(trek_id=trek_id, user_id=user_id, status="Booked").first()
    if not existing and trek.status.lower() == "open" and trek.available_slots > 0:
        booking = Booking(user_id=user_id, trek_id=trek_id, date=datetime.now(), status="Booked")
        trek.available_slots -= 1
        db.session.add(booking)
        db.session.commit()

    return redirect(f"/user/trek/{user_id}/{trek_id}")


@app.route('/user/trek/cancel/<int:user_id>/<int:trek_id>', methods=["POST"])
def cancel_booking(user_id, trek_id):
    trek = Trek.query.get(trek_id)
    booking = Booking.query.filter_by(trek_id=trek_id, user_id=user_id, status="Booked").first()

    if booking:
        booking.status = "Cancelled"
        trek.available_slots += 1
        db.session.commit()

    return redirect(f"/user/trek/{user_id}/{trek_id}")

@app.route('/user/bookings/<int:user_id>')
def user_bookings(user_id):
    user = User.query.get(user_id)
    bookings = user.bookings

    return render_template(
        "/user/bookings.html",
        current_user_name=f"{user.name}",
        current_role="user",
        user=user,
        bookings=bookings
    )

@app.route('/user/trek_history/<int:user_id>')
def user_trek_history(user_id):
    user = User.query.get(user_id)
    
    # Fetches bookings where the trek was completed
    completed_bookings = Booking.query.filter(
        Booking.user_id == user_id,
        Booking.status == "Completed"
    ).all()

    return render_template(
        "/user/trek_history.html",
        current_user_name=f"{user.name}",
        current_role="user",
        user=user,
        history=completed_bookings
    )