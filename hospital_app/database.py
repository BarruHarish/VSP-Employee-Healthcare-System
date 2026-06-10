import sqlite3
import os
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_db():
    db_path = 'hospital.db'
    
    # If database exists, we delete it to start fresh with new schema
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create Admins table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Create Employees table (Replaces patients table)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT UNIQUE NOT NULL,
            employee_name TEXT NOT NULL,
            department TEXT,
            designation TEXT,
            mobile TEXT NOT NULL,
            email TEXT,
            dob TEXT,
            gender TEXT,
            blood_group TEXT,
            address TEXT,
            password TEXT NOT NULL
        )
    ''')

    # Create Dependents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dependents (
            dependent_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            dependent_name TEXT NOT NULL,
            relationship TEXT NOT NULL,
            dob TEXT,
            gender TEXT,
            blood_group TEXT,
            mobile TEXT,
            aadhaar_number TEXT,
            status TEXT DEFAULT 'Active',
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
    ''')

    # Create Departments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            department_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Active',
            created_date TEXT NOT NULL
        )
    ''')

    # Create Doctors table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department_id INTEGER,
            specialization TEXT,
            qualification TEXT,
            experience TEXT,
            phone_number TEXT,
            email TEXT,
            available_days TEXT,
            available_time_slots TEXT,
            status TEXT DEFAULT 'Active',
            profile_photo TEXT,
            FOREIGN KEY (department_id) REFERENCES departments (id)
        )
    ''')

    # Create Appointments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_number TEXT UNIQUE NOT NULL,
            employee_id INTEGER,
            dependent_id INTEGER,
            patient_name TEXT,
            relationship TEXT,
            doctor_id INTEGER,
            department_id INTEGER,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (employee_id) REFERENCES employees (id),
            FOREIGN KEY (dependent_id) REFERENCES dependents (dependent_id),
            FOREIGN KEY (doctor_id) REFERENCES doctors (id),
            FOREIGN KEY (department_id) REFERENCES departments (id)
        )
    ''')

    # Insert default admin
    hashed_admin_pw = generate_password_hash('admin123')
    cursor.execute('INSERT INTO admins (username, password) VALUES (?, ?)', ('admin', hashed_admin_pw))

    # Insert default departments
    default_departments = [
        ('D001', 'General Medicine', 'Primary care and general health issues'),
        ('D002', 'General Surgery', 'General surgical procedures'),
        ('D003', 'Orthopedics', 'Bone and joint care'),
        ('D004', 'Cardiology', 'Heart and cardiovascular care'),
        ('D005', 'Neurology', 'Brain and nervous system care'),
        ('D006', 'Dermatology', 'Skin care'),
        ('D007', 'ENT', 'Ear, Nose, and Throat care'),
        ('D008', 'Ophthalmology', 'Eye care'),
        ('D009', 'Pediatrics', 'Child care'),
        ('D010', 'Gynecology', 'Women''s health'),
        ('D011', 'Dentistry', 'Dental care'),
        ('D012', 'Psychiatry', 'Mental health care'),
        ('D013', 'Pulmonology', 'Respiratory system care'),
        ('D014', 'Urology', 'Urinary tract care'),
        ('D015', 'Gastroenterology', 'Digestive system care'),
        ('D016', 'Nephrology', 'Kidney care'),
        ('D017', 'Oncology', 'Cancer care'),
        ('D018', 'Physiotherapy', 'Physical rehabilitation'),
        ('D019', 'Emergency Medicine', 'Emergency care'),
        ('D020', 'Radiology', 'Imaging and diagnostics'),
        ('D021', 'Pathology', 'Laboratory tests')
    ]
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    for code, name, desc in default_departments:
        cursor.execute('INSERT INTO departments (department_code, name, description, created_date) VALUES (?, ?, ?, ?)',
                       (code, name, desc, current_date))

    # Insert sample doctors
    sample_doctors = [
        ('Dr. Srinivas Rao', 1, 'Internal Medicine', 'MD', '15 Years', '9876543210', 'srinivas@hospital.com', 'Mon-Fri', '09:00 AM - 01:00 PM'),
        ('Dr. Prakash Kumar', 3, 'Orthopedic Surgeon', 'MS Ortho', '10 Years', '9876543211', 'prakash@hospital.com', 'Mon, Wed, Fri', '10:00 AM - 02:00 PM'),
        ('Dr. Anil Kumar', 4, 'Cardiologist', 'DM Cardiology', '12 Years', '9876543212', 'anil@hospital.com', 'Tue, Thu, Sat', '11:00 AM - 03:00 PM'),
        ('Dr. Lakshmi Devi', 6, 'Dermatologist', 'MD Dermatology', '8 Years', '9876543213', 'lakshmi@hospital.com', 'Mon-Sat', '04:00 PM - 08:00 PM'),
        ('Dr. Ravi Teja', 7, 'ENT Specialist', 'MS ENT', '9 Years', '9876543214', 'ravi@hospital.com', 'Mon, Wed, Fri', '09:00 AM - 01:00 PM'),
        ('Dr. Suresh Babu', 8, 'Ophthalmologist', 'MS Ophthalmology', '14 Years', '9876543215', 'suresh@hospital.com', 'Tue, Thu, Sat', '10:00 AM - 02:00 PM'),
        ('Dr. Priya Reddy', 9, 'Pediatrician', 'MD Pediatrics', '7 Years', '9876543216', 'priya@hospital.com', 'Mon-Fri', '09:00 AM - 04:00 PM'),
        ('Dr. Mahesh Kumar', 11, 'Dentist', 'BDS', '5 Years', '9876543217', 'mahesh@hospital.com', 'Mon-Sat', '10:00 AM - 06:00 PM')
    ]

    for doc in sample_doctors:
        cursor.execute('''
            INSERT INTO doctors (name, department_id, specialization, qualification, experience, phone_number, email, available_days, available_time_slots)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', doc)

    # Insert a sample employee
    hashed_emp_pw = generate_password_hash('password123')
    cursor.execute('''
        INSERT INTO employees (employee_id, employee_name, department, designation, mobile, email, dob, gender, blood_group, address, password)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('EMP1001', 'Ramesh Kumar', 'IT Support', 'System Admin', '9876543200', 'ramesh@vsp.com', '1985-06-15', 'Male', 'O+', 'Sector 5, MVP Colony, Visakhapatnam', hashed_emp_pw))
    emp_id = cursor.lastrowid

    # Insert sample dependents for the employee
    cursor.execute('''
        INSERT INTO dependents (employee_id, dependent_name, relationship, dob, gender, blood_group, mobile, aadhaar_number)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (emp_id, 'Sunitha Kumar', '02 - Spouse', '1988-08-20', 'Female', 'A+', '9876543201', '123456789012'))
    
    cursor.execute('''
        INSERT INTO dependents (employee_id, dependent_name, relationship, dob, gender, blood_group, mobile, aadhaar_number)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (emp_id, 'Rahul Kumar', '05 - Son', '2010-05-10', 'Male', 'O+', '', ''))

    conn.commit()
    conn.close()
    print("Database initialized successfully with Employee & Dependent modules.")

if __name__ == '__main__':
    init_db()
