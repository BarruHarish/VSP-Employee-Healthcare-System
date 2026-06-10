# VSP Employee Healthcare System

A comprehensive Hospital Appointment Management System designed for employees and their dependents. This system allows employees to manage healthcare appointments, maintain dependent profiles, and access medical services through a centralized web portal.

## Project Overview

The VSP Employee Healthcare System is a full-stack web application that digitizes the hospital appointment process for employees and their family members.

Employees can:

* Register and login securely
* Manage their profile
* Add and manage dependents
* Book doctor appointments
* View appointment history
* Track upcoming appointments

Administrators can:

* Manage departments
* Manage doctors
* Manage employees
* Manage appointments
* Generate reports and analytics

---

## Features

### Employee Module

* Employee Registration
* Secure Login & Logout
* Employee Dashboard
* Profile Management
* Dependent Management
* Appointment Booking
* Appointment History
* Upcoming Appointments

### Dependency Management

Supported Relationships:

* Employee (Self)
* Spouse
* Father
* Mother
* Son
* Daughter

### Appointment Management

* Select Patient
* Select Department
* Select Doctor
* Choose Date & Time Slot
* Confirm Appointment
* View Appointment Status

### Admin Module

* Admin Dashboard
* Department Management
* Doctor Management
* Employee Management
* Appointment Management
* Reports & Analytics

---

## Technology Stack

### Frontend

* HTML5
* CSS3
* JavaScript

### Backend

* Python
* Flask

### Database

* SQLite

---

## Project Structure

```text
hospital_app/
│
├── app.py
├── database.py
├── requirements.txt
│
├── static/
│   ├── css/
│   └── js/
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── employee_dashboard.html
│   ├── employee_book.html
│   ├── employee_dependents.html
│   ├── admin_dashboard.html
│   ├── admin_doctors.html
│   ├── admin_departments.html
│   └── admin_reports.html
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/BarruHarish/VSP-Employee-Healthcare-System.git
```

### Navigate to Project

```bash
cd VSP-Employee-Healthcare-System
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
python app.py
```

### Open Browser

```text
http://127.0.0.1:5000
```

---

## Database Tables

* Employees
* Dependents
* Doctors
* Departments
* Appointments
* Admins

---

## Future Enhancements

* Email Notifications
* SMS Alerts
* Online Prescription Management
* Medical Records Management
* Doctor Availability Calendar
* PDF Appointment Receipts
* Role-Based Access Control
* Cloud Deployment

---

## Author

Barru Harish

GitHub:
https://github.com/BarruHarish

---

## License

This project is developed for educational and academic purposes.
