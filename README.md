# 📚 MyAcademy Attendance Management Script  

**Short Description:**  
A Python-based attendance management system for MyAcademy that automates student registration, daily attendance, and WhatsApp absence notifications. It includes backup/restore features, Excel export, and detailed stats, making attendance tracking simple, reliable, and professional for small educational institutes.  

---

## 📌 Features  
- **Student Management**  
  - Register students with name, grade, phone, joining date, and auto-generated ID.  

- **Attendance Management**  
  - Record daily attendance (P/A/L).  
  - Maintain daily attendance files + master stats file.  
  - Edit past attendance records.  
  - View attendance by date or by student.  

- **Notifications**  
  - Automatically send WhatsApp absence messages to parents.  

- **Reports & Stats**  
  - Track presents, absents, leaves, and attendance percentage.  
  - Export full attendance records to Excel.  

- **Backup & Restore**  
  - Create dated backups of student and attendance files.  
  - Restore data when needed.  

---

## 🛠️ Tech Stack  
- **Language:** Python 3  
- **Libraries:**  
  - `pywhatkit` → WhatsApp messaging  
  - `pandas` → Export to Excel  
  - `datetime`, `os`, `shutil` → File handling & backups  

---


## 📊 Example Menu

```
Welcome to My Academy Attendance System

Menu:
1. Add new student(s)
2. View student attendance stats
3. Take attendance and send absence messages
4. Create Backup
5. Restore from Backup
6. View date-wise attendance for a student
7. View attendance of a specific date
8. Edit attendance record for a date
9. Copy attendance to Excel file
10. Exit
```

---

## 🚀 Future Improvements

* Web dashboard version.
* SMS/email integration.
* Attendance trend analysis & visualization.

```
