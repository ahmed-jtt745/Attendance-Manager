import pywhatkit as pwk
import datetime
import os
import shutil
import pandas as pd

STUDENT_FILE = "students.txt"
STATS_FILE = "master_attendance.txt"
DAILY_DIR = "daily_attendance"
BACKUP_DIR = "backups"
DELETED_STUDENTS_FILE = "deleted_students.txt"

# --- Load existing students from file ---
def load_students():
    students = []
    if not os.path.exists(STUDENT_FILE):
        return students
    
    deleted_students = []
    if os.path.exists(DELETED_STUDENTS_FILE):
        with open(DELETED_STUDENTS_FILE, "r") as file:
            deleted_students = [line.strip().lower() for line in file]

    with open(STUDENT_FILE, "r") as file:
        for line in file:
            parts = line.strip().split(",")
            if len(parts) == 5:
                name, phone, grade, reg_num, joining_date = parts
                if name.lower() not in deleted_students:
                    students.append((name, phone, grade, reg_num, joining_date))
    return students

# --- Add new students to the file ---
def add_student():
    while True:
        grade = input("Enter student grade: ").strip()
        name = input("Enter student name: ").title()
        phone = input("Enter parent's phone number: ")

        # Count total students from file to ensure unique registration numbers
        total_students = 0
        if os.path.exists(STUDENT_FILE):
            with open(STUDENT_FILE, "r") as file:
                total_students = len(file.readlines())

        reg_number = total_students + 1
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

def delete_student():
    students = load_students()
    if not students:
        print("No active students to delete.")
        return

    print("\nSelect a student to delete:")
    for i, student in enumerate(students):
        print(f"{i+1}. {student[0]} (Reg: {student[3]})")

    try:
        choice = int(input("Enter the number of the student to delete: ")) - 1
        if 0 <= choice < len(students):
            student_to_delete = students[choice][0]
            with open(DELETED_STUDENTS_FILE, "a") as file:
                file.write(f"{student_to_delete}\n")
            print(f"Student '{student_to_delete}' marked as deleted. Their records are kept, but they will not appear in future attendance or reports.")
        else:
            print("Invalid choice.")
    except ValueError:
        print("Invalid input. Please enter a valid number.")

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
    send_messages = True

    use_custom_date = input("Do you want to enter a custom date for this attendance? (Y/N): ").strip().upper()
    if use_custom_date == "Y":
        send_messages = False
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

    if send_messages:
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
    if not os.path.exists(DAILY_DIR):
        print("No daily attendance records found to export.")
        return

    # Prompt user for month and year
    month_input = input("Enter the month name to export (e.g., September): ").strip().title()
    year_input = input("Enter the year (e.g., 2024): ").strip()
    
    try:
        month_number = datetime.datetime.strptime(month_input, "%B").month
    except ValueError:
        print("Invalid month name. Please enter a full month name like 'September'.")
        return

    attendance_data = {}
    name_order = []

    files_to_process = []
    for filename in sorted(os.listdir(DAILY_DIR)):
        if filename.endswith('.txt'):
            try:
                file_date = datetime.datetime.strptime(filename.replace('.txt', ''), "%Y-%m-%d")
                if file_date.month == month_number and file_date.year == int(year_input):
                    files_to_process.append(filename)
            except ValueError:
                continue

    if not files_to_process:
        print("No attendance records found for the specified month.")
        return

    for idx, file_name in enumerate(files_to_process):
        date = file_name.replace('.txt', '')
        file_path = os.path.join(DAILY_DIR, file_name)

        with open(file_path, 'r') as file:
            for line in file:
                name, status = line.strip().split(',')
                
                deleted_students = []
                if os.path.exists(DELETED_STUDENTS_FILE):
                    with open(DELETED_STUDENTS_FILE, "r") as del_file:
                        deleted_students = [line.strip().lower() for line in del_file]
                
                if name.lower() not in deleted_students:
                    if name not in attendance_data:
                        attendance_data[name] = {}
                        if idx == 0:
                            name_order.append(name)

                    attendance_data[name][date] = status

    for name in attendance_data:
        if name not in name_order:
            name_order.append(name)

    df = pd.DataFrame.from_dict(attendance_data, orient='index')
    df.index.name = 'Student Name'
    df = df.loc[name_order]
    
    # Check if the dataframe is empty
    if df.empty:
        print("No active student records to export for the specified month.")
        return

    output_path = f"Attendance_{month_input}_{year_input}.xlsx"
    df.to_excel(output_path)

    print(f"✅ Ordered attendance for {month_input} {year_input} exported to '{output_path}' successfully!")

def print_student_stats():
    while True:
        print("\nView and Export Student Stats:")
        print("1. All Records")
        print("2. Specific Month")
        print("3. Back to Student Management Menu")
        sub_choice = input("Choose an option: ").strip()

        if sub_choice == '1':
            if not os.path.exists(STATS_FILE):
                print("Master attendance file doesn't exist.")
                return

            stats_data = {}
            with open(STATS_FILE, "r") as f:
                for line in f:
                    name, p, a, l = line.strip().split(',')
                    stats_data[name] = {'Presents': int(p), 'Absents': int(a), 'Leaves': int(l)}

            students = load_students()
            
            # Prepare data for table
            table_data = []
            for student in students:
                name = student[0]
                reg_num = student[3]
                if name in stats_data:
                    presents = stats_data[name]['Presents']
                    absents = stats_data[name]['Absents']
                    leaves = stats_data[name]['Leaves']
                    total_classes = presents + absents + leaves
                    
                    if total_classes > 0 and (total_classes - leaves) > 0:
                        percentage = (presents / (total_classes - leaves)) * 100
                    else:
                        percentage = 0
                    
                    table_data.append([name, reg_num, presents, absents, leaves, f"{percentage:.2f}%"])
            
            # Print the formatted table
            if not table_data:
                print("No active student stats found.")
                continue

            # Calculate column widths dynamically
            name_width = max(len('Name'), max(len(row[0]) for row in table_data))
            regno_width = max(len('Regno'), max(len(row[1]) for row in table_data))
            presents_width = max(len('Presents'), max(len(str(row[2])) for row in table_data))
            absents_width = max(len('Absents'), max(len(str(row[3])) for row in table_data))
            leaves_width = max(len('Leaves'), max(len(str(row[4])) for row in table_data))
            percentage_width = max(len('Percentage'), max(len(row[5]) for row in table_data))

            header_format = f"| {{:^{name_width}}} | {{:^{regno_width}}} | {{:^{presents_width}}} | {{:^{absents_width}}} | {{:^{leaves_width}}} | {{:^{percentage_width}}} |"
            row_format = f"| {{:^{name_width}}} | {{:^{regno_width}}} | {{:^{presents_width}}} | {{:^{absents_width}}} | {{:^{leaves_width}}} | {{:^{percentage_width}}} |"
            line = "-" * (name_width + regno_width + presents_width + absents_width + leaves_width + percentage_width + 17)

            print("\n" + line)
            print(header_format.format('Name', 'Regno', 'Presents', 'Absents', 'Leaves', 'Percentage'))
            print(line)

            for row in table_data:
                print(row_format.format(row[0], row[1], row[2], row[3], row[4], row[5]))
                print(line)

        elif sub_choice == '2':
            month_input = input("Enter the month name to view stats (e.g., September): ").strip().title()
            year_input = input("Enter the year (e.g., 2024): ").strip()

            try:
                month_number = datetime.datetime.strptime(month_input, "%B").month
            except ValueError:
                print("Invalid month name. Please enter a full month name like 'September'.")
                continue

            monthly_stats = {}
            students_info = {s[0]: s for s in load_students()}

            if not os.path.exists(DAILY_DIR):
                print("No daily attendance records found.")
                continue

            files_to_process = []
            for filename in sorted(os.listdir(DAILY_DIR)):
                if filename.endswith('.txt'):
                    try:
                        file_date = datetime.datetime.strptime(filename.replace('.txt', ''), "%Y-%m-%d")
                        if file_date.month == month_number and file_date.year == int(year_input):
                            files_to_process.append(filename)
                    except ValueError:
                        continue

            if not files_to_process:
                print(f"No attendance records found for {month_input} {year_input}.")
                continue

            for file_name in files_to_process:
                file_path = os.path.join(DAILY_DIR, file_name)
                with open(file_path, 'r') as file:
                    for line in file:
                        name, status = line.strip().split(',')
                        name = name.strip()
                        status = status.strip().upper()

                        if name in students_info:
                            if name not in monthly_stats:
                                monthly_stats[name] = {'Presents': 0, 'Absents': 0, 'Leaves': 0}
                            
                            if status == 'P':
                                monthly_stats[name]['Presents'] += 1
                            elif status == 'A':
                                monthly_stats[name]['Absents'] += 1
                            elif status == 'L':
                                monthly_stats[name]['Leaves'] += 1
            
            table_data = []
            for name, stats in monthly_stats.items():
                reg_num = students_info[name][3]
                presents = stats['Presents']
                absents = stats['Absents']
                leaves = stats['Leaves']
                total_classes = presents + absents + leaves

                if total_classes > 0 and (total_classes - leaves) > 0:
                    percentage = (presents / (total_classes - leaves)) * 100
                else:
                    percentage = 0
                
                table_data.append([name, reg_num, presents, absents, leaves, f"{percentage:.2f}%"])

            # Print the formatted table
            if not table_data:
                print(f"No active student stats found for {month_input} {year_input}.")
                continue

            # Calculate column widths dynamically
            name_width = max(len('Name'), max(len(row[0]) for row in table_data))
            regno_width = max(len('Regno'), max(len(row[1]) for row in table_data))
            presents_width = max(len('Presents'), max(len(str(row[2])) for row in table_data))
            absents_width = max(len('Absents'), max(len(str(row[3])) for row in table_data))
            leaves_width = max(len('Leaves'), max(len(str(row[4])) for row in table_data))
            percentage_width = max(len('Percentage'), max(len(row[5]) for row in table_data))

            header_format = f"| {{:^{name_width}}} | {{:^{regno_width}}} | {{:^{presents_width}}} | {{:^{absents_width}}} | {{:^{leaves_width}}} | {{:^{percentage_width}}} |"
            row_format = f"| {{:^{name_width}}} | {{:^{regno_width}}} | {{:^{presents_width}}} | {{:^{absents_width}}} | {{:^{leaves_width}}} | {{:^{percentage_width}}} |"
            line = "-" * (name_width + regno_width + presents_width + absents_width + leaves_width + percentage_width + 17)

            print("\n" + line)
            print(header_format.format('Name', 'Regno', 'Presents', 'Absents', 'Leaves', 'Percentage'))
            print(line)

            for row in table_data:
                print(row_format.format(row[0], row[1], row[2], row[3], row[4], row[5]))
                print(line)

        elif sub_choice == '3':
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 3.")


# --- Main menu ---
def main():
    print("Welcome to My Academy Attendance System")

    while True:
        print("\nMenu:")
        print("1. Student Management")
        print("2. Take attendance")
        print("3. Backup")
        print("4. View and Edit Attendance Records")
        print("5. Copy to Excel file")
        print("6. Exit")

        choice = input("Choose an option: ").strip()
        if not choice.isdigit():
            print("Invalid input. Please enter a number.")
            continue

        if choice == '1':
            while True:
                print("\nStudent Management:")
                print("1. Add new student(s)")
                print("2. Delete a student")
                print("3. View student attendance stats (Specific Student)")
                print("4. View date-wise attendance for a student")
                print("5. View Student Stats (Table Format)")
                print("6. Back to Main Menu")
                
                sub_choice = input("Choose an option: ").strip()
                if sub_choice == '1':
                    add_student()
                elif sub_choice == '2':
                    delete_student()
                elif sub_choice == '3':
                    view_student_stats()
                elif sub_choice == '4':
                    view_attendance_by_date()
                elif sub_choice == '5':
                    print_student_stats()
                elif sub_choice == '6':
                    break
                else:
                    print("Invalid choice. Please enter a number between 1 and 6.")

        elif choice == '2':
            take_attendance()
        elif choice == '3':
            while True:
                print("\nBackup:")
                print("1. Create Backup")
                print("2. Restore from Backup")
                print("3. Back to Main Menu")

                sub_choice = input("Choose an option: ").strip()
                if sub_choice == '1':
                    create_backup()
                elif sub_choice == '2':
                    restore_backup()
                elif sub_choice == '3':
                    break
                else:
                    print("Invalid choice. Please enter a number between 1 and 3.")

        elif choice == '4':
            while True:
                print("\nView and Edit Attendance:")
                print("1. View attendance of a specific date")
                print("2. Edit attendance record for a date")
                print("3. Back to Main Menu")

                sub_choice = input("Choose an option: ").strip()
                if sub_choice == '1':
                    view_attendance_on_specific_date()
                elif sub_choice == '2':
                    edit_attendance_record()
                elif sub_choice == '3':
                    break
                else:
                    print("Invalid choice. Please enter a number between 1 and 3.")

        elif choice == '5':
            txt_to_xls()
        elif choice == '6':
            print("Goodbye! Exiting program.")
            break
        else:
            print("Invalid choice! Please enter a number between 1 and 6.")

        continue_menu = input("\nDo you want to go back to the main menu? (y/n): ").lower()
        if continue_menu != 'y':
            print("Goodbye! Exiting program.")
            break

if __name__ == "__main__":
    main()