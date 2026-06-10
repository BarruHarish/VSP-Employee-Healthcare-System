import sqlite3
import os
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_db():
    db_path = 'hospital.db'
    
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

    # Create Employee Departments table (Steel Plant Departments)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employee_departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'Active'
        )
    ''')

    # Create Employees table
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
            status TEXT DEFAULT 'Active',
            profile_photo TEXT,
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

    # Create Hospital Departments table
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

    # Insert Employee Departments (Steel Plant Departments)
    employee_departments_data = [
        ('Information Technology (IT)',),
        ('Steel Melting Shop (SMS)',),
        ('Blast Furnace',),
        ('Coke Ovens',),
        ('Power Plant',),
        ('Mechanical Maintenance',),
        ('Electrical Maintenance',),
        ('Production',),
        ('Human Resources (HR)',),
        ('Finance & Accounts',),
        ('Safety Department',),
        ('Materials Management',),
        ('Projects Department',),
        ('Quality Assurance',)
    ]
    cursor.executemany('INSERT INTO employee_departments (name) VALUES (?)', employee_departments_data)

    # Insert Realistic Hospital Departments
    default_departments = [
        ('D001', 'General Medicine', 'Primary care and general health issues'),
        ('D002', 'Orthopedics', 'Bone and joint care'),
        ('D003', 'Cardiology', 'Heart and cardiovascular care'),
        ('D004', 'ENT', 'Ear, Nose, and Throat care'),
        ('D005', 'Ophthalmology', 'Eye care'),
        ('D006', 'Dermatology', 'Skin care'),
        ('D007', 'Dentistry', 'Dental care'),
        ('D008', 'Pediatrics', 'Child care'),
        ('D009', 'Gynecology', 'Women''s health'),
        ('D010', 'Physiotherapy', 'Physical rehabilitation')
    ]
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    for code, name, desc in default_departments:
        cursor.execute('INSERT INTO departments (department_code, name, description, created_date) VALUES (?, ?, ?, ?)',
                       (code, name, desc, current_date))

    # Insert Realistic Doctors mapped to the new departments
    # 1: General Medicine, 2: Orthopedics, 3: Cardiology, 4: ENT, 5: Ophthalmology
    # 6: Dermatology, 7: Dentistry, 8: Pediatrics, 9: Gynecology, 10: Physiotherapy
    sample_doctors = [
        # General Medicine (1)
        ('Dr. Srinivas Rao', 1, 'Internal Medicine', 'MD', '15 Years', '9876543210', 'srinivas@hospital.com', 'Mon-Fri', '09:00 AM - 01:00 PM'),
        ('Dr. Madhuri Devi', 1, 'General Physician', 'MD', '10 Years', '9876543211', 'madhuri@hospital.com', 'Mon-Sat', '10:00 AM - 02:00 PM'),
        ('Dr. Ramesh Kumar', 1, 'Internal Medicine', 'MD', '12 Years', '9876543212', 'ramesh@hospital.com', 'Tue-Sun', '11:00 AM - 04:00 PM'),
        
        # Orthopedics (2)
        ('Dr. Prakash Kumar', 2, 'Orthopedic Surgeon', 'MS Ortho', '10 Years', '9876543213', 'prakash@hospital.com', 'Mon, Wed, Fri', '10:00 AM - 02:00 PM'),
        ('Dr. Sandeep Reddy', 2, 'Orthopedics', 'MS Ortho', '8 Years', '9876543214', 'sandeep@hospital.com', 'Tue, Thu, Sat', '09:00 AM - 01:00 PM'),
        ('Dr. Venkatesh Rao', 2, 'Joint Replacement', 'MS Ortho', '14 Years', '9876543215', 'venkatesh@hospital.com', 'Mon-Fri', '02:00 PM - 06:00 PM'),
        
        # Cardiology (3)
        ('Dr. Anil Kumar', 3, 'Cardiologist', 'DM Cardiology', '12 Years', '9876543216', 'anil@hospital.com', 'Tue, Thu, Sat', '11:00 AM - 03:00 PM'),
        ('Dr. Rajesh Naidu', 3, 'Interventional Cardiology', 'DM', '15 Years', '9876543217', 'rajesh@hospital.com', 'Mon-Fri', '09:00 AM - 01:00 PM'),
        ('Dr. Kiran Kumar', 3, 'Cardiology', 'DM', '9 Years', '9876543218', 'kiran@hospital.com', 'Mon, Wed, Fri', '02:00 PM - 06:00 PM'),
        
        # ENT (4)
        ('Dr. Ravi Teja', 4, 'ENT Specialist', 'MS ENT', '9 Years', '9876543219', 'ravi@hospital.com', 'Mon, Wed, Fri', '09:00 AM - 01:00 PM'),
        ('Dr. Sai Krishna', 4, 'Otolaryngology', 'MS ENT', '6 Years', '9876543220', 'sai@hospital.com', 'Tue, Thu, Sat', '10:00 AM - 02:00 PM'),
        ('Dr. Pradeep Kumar', 4, 'ENT Surgeon', 'MS ENT', '11 Years', '9876543221', 'pradeep@hospital.com', 'Mon-Sat', '04:00 PM - 08:00 PM'),
        
        # Ophthalmology (5)
        ('Dr. Suresh Babu', 5, 'Ophthalmologist', 'MS Ophthalmology', '14 Years', '9876543222', 'suresh@hospital.com', 'Tue, Thu, Sat', '10:00 AM - 02:00 PM'),
        ('Dr. Niharika Devi', 5, 'Eye Surgeon', 'MS', '8 Years', '9876543223', 'niharika@hospital.com', 'Mon, Wed, Fri', '09:00 AM - 01:00 PM'),
        ('Dr. Naveen Kumar', 5, 'Ophthalmology', 'MS', '10 Years', '9876543224', 'naveen@hospital.com', 'Mon-Fri', '02:00 PM - 06:00 PM'),
        
        # Dermatology (6)
        ('Dr. Lakshmi Devi', 6, 'Dermatologist', 'MD Dermatology', '8 Years', '9876543225', 'lakshmi@hospital.com', 'Mon-Sat', '04:00 PM - 08:00 PM'),
        ('Dr. Swathi Reddy', 6, 'Skin Specialist', 'MD', '5 Years', '9876543226', 'swathi@hospital.com', 'Mon, Wed, Fri', '09:00 AM - 01:00 PM'),
        ('Dr. Haritha Rao', 6, 'Cosmetologist', 'MD', '12 Years', '9876543227', 'haritha@hospital.com', 'Tue, Thu, Sat', '10:00 AM - 02:00 PM'),
        
        # Dentistry (7)
        ('Dr. Mahesh Kumar', 7, 'Dentist', 'BDS', '5 Years', '9876543228', 'mahesh@hospital.com', 'Mon-Sat', '10:00 AM - 06:00 PM'),
        ('Dr. Vinay Kumar', 7, 'Dental Surgeon', 'MDS', '9 Years', '9876543229', 'vinay@hospital.com', 'Mon-Fri', '09:00 AM - 01:00 PM'),
        ('Dr. Rohith Reddy', 7, 'Orthodontics', 'MDS', '7 Years', '9876543230', 'rohith@hospital.com', 'Tue, Thu, Sat', '02:00 PM - 06:00 PM'),
        
        # Pediatrics (8)
        ('Dr. Priya Reddy', 8, 'Pediatrician', 'MD Pediatrics', '7 Years', '9876543231', 'priya@hospital.com', 'Mon-Fri', '09:00 AM - 04:00 PM'),
        ('Dr. Keerthi Devi', 8, 'Child Specialist', 'MD', '10 Years', '9876543232', 'keerthi@hospital.com', 'Mon, Wed, Fri', '10:00 AM - 02:00 PM'),
        ('Dr. Anusha Rao', 8, 'Neonatology', 'MD', '12 Years', '9876543233', 'anusha@hospital.com', 'Tue, Thu, Sat', '04:00 PM - 08:00 PM'),
        
        # Gynecology (9)
        ('Dr. Kavitha Devi', 9, 'Gynecologist', 'MD', '15 Years', '9876543234', 'kavitha@hospital.com', 'Mon-Sat', '09:00 AM - 01:00 PM'),
        ('Dr. Sunitha Reddy', 9, 'Obstetrics', 'MD', '11 Years', '9876543235', 'sunitha@hospital.com', 'Mon, Wed, Fri', '02:00 PM - 06:00 PM'),
        ('Dr. Deepika Rao', 9, 'Gynecology', 'MS', '8 Years', '9876543236', 'deepika@hospital.com', 'Tue, Thu, Sat', '10:00 AM - 02:00 PM'),
        
        # Physiotherapy (10)
        ('Dr. Ajay Kumar', 10, 'Physiotherapist', 'BPT', '6 Years', '9876543237', 'ajay@hospital.com', 'Mon-Sat', '09:00 AM - 05:00 PM'),
        ('Dr. Siva Krishna', 10, 'Sports Medicine', 'MPT', '9 Years', '9876543238', 'siva@hospital.com', 'Mon-Fri', '10:00 AM - 06:00 PM'),
        ('Dr. Harish Kumar', 10, 'Rehabilitation', 'MPT', '7 Years', '9876543239', 'harish@hospital.com', 'Tue-Sun', '08:00 AM - 04:00 PM')
    ]

    for doc in sample_doctors:
        cursor.execute('''
            INSERT INTO doctors (name, department_id, specialization, qualification, experience, phone_number, email, available_days, available_time_slots)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', doc)

    # Insert a sample employee
    hashed_emp_pw = generate_password_hash('password123')
    cursor.execute('''
        INSERT INTO employees (employee_id, employee_name, department, designation, mobile, email, dob, gender, blood_group, address, password, profile_photo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '')
    ''', ('EMP1001', 'Ramesh Kumar', 'Information Technology (IT)', 'System Admin', '9876543200', 'ramesh@vsp.com', '1985-06-15', 'Male', 'O+', 'Sector 5, MVP Colony, Visakhapatnam', hashed_emp_pw))
    emp_id = cursor.lastrowid

    # Insert sample dependents
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
    print("Database initialized successfully with separated Employee & Hospital Departments.")

if __name__ == '__main__':
    init_db()
