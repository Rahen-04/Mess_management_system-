# Mess_management_system-
{**mandatory:
to run : - // create the users table in itworkshop database in pgadmin  before runing the login.js file //
}




Introduction:
 					This project is a web-based College Mess Management System developed with the aim of reducing food wastage and improving efficiency. The system enables only authorized personnel such as the admin and mess secretary to register users. Each user is uniquely identified by their roll number and is associated with a QR code which is scanned during meals
 
1.	Technologies Used-
Backend: Node.js with PostgreSQL (pgadmin for management)

 Frontend: HTML, CSS, JavaScript- Password Security: bcrypt for hashing- QR Code: Generated per user and scanned via the admin panel


2.	User Roles and Features-
	 Admin: Username 'admin' and password 'admin123'. Can register/delete users, view user data, and access the QR code scanner.- Mess Secretary: Can only register the clients (users).- Users: Can log in, view QR code, submit feedback, complaints, polls, and apply for leave. Registration is only allowed through the admin or mess secretary. On login (validated using roll number and hashed password), users access their dashboard

3.	Database Schema:
 Only the 'users' table must be manually created in pgAdmin. All other tables are created dynamically in the backend using db.connect(). 
SQL Code: Create 'users' Table
CREATE TABLE users (
    id VARCHAR(50) PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_scan_time TIMESTAMP WITH TIME ZONE );
4.	Features Overview- QR Code Allotment:

 Each user gets a unique QR code after registration, visible on their dashboard.-

 Login: Users authenticate using roll number and password (hashed using bcrypt).
Forms: Feedback form, complaint form, meal poll form.
Polls: Users indicate if they will attend the next day's meal. Admin sees total count to prepare 

accordingly Leave Application: Users can apply for leave; admin can delete such users from active meals.

QR Code Scanning: Admin scans user's QR before meal. Double scanning is prevented to stop multiple entries
5.	Food Wastage Prevention Logic:

 By collecting poll responses and validating each user's QR code only once per meal, the system ensures only the intended number of meals are prepared and served. This prevents unauthorized access and controls wastage effectively. 


6.	Menu Display:

 A dedicated menu button on the home page displays a full month's mess timetable to all users. 

7.	Conclusion:

 The web application significantly improves mess management by automating user tracking, controlling food distribution via QR codes, and promoting accountability. It serves as a practical tool to reduce food wastage while ensuring fairness and transparency.
