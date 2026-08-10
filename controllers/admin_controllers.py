from flask import render_template, request, flash, redirect
from sqlalchemy import cast, String
from model import db, User, Staff, Trek, StaffAssignments, Booking
from main import app
from datetime import datetime

@app.route('/admin/dashboard', methods=["GET", "POST"])
def admin_dashboard():
    user_count = User.query.filter_by(role="user").count()
    staff_count = Staff.query.count()
    trek_count = Trek.query.count()
    booking_count = Booking.query.count()
    recent_bookings = Booking.query.order_by(Booking.id.desc()).limit(5).all()
    admin_user = User.query.filter_by(role="admin").first()

    return render_template("/admin/dashboard.html",
                           user_count=user_count,
                           staff_count=staff_count,
                           trek_count=trek_count,
                           booking_count=booking_count,
                           bookings=recent_bookings,
                           current_user_name=admin_user.name if admin_user else "Admin",
                           current_role="admin")

@app.route('/admin/trek/create', methods=["GET", "POST"])
def create_trek():
    admin_user = User.query.filter_by(role="admin").first()
    if request.method == "POST":
        name = request.form.get('name')
        location = request.form.get('location')
        difficulty = request.form.get('difficulty')
        duration = int(request.form.get('duration'))
        available_slots = int(request.form.get('slots'))
        status = request.form.get('status')
        start_date = datetime.strptime(request.form.get('start_date'), "%Y-%m-%d").date()
        end_date = datetime.strptime(request.form.get('end_date'), "%Y-%m-%d").date()
        description = request.form.get('description')
        trek = Trek(
            name=name,
            location=location,
            difficulty=difficulty,
            duration=duration,
            available_slots=available_slots,
            status=status,
            start_date=start_date,
            end_date=end_date,
            description=description
        )
        try:
            db.session.add(trek)
            db.session.commit()
            for staff_member_id in request.form.getlist('staff'):
                assignment = StaffAssignments(
                    staff_id=staff_member_id,
                    trek_id=trek.id
                )
                db.session.add(assignment)
            db.session.commit()
            flash("Trek added successfully !", "success")
            
        except Exception as e:
            db.session.rollback()
            flash("Trek could not be added !", "error")
        
        return redirect("/admin/treks")
    return render_template("/admin/create_trek.html",
                           current_user_name=admin_user.name if admin_user else "Admin",
                           current_role="admin",
                           staff=Staff.query.filter_by(status="accepted").all())

@app.route('/admin/trek/delete/<int:trek_id>')
def delete_trek(trek_id):
    trek = Trek.query.get(trek_id)
    if trek:
        try:
            db.session.delete(trek)
            db.session.commit()
            flash("Trek deleted Successfully !", "success")
        except Exception as e:
            db.session.rollback()
            flash("Could not delete trek", "error")
    return redirect("/admin/treks")

@app.route('/admin/trek/update/<int:trek_id>', methods=["GET", "POST"])
def update_trek(trek_id):
    trek = Trek.query.get(trek_id)
    admin_user = User.query.filter_by(role="admin").first()
    if request.method == "POST":
        try:
            trek.name = request.form.get('name')
            trek.location = request.form.get('location')
            trek.difficulty = request.form.get('difficulty')
            trek.duration = int(request.form.get('duration'))
            trek.available_slots = int(request.form.get('slots'))
            trek.status = request.form.get('status')
            trek.start_date = datetime.strptime(request.form.get('start_date'), "%Y-%m-%d").date()
            trek.end_date = datetime.strptime(request.form.get('end_date'), "%Y-%m-%d").date()
            trek.description = request.form.get('description')
            assigned_staff = list(map(int, request.form.getlist('staff')))

            for staff_member_id in assigned_staff:
                if staff_member_id not in [assignment.staff_id for assignment in trek.assigned_staff]:
                    assignment = StaffAssignments(
                        staff_id=staff_member_id,
                        trek_id=trek.id
                    )
                    db.session.add(assignment)

            for assignment in list(trek.assigned_staff):
                if assignment.staff_id not in assigned_staff:
                    db.session.delete(assignment)

            db.session.commit()
            flash("Trek updated Successfully !", "success")

        except Exception as e:
            db.session.rollback()
            flash("Trek Could not be Updated !", "error")

        return redirect("/admin/treks")

    return render_template("/admin/update_trek.html",
                           current_user_name=admin_user.name if admin_user else "Admin",
                           current_role="admin",
                           trek=trek,
                           assigned_staff_id=[assignment.staff_id for assignment in trek.assigned_staff],
                           staff=Staff.query.filter_by(status="accepted").all())

@app.route('/admin/treks', methods=["GET", "POST"])
def treks():
    query = request.args.get('q', '')
    admin_user = User.query.filter_by(role="admin").first()
    result = []
    if query:
        if query.isdigit():
            result = Trek.query.filter(cast(Trek.id, String).like(f"%{query}%")).all()
        else:
            result = Trek.query.filter(Trek.name.ilike(f"%{query}%")).all()
    else:
        result = Trek.query.all()

    return render_template("/admin/treks.html",
                           current_user_name=admin_user.name if admin_user else "Admin",
                           current_role="admin",
                           result=result,
                           query=query)

@app.route('/admin/staff')
def manage_staff():
    query = request.args.get('q', '')
    admin_user = User.query.filter_by(role="admin").first()
    result = []
    if query:
        if query.isdigit():
            result = Staff.query.filter(cast(Staff.id, String).like(f"%{query}%")).all()
        else:
            result = Staff.query.join(User).filter(User.name.ilike(f"%{query}%")).all()
    else:
        result = Staff.query.all()

    return render_template("/admin/manage_staff.html",
                           current_user_name=admin_user.name if admin_user else "Admin",
                           current_role="admin",
                           staff=result,
                           query=query)

@app.route('/admin/staff/accept/<int:staff_id>')
def accept_staff(staff_id):
    staff_member = Staff.query.get(staff_id)
    if staff_member:
        staff_member.status = "accepted"
        db.session.commit()
        flash(f"Staff member {staff_member.user.name} accepted successfully !", "success")
    return redirect("/admin/staff")

@app.route('/admin/staff/blacklist/<int:staff_id>')
def blacklist_staff(staff_id):
    staff_member = Staff.query.get(staff_id)
    if staff_member:
        staff_member.status = "blacklisted"
        db.session.commit()
        flash(f"Staff member {staff_member.user.name} blacklisted successfully !", "success")
    return redirect("/admin/staff")

@app.route('/admin/staff/reject/<int:staff_id>')
def reject_staff(staff_id):
    staff_member = Staff.query.get(staff_id)
    if staff_member:
        db.session.delete(staff_member)
        db.session.commit()
        flash("Staff request rejected successfully !", "success")
    return redirect("/admin/staff")

@app.route('/admin/users')
def manage_users():
    query = request.args.get('q', '')
    admin_user = User.query.filter_by(role="admin").first()
    result = []
    if query:
        if query.isdigit():
            result = User.query.filter(cast(User.id, String).like(f"%{query}%")).filter_by(role="user").all()
        else:
            result = User.query.filter(User.name.ilike(f"%{query}%")).filter_by(role="user").all()
    else:
        result = User.query.filter_by(role="user").all()

    return render_template("/admin/manage_users.html",
                           current_user_name=admin_user.name if admin_user else "Admin",
                           current_role="admin",
                           result=result,
                           query=query)

@app.route('/admin/user/blacklist/<int:user_id>')
def blacklist_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.status = "blacklisted"
        db.session.commit()
        flash(f"User {user.name} blacklisted successfully !", "success")
    return redirect("/admin/users")

@app.route('/admin/user/accept/<int:user_id>')
def accept_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.status = "accepted"
        db.session.commit()
        flash(f"User {user.name} accepted successfully !", "success")
    return redirect("/admin/users")

@app.route('/admin/bookings')
def get_bookings():
    query = request.args.get('q', '')
    admin_user = User.query.filter_by(role="admin").first()
    result = []
    if query:
        if query.isdigit():
            result = Booking.query.filter(cast(Booking.id, String).like(f"%{query}%")).all()
        else:
            result = Booking.query.join(User).filter(User.name.ilike(f"%{query}%")).all()
    else:
        result = Booking.query.all()

    return render_template("/admin/bookings.html",
                            current_user_name=admin_user.name if admin_user else "Admin",
                            current_role="admin",
                            result=result,
                            query=query)