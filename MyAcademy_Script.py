import pywhatkit as pwk
import datetime
import os
import shutil
import pandas as pd

STUDENT_FILE = "students.txt"
STATS_FILE = "master_attendance.txt"
DAILY_DIR = "daily_attendance"
BACKUP_DIR = "backups"

# --- Load existing students from file ---
def load_students():
    students = []
    if not os.path.exists(STUDENT_FILE):
        return students
    with open(STUDENT_FILE, "r") as file:
        for line in file:
            parts = line.strip().split(",")
            if len(parts) == 5:
                name, phone, grade, reg_num, joining_date = parts
                students.append((name, phone, grade, reg_num, joining_date))
    return students

# --- Add new students to the file ---
def add_student():
    while True:
        grade = input("Enter student grade: ").strip()
        name = input("Enter student name: ").title()
        phone = input("Enter parent's phone number: ")

        students = load_students()
        reg_number = len(students) + 1
        year = str(datetime.date.today().year)[-2:]
        grade_str = f"{int(grade):02}"
        registration_number = f"MA{year}{grade_str}{reg_number:02}"

        use_custom = input("Do you want to enter a custom joining date? (Y/N): ").strip().upper()
        if use_custom == "Y":
            while True:
                custom_date = input("Enter joining date (YYYY-MM-DD): ").strip()
                try:
                    datetime.datetime.strptime(custom_date, "%Y-%m-%d")
                    joining_date = custom_date
                    break
                except ValueError:
                    print("Invalid format. Please use YYYY-MM-DD.")
        else:
            joining_date = datetime.date.today().isoformat()

        with open(STUDENT_FILE, "a") as file:
            file.write(f"{name},{phone},{grade},{registration_number},{joining_date}\n")

        with open(STATS_FILE, "a") as file:
            file.write(f"{name},0,0,0\n")

        cont = input("Do you want to add another student? (y/n): ").lower()
        if cont != 'y':
            break

# --- View student attendance stats ---
def view_student_stats():
    while True:
        student_name = input("Enter the student's name: ").strip()

        if not os.path.exists(STATS_FILE):
            print("Master attendance file doesn't exist.")
            return

        found = False
        with open(STATS_FILE, "r") as file:
            for line in file:
                name, p, a, l = line.strip().split(",")
                if name.lower() == student_name.lower():
                    found = True
                    total_classes = int(p) + int(a) + int(l)
                    percentage = (int(p) / (total_classes - int(l))) * 100 if total_classes > 0 else 0

                    students = load_students()
                    for student in students:
                        if student[0].lower() == student_name.lower():
                            registration_number = student[3]
                            grade = student[2]
                            joining_date = student[4]
                            break

                    print(f"\nStats for {name}:")
                    print(f"Registration Number: {registration_number}")
                    print(f"Grade: {grade}")
                    print(f"Joining Date: {joining_date}")
                    print(f"Total Classes: {total_classes}")
                    print(f"Total Presents: {p}")
                    print(f"Total Leaves: {l}")
                    print(f"Total Absents: {a}")
                    print(f"Attendance Percentage: {percentage:.2f}%")
                    break

        if not found:
            print(f"No record found for {student_name}.")

        continue_check = input("\nDo you want to check another student's record? (y/n): ").lower()
        if continue_check != 'y':
            break

# --- Take attendance and send messages instantly ---
def take_attendance():
    students = load_students()

    use_custom_date = input("Do you want to enter a custom date for this attendance? (Y/N): ").strip().upper()
    if use_custom_date == "Y":
        while True:
            custom_date_input = input("Enter the date (YYYY-MM-DD): ").strip()
            try:
                datetime.datetime.strptime(custom_date_input, "%Y-%m-%d")
                today = custom_date_input
                break
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
    else:
        today = datetime.date.today().isoformat()

    if not os.path.exists(DAILY_DIR):
        os.makedirs(DAILY_DIR)

    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r") as file:
            all_records = file.readlines()
    else:
        all_records = [f"{student[0]},0,0,0\n" for student in students]
        with open(STATS_FILE, "w") as file:
            file.writelines(all_records)

    for i, student in enumerate(students):
        print(f"{i + 1}. {student[0]} (Grade {student[2]})")

    absent_students = []
    daily_lines = []

    for i, student in enumerate(students):
        while True:
            attendance = input(f"Enter attendance for {student[0]} (P/A/L): ").strip().upper()
            if attendance in ["P", "A", "L"]:
                break
            else:
                print("Invalid input. Please enter P (Present), A (Absent), or L (Leave).")

        daily_lines.append(f"{student[0]},{attendance}\n")

        for j, line in enumerate(all_records):
            name, p, a, l = line.strip().split(",")
            if name.lower() == student[0].lower():
                if attendance == "P":
                    all_records[j] = f"{name},{int(p)+1},{a},{l}\n"
                elif attendance == "A":
                    all_records[j] = f"{name},{p},{int(a)+1},{l}\n"
                    absent_students.append(student)
                elif attendance == "L":
                    all_records[j] = f"{name},{p},{a},{int(l)+1}\n"

    with open(STATS_FILE, "w") as file:
        file.writelines(all_records)

    with open(os.path.join(DAILY_DIR, f"{today}.txt"), "w") as daily_file:
        daily_file.writelines(daily_lines)

    for student in absent_students:
        phone_number = student[1]
        message = f"Assalam o Alaikum, {student[0]} is absent today.\nDate: {today}\nAhmed Ali"

        try:
            pwk.sendwhatmsg_instantly(phone_number, message, wait_time=15, tab_close=True, close_time=3)
        except Exception as e:
            print(f"Error sending message to {student[0]}: {e}")

    print("Attendance recorded and messages sent.")

# --- Backup Functionality ---
def create_backup():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    today = datetime.date.today()
    formatted_date = today.strftime("%d_%b_%Y")

    student_backup = os.path.join(BACKUP_DIR, f"students_{formatted_date}.txt")
    stats_backup = os.path.join(BACKUP_DIR, f"master_attendance_{formatted_date}.txt")

    shutil.copy(STUDENT_FILE, student_backup)
    shutil.copy(STATS_FILE, stats_backup)
    print("Backup created successfully.")

# --- Restore from Backup ---
def restore_backup():
    if not os.path.exists(BACKUP_DIR):
        print("No backup directory found.")
        return

    backups = os.listdir(BACKUP_DIR)
    student_backups = sorted([f for f in backups if f.startswith("students_")])
    stats_backups = sorted([f for f in backups if f.startswith("master_attendance_")])

    if not student_backups or not stats_backups:
        print("No backup files found.")
        return

    print("Available student backups:")
    for i, f in enumerate(student_backups):
        print(f"{i+1}. {f}")

    try:
        choice = int(input("Enter the number of the backup you want to restore: ")) - 1
        if 0 <= choice < len(student_backups):
            shutil.copy(os.path.join(BACKUP_DIR, student_backups[choice]), STUDENT_FILE)
            shutil.copy(os.path.join(BACKUP_DIR, stats_backups[choice]), STATS_FILE)
            print("Backup restored successfully.")
        else:
            
            print("Invalid choice.")
    except ValueError:
        print("Invalid input. Please enter a valid number.")

# --- View date-wise attendance for a student ---
def view_attendance_by_date():
    name = input("Enter student name: ").strip().lower()
    if not os.path.exists(DAILY_DIR):
        print("No daily attendance records found.")
        return

    print("\nSelect view option:")
    print("1. Show all records")
    print("2. Show only absent dates")
    choice = input("Enter your choice (1 or 2): ").strip()

    show_all = choice == "1"

    print(f"\nDate-wise attendance for {name.title()}:")
    found = False
    for filename in sorted(os.listdir(DAILY_DIR)):
        path = os.path.join(DAILY_DIR, filename)
        with open(path, "r") as f:
            for line in f:
                s_name, status = line.strip().split(",")
                if s_name.strip().lower() == name:
                    status = status.strip().upper()  # Handle 'A' or 'a'
                    if show_all or status == "A":
                        date_display = datetime.datetime.strptime(filename.replace('.txt', ''), '%Y-%m-%d').strftime('%d %b %Y')
                        print(f"{date_display}: {status}")
                        found = True

    if not found:
        print("No matching attendance records found.")

# --- View attendance for a specific date ---
def view_attendance_on_specific_date():
    if not os.path.exists(DAILY_DIR):
        print("No daily attendance records found.")
        return

    print("\nAvailable attendance dates:")
    files = sorted(os.listdir(DAILY_DIR))
    for idx, filename in enumerate(files):
        date_display = datetime.datetime.strptime(filename.replace('.txt', ''), '%Y-%m-%d').strftime('%d %b %Y')
        print(f"{idx+1}. {date_display}")

    try:
        choice = int(input("Enter the number of the date you want to view: ")) - 1
        if 0 <= choice < len(files):
            selected_file = files[choice]
            print(f"\nAttendance on {selected_file.replace('.txt','')}")
            with open(os.path.join(DAILY_DIR, selected_file), "r") as f:
                for line in f:
                    s_name, status = line.strip().split(",")
                    print(f"{s_name}: {status}")
        else:
            print("Invalid choice.")
    except ValueError:
        print("Invalid input. Please enter a valid number.")

# --- Edit attendance record for a specific date ---
def edit_attendance_record():
    if not os.path.exists(DAILY_DIR):
        print("No attendance records found.")
        return

    print("\nAvailable attendance dates:")
    files = sorted(os.listdir(DAILY_DIR))
    for idx, filename in enumerate(files):
        date_display = datetime.datetime.strptime(filename.replace('.txt', ''), '%Y-%m-%d').strftime('%d %b %Y')
        print(f"{idx+1}. {date_display}")

    try:
        choice = int(input("Select the date number to edit: ")) - 1
        if 0 <= choice < len(files):
            selected_file = files[choice]
            file_path = os.path.join(DAILY_DIR, selected_file)

            with open(file_path, "r") as f:
                lines = f.readlines()

            record_dict = {line.split(",")[0].strip(): line.split(",")[1].strip() for line in lines}

            while True:
                print("\nCurrent Records:")
                for name, status in record_dict.items():
                    print(f"{name}: {status}")

                name_to_edit = input("\nEnter the student's name to edit (or type 'done' to finish): ").strip()
                if name_to_edit.lower() == "done":
                    break

                if name_to_edit not in record_dict:
                    print("Student not found in this date's record.")
                    continue

                new_status = input(f"Enter new status for {name_to_edit} (P/A/L): ").strip().upper()
                if new_status not in ["P", "A", "L"]:
                    print("Invalid status. Use P, A, or L.")
                    continue

                old_status = record_dict[name_to_edit]
                record_dict[name_to_edit] = new_status

                # Update master record accordingly
                if os.path.exists(STATS_FILE):
                    with open(STATS_FILE, "r") as f:
                        master_lines = f.readlines()
                    for i in range(len(master_lines)):
                        parts = master_lines[i].strip().split(",")
                        if parts[0].lower() == name_to_edit.lower():
                            p, a, l = int(parts[1]), int(parts[2]), int(parts[3])
                            # Subtract old status
                            if old_status == "P":
                                p -= 1
                            elif old_status == "A":
                                a -= 1
                            elif old_status == "L":
                                l -= 1
                            # Add new status
                            if new_status == "P":
                                p += 1
                            elif new_status == "A":
                                a += 1
                            elif new_status == "L":
                                l += 1
                            master_lines[i] = f"{parts[0]},{p},{a},{l}\n"
                            break
                    with open(STATS_FILE, "w") as f:
                        f.writelines(master_lines)

            # Rewrite daily file
            with open(file_path, "w") as f:
                for name, status in record_dict.items():
                    f.write(f"{name},{status}\n")

            print("Attendance record updated.")
        else:
            print("Invalid choice.")
    except ValueError:
        print("Please enter a valid number.")

# --- Copy data to Excel file ---      
def txt_to_xls():
    folder_path = "Files"

    attendance_data = {}
    name_order = []  # To preserve the sequence of names from the first file

    # Get and sort all text files
    files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    files.sort()

    for idx, file_name in enumerate(files):
        date = file_name.replace('.txt', '')
        file_path = os.path.join(folder_path, file_name)

        with open(file_path, 'r') as file:
            for line in file:
                name, status = line.strip().split(',')

                # Add to name order list only on first file
                if name not in attendance_data:
                    attendance_data[name] = {}
                    if idx == 0:
                        name_order.append(name)

                attendance_data[name][date] = status

    # Add any new names (not in first file) to end of list
    for name in attendance_data:
        if name not in name_order:
            name_order.append(name)

    # Create DataFrame and reorder it
    df = pd.DataFrame.from_dict(attendance_data, orient='index')
    df.index.name = 'Student Name'
    df = df.loc[name_order]  # Reorder by original sequence

    # Save to Excel
    output_path = "All_Attendance.xlsx"
    df.to_excel(output_path)

    print(f"✅ Ordered attendance exported to '{output_path}' successfully!")


# --- Main menu ---
def main():
    print("Welcome to My Academy Attendance System")

    while True:
        print("\nMenu:")
        print("1. Add new student(s)")
        print("2. View student attendance stats")
        print("3. Take attendance and send absence messages")
        print("4. Create Backup")
        print("5. Restore from Backup")
        print("6. View date-wise attendance for a student")
        print("7. View attendance of a specific date")
        print("8. Edit attendance record for a date")
        print("9. Copy attendance to Excel file")
        print("10. Exit")

        choice = input("Choose an option: ").strip()
        if not choice.isdigit():
            print("Invalid input. Please enter a number.")
            continue

        if choice == '1':
            add_student()
        elif choice == '2':
            view_student_stats()
        elif choice == '3':
            take_attendance()
        elif choice == '4':
            create_backup()
        elif choice == '5':
            restore_backup()
        elif choice == '6':
            view_attendance_by_date()
        elif choice == '7':
            view_attendance_on_specific_date()
        elif choice == '8':
            edit_attendance_record()
        elif choice == '9':
            txt_to_xls()
        elif choice == '10':
            print("Goodbye! Exiting program.")
            break
        else:
            print("Invalid choice! Please enter a number between 1 and 9.")

        continue_menu = input("\nDo you want to go back to the main menu? (y/n): ").lower()
        if continue_menu != 'y':
            print("Goodbye! Exiting program.")
            break

if __name__ == "__main__":
    main()
