# 📚 MyAcademy Attendance Management Script  

**Short Description:**  
A Python-based attendance management system for MyAcademy that automates student registration, daily attendance, and WhatsApp absence notifications. It includes backup/restore features, Excel export, and detailed stats, making attendance tracking simple, reliable, and professional for small educational institutes.  

---

## 📌 Features  
- **Student Management**  
  - Register students with name, grade, phone, joining date, and auto-generated ID.
  - View attendance stats of any specific student.
  - View complete list of stats in clean tabular form.

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
1. Student Management
2. Take attendance
3. Backup
4. View and Edit Attendance Records
5. Copy to Excel file
6. Exit
```

---

## 🚀 Future Improvements

* Web dashboard version.
* SMS/email integration.
* Attendance trend analysis & visualization.

