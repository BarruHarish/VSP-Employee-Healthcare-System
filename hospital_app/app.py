from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime
import uuid

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = "super_secret_key" # Replace with a secure random key in production
Session(app)

UPLOAD_FOLDER = os.path.join('static', 'uploads', 'profiles')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database helper function
def get_db_connection():
    conn = sqlite3.connect('hospital.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- Authentication & General Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        employee_name = request.form['name']
        employee_id = request.form['employee_id']
        mobile_number = request.form['mobile_number']
        password = request.form['password']
        
        hashed_pw = generate_password_hash(password)
        
        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO employees (employee_name, employee_id, mobile, password, department, designation, email, dob, gender, blood_group, address, status, profile_photo) 
                VALUES (?, ?, ?, ?, '', '', '', '', '', '', '', 'Active', '')
            ''', (employee_name, employee_id, mobile_number, hashed_pw))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Employee ID already exists.', 'danger')
        finally:
            conn.close()
            
    return render_template('register.html')

@app.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    conn = get_db_connection()
    admin_count = conn.execute('SELECT COUNT(*) FROM admins').fetchone()[0]
    
    if admin_count > 0:
        conn.close()
        flash('An admin is already registered. Only one admin is allowed.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        hashed_pw = generate_password_hash(password)
        try:
            conn.execute('INSERT INTO admins (username, password) VALUES (?, ?)',
                         (username, hashed_pw))
            conn.commit()
            flash('Admin registered successfully! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.', 'danger')
        finally:
            conn.close()
            
    conn.close()
    return render_template('admin_register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id_input = request.form['employee_id']
        password = request.form['password']
        role = request.form['role']
        
        conn = get_db_connection()
        if role == 'admin':
            admin = conn.execute('SELECT * FROM admins WHERE username = ?', (user_id_input,)).fetchone()
            if admin and check_password_hash(admin['password'], password):
                session['user_id'] = admin['id']
                session['role'] = 'admin'
                session['name'] = admin['username']
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid admin credentials', 'danger')
        else:
            employee = conn.execute('SELECT * FROM employees WHERE employee_id = ? AND status="Active"', (user_id_input,)).fetchone()
            if employee and check_password_hash(employee['password'], password):
                session['user_id'] = employee['id']
                session['role'] = 'employee'
                session['name'] = employee['employee_name']
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid Employee ID, password, or account is inactive.', 'danger')
        conn.close()

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# --- API Routes ---
@app.route('/api/doctors/<int:department_id>')
def api_get_doctors(department_id):
    conn = get_db_connection()
    doctors = conn.execute('SELECT id, name, specialization FROM doctors WHERE department_id = ? AND status="Active"', (department_id,)).fetchall()
    conn.close()
    docs_list = [{'id': doc['id'], 'name': doc['name'], 'specialization': doc['specialization']} for doc in doctors]
    return jsonify(docs_list)


# --- Employee Routes ---

def check_employee():
    if not session.get('user_id') or session.get('role') != 'employee':
        return False
    return True

@app.route('/dashboard')
def dashboard():
    if not check_employee(): return redirect(url_for('login'))
        
    conn = get_db_connection()
    employee = conn.execute('SELECT * FROM employees WHERE id = ?', (session['user_id'],)).fetchone()
    dependents = conn.execute('SELECT * FROM dependents WHERE employee_id = ?', (session['user_id'],)).fetchall()
    
    appointments = conn.execute('''
        SELECT a.appointment_number, a.patient_name, a.relationship, a.appointment_date, a.appointment_time, a.status, d.name as doctor_name, dep.name as dept_name
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.id
        JOIN departments dep ON a.department_id = dep.id
        WHERE a.employee_id = ?
        ORDER BY a.appointment_date DESC
    ''', (session['user_id'],)).fetchall()
    
    conn.close()

    # Calculate Profile Completion
    fields_to_check = ['employee_name', 'department', 'designation', 'mobile', 'email', 'dob', 'gender', 'blood_group', 'address', 'profile_photo']
    filled_fields = sum(1 for field in fields_to_check if employee[field] and str(employee[field]).strip() != '')
    completion_percentage = int((filled_fields / len(fields_to_check)) * 100)

    return render_template('employee_dashboard.html', employee=employee, dependents=dependents, appointments=appointments, completion_percentage=completion_percentage)

@app.route('/profile', methods=['GET', 'POST'])
def employee_profile():
    if not check_employee(): return redirect(url_for('login'))
    
    conn = get_db_connection()
    employee = conn.execute('SELECT * FROM employees WHERE id = ?', (session['user_id'],)).fetchone()
    
    if request.method == 'POST':
        name = request.form['employee_name']
        department = request.form['department']
        designation = request.form['designation']
        mobile = request.form['mobile']
        email = request.form['email']
        dob = request.form['dob']
        gender = request.form['gender']
        blood_group = request.form['blood_group']
        address = request.form['address']
        
        # Validation
        if not mobile.isdigit() or len(mobile) < 10:
            flash('Invalid mobile number.', 'danger')
            return redirect(url_for('employee_profile'))
            
        if '@' not in email or '.' not in email:
            flash('Invalid email address.', 'danger')
            return redirect(url_for('employee_profile'))

        # Handle Profile Photo Upload
        photo_filename = employee['profile_photo']
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                unique_filename = f"{session['user_id']}_{uuid.uuid4().hex}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                photo_filename = f"uploads/profiles/{unique_filename}"
        
        conn.execute('''
            UPDATE employees 
            SET employee_name=?, department=?, designation=?, mobile=?, email=?, dob=?, gender=?, blood_group=?, address=?, profile_photo=?
            WHERE id=?
        ''', (name, department, designation, mobile, email, dob, gender, blood_group, address, photo_filename, session['user_id']))
        conn.commit()
        conn.close()
        
        session['name'] = name # Update session name just in case
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    conn.close()
    return render_template('employee_profile.html', employee=employee)

@app.route('/dependents', methods=['GET', 'POST'])
def employee_dependents():
    if not check_employee(): return redirect(url_for('login'))
    
    conn = get_db_connection()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            name = request.form['dependent_name']
            relationship = request.form['relationship']
            dob = request.form['dob']
            gender = request.form['gender']
            blood_group = request.form['blood_group']
            mobile = request.form['mobile']
            aadhaar = request.form['aadhaar_number']
            
            conn.execute('''
                INSERT INTO dependents (employee_id, dependent_name, relationship, dob, gender, blood_group, mobile, aadhaar_number)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session['user_id'], name, relationship, dob, gender, blood_group, mobile, aadhaar))
            conn.commit()
            flash('Dependent added successfully.', 'success')
            
        elif action == 'edit':
            dep_id = request.form['dependent_id']
            name = request.form['dependent_name']
            relationship = request.form['relationship']
            dob = request.form['dob']
            gender = request.form['gender']
            blood_group = request.form['blood_group']
            mobile = request.form['mobile']
            aadhaar = request.form['aadhaar_number']
            status = request.form['status']
            
            conn.execute('''
                UPDATE dependents 
                SET dependent_name=?, relationship=?, dob=?, gender=?, blood_group=?, mobile=?, aadhaar_number=?, status=?
                WHERE dependent_id=? AND employee_id=?
            ''', (name, relationship, dob, gender, blood_group, mobile, aadhaar, status, dep_id, session['user_id']))
            conn.commit()
            flash('Dependent updated successfully.', 'success')
            
        elif action == 'delete':
            dep_id = request.form['dependent_id']
            conn.execute('DELETE FROM dependents WHERE dependent_id=? AND employee_id=?', (dep_id, session['user_id']))
            conn.commit()
            flash('Dependent deleted successfully.', 'success')
            
        return redirect(url_for('employee_dependents'))

    dependents = conn.execute('SELECT * FROM dependents WHERE employee_id = ?', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('employee_dependents.html', dependents=dependents)

@app.route('/book', methods=['GET', 'POST'])
def book():
    if not check_employee(): return redirect(url_for('login'))
        
    conn = get_db_connection()
    if request.method == 'POST':
        patient_selection = request.form['patient_selection']
        department_id = request.form['department_id']
        doctor_id = request.form['doctor_id']
        date = request.form['appointment_date']
        time_slot = request.form['appointment_time']
        appointment_number = 'APT' + datetime.now().strftime('%Y%m%d%H%M%S')
        
        if patient_selection == 'self':
            emp = conn.execute('SELECT employee_name FROM employees WHERE id = ?', (session['user_id'],)).fetchone()
            patient_name = emp['employee_name']
            relationship = '01 - Employee (Self)'
            dependent_id = None
        else:
            dep = conn.execute('SELECT dependent_name, relationship FROM dependents WHERE dependent_id = ? AND employee_id = ?', (patient_selection, session['user_id'])).fetchone()
            patient_name = dep['dependent_name']
            relationship = dep['relationship']
            dependent_id = patient_selection
            
        conn.execute('''
            INSERT INTO appointments (appointment_number, employee_id, dependent_id, patient_name, relationship, doctor_id, department_id, appointment_date, appointment_time, status) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (appointment_number, session['user_id'], dependent_id, patient_name, relationship, doctor_id, department_id, date, time_slot, 'Pending'))
        conn.commit()
        flash('Appointment booked successfully!', 'success')
        conn.close()
        return redirect(url_for('dashboard'))
        
    departments = conn.execute('SELECT * FROM departments WHERE status="Active"').fetchall()
    dependents = conn.execute('SELECT * FROM dependents WHERE employee_id = ? AND status="Active"', (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template('employee_book.html', departments=departments, dependents=dependents)


# --- Admin Routes ---

def check_admin():
    if not session.get('user_id') or session.get('role') != 'admin':
        return False
    return True

@app.route('/admin')
@app.route('/admin/dashboard')
def admin_dashboard():
    if not check_admin(): return redirect(url_for('login'))
    
    conn = get_db_connection()
    stats = {}
    stats['total_employees'] = conn.execute('SELECT COUNT(*) FROM employees').fetchone()[0]
    stats['total_dependents'] = conn.execute('SELECT COUNT(*) FROM dependents').fetchone()[0]
    stats['total_doctors'] = conn.execute('SELECT COUNT(*) FROM doctors').fetchone()[0]
    stats['total_departments'] = conn.execute('SELECT COUNT(*) FROM departments').fetchone()[0]
    
    today = datetime.now().strftime('%Y-%m-%d')
    stats['today_appointments'] = conn.execute('SELECT COUNT(*) FROM appointments WHERE appointment_date = ?', (today,)).fetchone()[0]
    stats['pending_appointments'] = conn.execute('SELECT COUNT(*) FROM appointments WHERE status = "Pending"').fetchone()[0]
    stats['completed_appointments'] = conn.execute('SELECT COUNT(*) FROM appointments WHERE status = "Completed"').fetchone()[0]
    
    recent_appointments = conn.execute('''
        SELECT a.appointment_number, a.patient_name, a.relationship, d.name as doctor_name, a.appointment_date, a.appointment_time, a.status
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.id
        ORDER BY a.appointment_id DESC LIMIT 5
    ''').fetchall()
    
    conn.close()
    return render_template('admin_dashboard.html', stats=stats, recent_appointments=recent_appointments)

# Admin Departments
@app.route('/admin/departments', methods=['GET', 'POST'])
def admin_departments():
    if not check_admin(): return redirect(url_for('login'))
    conn = get_db_connection()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            code = request.form['department_code']
            name = request.form['name']
            desc = request.form['description']
            status = request.form['status']
            created_date = datetime.now().strftime('%Y-%m-%d')
            try:
                conn.execute('INSERT INTO departments (department_code, name, description, status, created_date) VALUES (?, ?, ?, ?, ?)',
                             (code, name, desc, status, created_date))
                conn.commit()
                flash('Department added successfully!', 'success')
            except sqlite3.IntegrityError:
                flash('Department Code already exists.', 'danger')
        elif action == 'edit':
            id = request.form['id']
            name = request.form['name']
            desc = request.form['description']
            status = request.form['status']
            conn.execute('UPDATE departments SET name=?, description=?, status=? WHERE id=?', (name, desc, status, id))
            conn.commit()
            flash('Department updated successfully!', 'success')
        elif action == 'delete':
            id = request.form['id']
            conn.execute('DELETE FROM departments WHERE id=?', (id,))
            conn.commit()
            flash('Department deleted successfully!', 'success')
        return redirect(url_for('admin_departments'))

    departments = conn.execute('SELECT * FROM departments ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('admin_departments.html', departments=departments)

# Admin Doctors
@app.route('/admin/doctors', methods=['GET', 'POST'])
def admin_doctors():
    if not check_admin(): return redirect(url_for('login'))
    conn = get_db_connection()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            name = request.form['name']
            dept_id = request.form['department_id']
            spec = request.form['specialization']
            qual = request.form['qualification']
            exp = request.form['experience']
            phone = request.form['phone_number']
            email = request.form['email']
            days = request.form['available_days']
            slots = request.form['available_time_slots']
            status = request.form['status']
            conn.execute('''
                INSERT INTO doctors (name, department_id, specialization, qualification, experience, phone_number, email, available_days, available_time_slots, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, dept_id, spec, qual, exp, phone, email, days, slots, status))
            conn.commit()
            flash('Doctor added successfully!', 'success')
        elif action == 'edit':
            id = request.form['id']
            name = request.form['name']
            dept_id = request.form['department_id']
            spec = request.form['specialization']
            qual = request.form['qualification']
            exp = request.form['experience']
            phone = request.form['phone_number']
            email = request.form['email']
            days = request.form['available_days']
            slots = request.form['available_time_slots']
            status = request.form['status']
            conn.execute('''
                UPDATE doctors SET name=?, department_id=?, specialization=?, qualification=?, experience=?, phone_number=?, email=?, available_days=?, available_time_slots=?, status=?
                WHERE id=?
            ''', (name, dept_id, spec, qual, exp, phone, email, days, slots, status, id))
            conn.commit()
            flash('Doctor updated successfully!', 'success')
        elif action == 'delete':
            id = request.form['id']
            conn.execute('DELETE FROM doctors WHERE id=?', (id,))
            conn.commit()
            flash('Doctor deleted successfully!', 'success')
        return redirect(url_for('admin_doctors'))

    doctors = conn.execute('''
        SELECT d.*, dep.name as dept_name 
        FROM doctors d 
        LEFT JOIN departments dep ON d.department_id = dep.id
        ORDER BY d.id DESC
    ''').fetchall()
    departments = conn.execute('SELECT * FROM departments WHERE status="Active"').fetchall()
    conn.close()
    return render_template('admin_doctors.html', doctors=doctors, departments=departments)

# Admin Employees
@app.route('/admin/employees', methods=['GET', 'POST'])
def admin_employees():
    if not check_admin(): return redirect(url_for('login'))
    conn = get_db_connection()
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            emp_id = request.form['employee_id']
            name = request.form['employee_name']
            dept = request.form['department']
            desig = request.form['designation']
            mobile = request.form['mobile']
            email = request.form['email']
            dob = request.form['dob']
            gender = request.form['gender']
            bg = request.form['blood_group']
            addr = request.form['address']
            status = request.form['status']
            pw = generate_password_hash('password123') # Default password
            
            try:
                conn.execute('''
                    INSERT INTO employees (employee_id, employee_name, department, designation, mobile, email, dob, gender, blood_group, address, status, password, profile_photo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '')
                ''', (emp_id, name, dept, desig, mobile, email, dob, gender, bg, addr, status, pw))
                conn.commit()
                flash('Employee added successfully!', 'success')
            except sqlite3.IntegrityError:
                flash('Employee ID already exists.', 'danger')
                
        elif action == 'edit':
            id = request.form['id']
            name = request.form['employee_name']
            dept = request.form['department']
            desig = request.form['designation']
            mobile = request.form['mobile']
            email = request.form['email']
            dob = request.form['dob']
            gender = request.form['gender']
            bg = request.form['blood_group']
            addr = request.form['address']
            status = request.form['status']
            
            conn.execute('''
                UPDATE employees SET employee_name=?, department=?, designation=?, mobile=?, email=?, dob=?, gender=?, blood_group=?, address=?, status=?
                WHERE id=?
            ''', (name, dept, desig, mobile, email, dob, gender, bg, addr, status, id))
            conn.commit()
            flash('Employee updated successfully!', 'success')
            
        elif action == 'delete':
            id = request.form['id']
            conn.execute('DELETE FROM dependents WHERE employee_id=?', (id,))
            conn.execute('DELETE FROM employees WHERE id=?', (id,))
            conn.commit()
            flash('Employee and their dependents deleted successfully!', 'success')
            
        return redirect(url_for('admin_employees'))

    employees = conn.execute('SELECT * FROM employees ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('admin_employees.html', employees=employees)

# Admin Patients / Dependents
@app.route('/admin/patients', methods=['GET', 'POST'])
def admin_patients():
    if not check_admin(): return redirect(url_for('login'))
    conn = get_db_connection()
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'edit':
            dep_id = request.form['dependent_id']
            name = request.form['dependent_name']
            mobile = request.form['mobile']
            dob = request.form['dob']
            status = request.form['status']
            
            conn.execute('''
                UPDATE dependents SET dependent_name=?, mobile=?, dob=?, status=?
                WHERE dependent_id=?
            ''', (name, mobile, dob, status, dep_id))
            conn.commit()
            flash('Dependent updated successfully!', 'success')
            
        elif action == 'delete':
            dep_id = request.form['dependent_id']
            conn.execute('DELETE FROM dependents WHERE dependent_id=?', (dep_id,))
            conn.commit()
            flash('Dependent deleted successfully!', 'success')
            
        return redirect(url_for('admin_patients'))

    dependents = conn.execute('''
        SELECT d.*, e.employee_id as emp_code, e.employee_name as emp_name
        FROM dependents d
        JOIN employees e ON d.employee_id = e.id
        ORDER BY d.dependent_id DESC
    ''').fetchall()
    
    conn.close()
    return render_template('admin_patients.html', dependents=dependents)

# Admin Appointments
@app.route('/admin/appointments', methods=['GET', 'POST'])
def admin_appointments():
    if not check_admin(): return redirect(url_for('login'))
    conn = get_db_connection()
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_status':
            id = request.form['id']
            status = request.form['status']
            conn.execute('UPDATE appointments SET status=? WHERE appointment_id=?', (status, id))
            conn.commit()
            flash(f'Appointment marked as {status}.', 'success')
        return redirect(url_for('admin_appointments'))

    doctor_id = request.args.get('doctor_id')
    department_id = request.args.get('department_id')
    
    query = '''
        SELECT a.*, e.employee_id as emp_code, d.name as doctor_name, dep.name as dept_name
        FROM appointments a
        JOIN employees e ON a.employee_id = e.id
        JOIN doctors d ON a.doctor_id = d.id
        JOIN departments dep ON a.department_id = dep.id
        WHERE 1=1
    '''
    params = []
    
    if doctor_id:
        query += " AND a.doctor_id = ?"
        params.append(doctor_id)
    if department_id:
        query += " AND a.department_id = ?"
        params.append(department_id)
        
    query += " ORDER BY a.appointment_date DESC, a.appointment_time DESC"
    
    appointments = conn.execute(query, params).fetchall()
    doctors = conn.execute('SELECT id, name FROM doctors').fetchall()
    departments = conn.execute('SELECT id, name FROM departments').fetchall()
    
    conn.close()
    return render_template('admin_appointments.html', appointments=appointments, doctors=doctors, departments=departments)

# Admin Reports
@app.route('/admin/reports')
def admin_reports():
    if not check_admin(): return redirect(url_for('login'))
    conn = get_db_connection()
    
    dept_stats = conn.execute('''
        SELECT dep.name, COUNT(a.appointment_id) as count
        FROM departments dep
        LEFT JOIN appointments a ON dep.id = a.department_id
        GROUP BY dep.id
    ''').fetchall()
    
    doc_stats = conn.execute('''
        SELECT d.name, COUNT(a.appointment_id) as count
        FROM doctors d
        LEFT JOIN appointments a ON d.id = a.doctor_id
        GROUP BY d.id
    ''').fetchall()
    
    status_stats = conn.execute('''
        SELECT status, COUNT(appointment_id) as count FROM appointments GROUP BY status
    ''').fetchall()

    conn.close()
    
    chart_data = {
        'dept_labels': [row['name'] for row in dept_stats],
        'dept_data': [row['count'] for row in dept_stats],
        'doc_labels': [row['name'] for row in doc_stats],
        'doc_data': [row['count'] for row in doc_stats],
        'status_labels': [row['status'] for row in status_stats],
        'status_data': [row['count'] for row in status_stats],
    }
    
    return render_template('admin_reports.html', chart_data=chart_data)

if __name__ == '__main__':
    app.run(debug=True)
