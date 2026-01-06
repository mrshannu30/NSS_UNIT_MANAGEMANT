from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
import bcrypt
import os
from datetime import datetime, timedelta
from functools import wraps
import qrcode
import io
import base64
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'nss_secret_key_change_this_in_production'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '3015'
app.config['MYSQL_DB'] = 'nss_management'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Login Required Decorator
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please login first', 'warning')
                return redirect(url_for('login'))
            if role and session.get('user_type') != role:
                flash('Unauthorized access', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Helper function to log activities
def log_activity(user_type, user_id, action, details='', ip_address=''):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO activity_log (user_type, user_id, action, details, ip_address)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_type, user_id, action, details, ip_address))
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        print(f"Error logging activity: {e}")

# Routes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        
        if user_type == 'admin':
            admin_id = request.form.get('admin_id')
            password = request.form.get('password')
            
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM admins WHERE admin_id = %s AND is_active = TRUE", (admin_id,))
            admin = cur.fetchone()
            cur.close()
            
            if admin and bcrypt.checkpw(password.encode('utf-8'), admin['password'].encode('utf-8')):
                session.permanent = True
                session['user_id'] = admin['id']
                session['user_type'] = 'admin'
                session['username'] = admin['username']
                
                # Update last login
                cur = mysql.connection.cursor()
                cur.execute("UPDATE admins SET last_login = NOW() WHERE id = %s", (admin['id'],))
                mysql.connection.commit()
                cur.close()
                
                log_activity('Admin', admin['id'], 'Login', f"Admin {admin['username']} logged in", request.remote_addr)
                flash('Welcome Admin!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid admin credentials', 'danger')
        
        elif user_type == 'volunteer':
            suc_code = request.form.get('suc_code')
            password = request.form.get('password')
            
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM volunteers WHERE suc_code = %s AND is_active = TRUE", (suc_code,))
            volunteer = cur.fetchone()
            cur.close()
            
            if volunteer:
                if not volunteer['is_approved']:
                    flash('Your registration is pending approval', 'warning')
                elif bcrypt.checkpw(password.encode('utf-8'), volunteer['password'].encode('utf-8')):
                    session.permanent = True
                    session['user_id'] = volunteer['id']
                    session['user_type'] = 'volunteer'
                    session['username'] = volunteer['full_name']
                    session['suc_code'] = volunteer['suc_code']
                    
                    # Update last login
                    cur = mysql.connection.cursor()
                    cur.execute("UPDATE volunteers SET last_login = NOW() WHERE id = %s", (volunteer['id'],))
                    mysql.connection.commit()
                    cur.close()
                    
                    log_activity('Volunteer', volunteer['id'], 'Login', f"Volunteer {volunteer['full_name']} logged in", request.remote_addr)
                    flash(f'Welcome {volunteer["full_name"]}!', 'success')
                    return redirect(url_for('volunteer_dashboard'))
                else:
                    flash('Invalid password', 'danger')
            else:
                flash('Invalid SUC code', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        data = {
            'suc_code': request.form.get('suc_code'),
            'full_name': request.form.get('full_name'),
            'father_name': request.form.get('father_name'),
            'mother_name': request.form.get('mother_name'),
            'blood_group': request.form.get('blood_group'),
            'group_name': request.form.get('group_name'),
            'roll_no': request.form.get('roll_no'),
            'year': request.form.get('year'),
            'date_of_birth': request.form.get('date_of_birth'),
            'adhaar_number': request.form.get('adhaar_number'),
            'mobile_number': request.form.get('mobile_number'),
            'parent_mobile_number': request.form.get('parent_mobile_number'),
            'email': request.form.get('email'),
            'gender': request.form.get('gender'),
            'section': request.form.get('section'),
            'community': request.form.get('community')
        }
        
        # Default password: last 4 digits of SUC code
        default_password = data['suc_code'][-4:]
        hashed_password = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt())
        
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO volunteers (
                    suc_code, password, full_name, father_name, mother_name, 
                    blood_group, group_name, roll_no, year, date_of_birth, 
                    adhaar_number, mobile_number, parent_mobile_number, email, 
                    gender, section, community
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                data['suc_code'], hashed_password, data['full_name'], data['father_name'],
                data['mother_name'], data['blood_group'], data['group_name'], data['roll_no'],
                data['year'], data['date_of_birth'], data['adhaar_number'], data['mobile_number'],
                data['parent_mobile_number'], data['email'], data['gender'], data['section'],
                data['community']
            ))
            mysql.connection.commit()
            cur.close()
            
            flash('Registration successful! Your password is the last 4 digits of your SUC code. Please wait for admin approval.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'danger')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    user_type = session.get('user_type')
    user_id = session.get('user_id')
    username = session.get('username')
    
    if user_type and user_id:
        log_activity(user_type.capitalize(), user_id, 'Logout', f"{username} logged out", request.remote_addr)
    
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))

# Admin Routes

@app.route('/admin/dashboard')
@login_required(role='admin')
def admin_dashboard():
    cur = mysql.connection.cursor()
    
    # Get statistics
    cur.execute("SELECT * FROM volunteer_stats")
    volunteer_stats = cur.fetchone()
    
    cur.execute("SELECT * FROM event_stats")
    event_stats = cur.fetchone()
    
    cur.execute("SELECT COUNT(*) as total_attendance FROM attendance")
    attendance_stats = cur.fetchone()
    
    # Recent volunteers
    cur.execute("""
        SELECT id, full_name, suc_code, email, created_at 
        FROM volunteers 
        WHERE is_approved = FALSE 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    pending_volunteers = cur.fetchall()
    
    # Upcoming events
    cur.execute("""
        SELECT * FROM events 
        WHERE event_date >= CURDATE() AND is_active = TRUE 
        ORDER BY event_date ASC 
        LIMIT 5
    """)
    upcoming_events = cur.fetchall()
    
    cur.close()
    
    return render_template('admin/dashboard.html', 
                         volunteer_stats=volunteer_stats,
                         event_stats=event_stats,
                         attendance_stats=attendance_stats,
                         pending_volunteers=pending_volunteers,
                         upcoming_events=upcoming_events)

@app.route('/admin/volunteers')
@login_required(role='admin')
def manage_volunteers():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM volunteers ORDER BY created_at DESC")
    volunteers = cur.fetchall()
    cur.close()
    return render_template('admin/manage_volunteers.html', volunteers=volunteers)

@app.route('/admin/volunteer/approve/<int:volunteer_id>')
@login_required(role='admin')
def approve_volunteer(volunteer_id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE volunteers SET is_approved = TRUE WHERE id = %s", (volunteer_id,))
    mysql.connection.commit()
    cur.close()
    
    log_activity('Admin', session['user_id'], 'Approve Volunteer', f"Approved volunteer ID: {volunteer_id}", request.remote_addr)
    flash('Volunteer approved successfully', 'success')
    return redirect(url_for('manage_volunteers'))

@app.route('/admin/events')
@login_required(role='admin')
def manage_events():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM events ORDER BY event_date DESC")
    events = cur.fetchall()
    cur.close()
    return render_template('admin/manage_events.html', events=events)

@app.route('/admin/event/create', methods=['GET', 'POST'])
@login_required(role='admin')
def create_event():
    if request.method == 'POST':
        event_data = {
            'event_name': request.form.get('event_name'),
            'event_description': request.form.get('event_description'),
            'event_date': request.form.get('event_date'),
            'event_time': request.form.get('event_time'),
            'venue': request.form.get('venue'),
            'event_type': request.form.get('event_type'),
            'coordinator_name': request.form.get('coordinator_name'),
            'max_participants': request.form.get('max_participants')
        }
        
        # Generate unique QR code
        qr_code = f"EVENT_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO events (
                    event_name, event_description, event_date, event_time, 
                    venue, event_type, coordinator_name, max_participants, 
                    qr_code, created_by
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                event_data['event_name'], event_data['event_description'],
                event_data['event_date'], event_data['event_time'],
                event_data['venue'], event_data['event_type'],
                event_data['coordinator_name'], event_data['max_participants'],
                qr_code, session['user_id']
            ))
            mysql.connection.commit()
            cur.close()
            
            log_activity('Admin', session['user_id'], 'Create Event', f"Created event: {event_data['event_name']}", request.remote_addr)
            flash('Event created successfully', 'success')
            return redirect(url_for('manage_events'))
        except Exception as e:
            flash(f'Error creating event: {str(e)}', 'danger')
    
    return render_template('admin/manage_events.html')

@app.route('/admin/attendance')
@login_required(role='admin')
def view_attendance():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT a.*, v.full_name, v.suc_code, e.event_name, e.event_date
        FROM attendance a
        JOIN volunteers v ON a.volunteer_id = v.id
        JOIN events e ON a.event_id = e.id
        ORDER BY a.marked_at DESC
    """)
    attendance_records = cur.fetchall()
    cur.close()
    return render_template('admin/attendance.html', attendance_records=attendance_records)

@app.route('/api/qr/generate/<int:event_id>')
@login_required(role='admin')
def generate_qr(event_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT qr_code, event_name FROM events WHERE id = %s", (event_id,))
    event = cur.fetchone()
    cur.close()
    
    if event:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(event['qr_code'])
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return jsonify({'success': True, 'qr_code': img_str, 'event_name': event['event_name']})
    return jsonify({'success': False, 'message': 'Event not found'})

# Volunteer Routes

@app.route('/volunteer/dashboard')
@login_required(role='volunteer')
def volunteer_dashboard():
    cur = mysql.connection.cursor()
    
    # Get volunteer info
    cur.execute("SELECT * FROM volunteers WHERE id = %s", (session['user_id'],))
    volunteer = cur.fetchone()
    
    # Get upcoming events
    cur.execute("""
        SELECT * FROM events 
        WHERE event_date >= CURDATE() AND is_active = TRUE 
        ORDER BY event_date ASC 
        LIMIT 10
    """)
    upcoming_events = cur.fetchall()
    
    # Get attendance summary
    cur.execute("""
        SELECT COUNT(*) as total_events_attended 
        FROM attendance 
        WHERE volunteer_id = %s
    """, (session['user_id'],))
    attendance_summary = cur.fetchone()
    
    cur.close()
    
    return render_template('volunteer/dashboard.html', 
                         volunteer=volunteer,
                         upcoming_events=upcoming_events,
                         attendance_summary=attendance_summary)

@app.route('/volunteer/attendance')
@login_required(role='volunteer')
def volunteer_attendance():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT a.*, e.event_name, e.event_date, e.venue
        FROM attendance a
        JOIN events e ON a.event_id = e.id
        WHERE a.volunteer_id = %s
        ORDER BY a.marked_at DESC
    """, (session['user_id'],))
    attendance_records = cur.fetchall()
    cur.close()
    return render_template('volunteer/attendance.html', attendance_records=attendance_records)

@app.route('/volunteer/change-password', methods=['GET', 'POST'])
@login_required(role='volunteer')
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return redirect(url_for('change_password'))
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT password FROM volunteers WHERE id = %s", (session['user_id'],))
        volunteer = cur.fetchone()
        
        if volunteer and bcrypt.checkpw(current_password.encode('utf-8'), volunteer['password'].encode('utf-8')):
            new_hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            cur.execute("UPDATE volunteers SET password = %s, password_changed = TRUE WHERE id = %s", 
                       (new_hashed, session['user_id']))
            mysql.connection.commit()
            cur.close()
            
            log_activity('Volunteer', session['user_id'], 'Password Changed', 'Volunteer changed password', request.remote_addr)
            flash('Password changed successfully', 'success')
            return redirect(url_for('volunteer_dashboard'))
        else:
            flash('Current password is incorrect', 'danger')
        
        cur.close()
    
    return render_template('volunteer/change_password.html')

@app.route('/api/attendance/mark', methods=['POST'])
@login_required(role='volunteer')
def mark_attendance():
    qr_code = request.json.get('qr_code')
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM events WHERE qr_code = %s AND is_active = TRUE", (qr_code,))
    event = cur.fetchone()
    
    if event:
        try:
            cur.execute("""
                INSERT INTO attendance (volunteer_id, event_id, marked_by)
                VALUES (%s, %s, 'QR_SCAN')
            """, (session['user_id'], event['id']))
            mysql.connection.commit()
            cur.close()
            
            log_activity('Volunteer', session['user_id'], 'Attendance Marked', f"Marked attendance for event ID: {event['id']}", request.remote_addr)
            return jsonify({'success': True, 'message': 'Attendance marked successfully'})
        except Exception as e:
            return jsonify({'success': False, 'message': 'Attendance already marked or error occurred'})
    
    cur.close()
    return jsonify({'success': False, 'message': 'Invalid QR code'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)