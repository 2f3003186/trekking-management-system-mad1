from flask import render_template, request, flash, redirect
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

    return render_template("/admin/dashboard.html",
                           user_count=user_count,
                           staff_count=staff_count,
                           trek_count=trek_count,
                           booking_count=booking_count,
                           bookings=recent_bookings,
                           current_user_name=User.query.get(1).name,
                           current_role="admin")

@app.route('/admin/trek/create', methods=["GET", "POST"])
def create_trek():
    if request.method == "POST":
        name = request.form.get('name')
        location = request.form.get('location')
        difficulty = request.form.get('difficulty')
        duration = int(request.form.get('duration'))
        available_slots = int(request.form.get('slots'))
        status = request.form.get('status')
        start_date = datetime.strptime(request.form.get('start_date'), "%Y-%m-%d").date()
        end_date = datetime.strptime(request.form.get('end_date'), "%Y-%m-%d").date()
        trek = Trek(
            name=name,
            location=location,
            difficulty=difficulty,
            duration=duration,
            available_slots=available_slots,
            status=status,
            start_date=start_date,
            end_date=end_date
        )
        try:
            db.session.add(trek)
            db.session.commit()
            for staff_member_id in request.form.getlist('staff'):
                assignment = StaffAssignments(
                    staff_id = staff_member_id,
                    trek_id = trek.id
                )
                db.session.add(assignment)
            db.session.commit()
            flash("Trek added successfully !", "success")
            
        except Exception as e:
            db.session.rollback()
            flash(f"Trek could not be added !\n {e}", "error")
        
        return redirect("/admin/treks")
    return render_template("/admin/create_trek.html", current_user_name=User.query.get(1).name,current_role="admin",staff=Staff.query.all())

@app.route('/admin/trek/delete/<int:trek_id>')
def delete_trek(trek_id):
    trek = Trek.query.get(trek_id)
    try:
        db.session.delete(trek)
        db.session.commit()
        flash("Trek deleted Successfully !")

    except Exception as e:
        flash(f"Could not delete trek\n{e}", "error")
    return redirect("/admin/treks")

@app.route('/admin/trek/update/<int:trek_id>', methods=["GET", "POST"])
def update_trek(trek_id):
    trek = Trek.query.get(trek_id)
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
            assigned_staff = request.form.getlist('staff')
            for staff_member_id in assigned_staff:
                if staff_member_id not in [assignment.staff_id for assignment in trek.assigned_staff]:
                    assignment = StaffAssignments(
                        staff_id = staff_member_id,
                        trek_id = trek.id
                    )
                    db.session.add(assignment)

            for assignment in trek.assigned_staff:
                if assignment.staff_id not in [assigned_staff]:
                    assignment = StaffAssignments.query.get(assignment.staff_id)
                    db.session.delete(assignment) 

            db.session.commit()
            flash("Trek updated Successfully !", "success")

        except Exception as e:
            db.session.rollback()
            flash(f"Trek Could not be Updated !\n{e}", "error")

        return redirect("/admin/treks")

        
    return render_template("/admin/update_trek.html", current_user_name=User.query.get(1).name,current_role="admin", trek=trek)

@app.route('/admin/treks')
def treks():
    query = request.args.get('q', '')
    result = []
    if query:
        if query.isdigit():
            result = (Trek.query.filter(Trek.id.like(f"%{query}%")).all())

        else:
            result = (Trek.query.filter(Trek.name.ilike(f"%{query}%")).all())

    else:
        result = (Trek.query.all())

    return render_template("/admin/treks.html",
                           current_user_name=User.query.get(1).name,
                           current_role="admin",
                           result=result,
                            query=query)

@app.route('/admin/staff')
def manage_staff():
    return render_template("/admin/manage_staff.html", current_user_name=User.query.get(1).name, current_role="admin")

@app.route('/admin/users')
def manage_users():
    return render_template("/admin/manage_users.html", current_user_name=User.query.get(1).name, current_role="admin")

@app.route('/admin/bookings')
def get_bookings():
    return render_template("/admin/bookings.html", current_user_name=User.query.get(1).name, current_role="admin")
