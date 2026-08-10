from flask import render_template, request, flash, redirect
from model import db, User, Staff, Trek, StaffAssignments, Booking
from main import app
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/', methods=["GET", "POST"])
def home():
    return render_template("index.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        users = User.query.all()
        for user in users:
            if check_password_hash(user.password, password) and user.email == email:

                if user.role == "admin":
                    return redirect('/admin/dashboard')
                
                if user.role == "staff":
                    staff_member = Staff.query.filter_by(user_id=user.id)
                    return redirect(f'/staff/dashboard/{staff_member.id}')

                if user.role == "user":
                    return redirect(f'/user/dashboard/{user.id}')

        else:
            flash("Account with enetered details not found !", "error")

    return render_template("login.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        ph_num = request.form.get('ph_num')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        role = request.form.get('role')

        if password != confirm_password:
            flash("Password and Confirm Password must be same !", "danger")
            return redirect("/register")

        if ph_num and len(ph_num) != 10:
            flash("Invalid Phone Number !", "danger")
            return redirect("/register")

        new_user = User(
            name=name,
            email=email,
            ph_num = ph_num,
            role=role,
            password=generate_password_hash(password)
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration Successful! You can now Login with your credentials", "success")
        return redirect('/login')

    return render_template("register.html")

