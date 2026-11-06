# ============================================================
# DIGITAL STUDENT INFORMATION SYSTEM
# CONSOLE-BASED SYSTEM
# ============================================================

from datetime import datetime, date
import re

WIDTH = 60
MAX_ID_LENGTH = 12

# Common courses / fields (students may also type their own)
COURSES = [
    ("BSIT", "BS Information Technology"),
    ("BSCS", "BS Computer Science"),
    ("BSIS", "BS Information Systems"),
    ("BSBA", "BS Business Administration"),
    ("BSA", "BS Accountancy"),
    ("BSED", "BS Education"),
    ("BSN", "BS Nursing"),
    ("BSCE", "BS Civil Engineering"),
    ("BSHM", "BS Hospitality Management"),
]

# Lists for accounts
student_accounts = []
registrar_accounts = []
instructor_accounts = []

# Student information
student_ids = []
student_names = []
student_status = []
student_registered = []
student_courses = []
student_birthdays = []

# Student records
student_schedules = []
student_attendance = []


# ============================================================
# DISPLAY / FORMAT HELPERS
# ============================================================

def line():
    print("=" * WIDTH)


def current_datetime():
    # Example: October 09, 2026 | 02:30 PM
    return datetime.now().strftime("%B %d, %Y | %I:%M %p")


def title(text, show_date=False):
    line()
    print(text.center(WIDTH))
    if show_date:
        print(current_datetime().center(WIDTH))
    line()


def pause():
    input("\nPress ENTER to continue...")


def ask(prompt):
    # Input with extra spaces removed from both ends
    return input(prompt).strip()


def fit(text, width):
    # Keep long values from breaking the table layout.
    text = str(text)
    if width <= 3:
        return text[:width]
    if len(text) > width:
        return text[:width - 3] + "..."
    return text


def print_table(headers, rows, widths, aligns=None):
    # Draws a clean console table with aligned columns and a distinct header.
    # widths are the inner widths of the columns.
    # aligns supports "l" (left), "c" (center), and "r" (right).

    if not headers:
        print("No table columns to display.")
        return

    if len(headers) != len(widths):
        raise ValueError("The number of headers must match the number of column widths.")

    if aligns is None:
        aligns = ["l"] * len(widths)
    else:
        aligns = list(aligns[:len(widths)])
        aligns.extend(["l"] * (len(widths) - len(aligns)))

    # Use consistent minimum widths and safely handle incomplete rows.
    widths = [max(1, int(width)) for width in widths]
    border = "+" + "+".join("-" * (width + 2) for width in widths) + "+"
    header_border = "+" + "+".join("=" * (width + 2) for width in widths) + "+"

    def make_row(cells):
        cells = list(cells)
        if len(cells) < len(widths):
            cells.extend([""] * (len(widths) - len(cells)))

        parts = []
        for i, width in enumerate(widths):
            value = fit(cells[i], width)
            if aligns[i] == "r":
                value = value.rjust(width)
            elif aligns[i] == "c":
                value = value.center(width)
            else:
                value = value.ljust(width)
            parts.append(" " + value + " ")
        return "|" + "|".join(parts) + "|"

    print(border)
    print(make_row(headers))
    print(header_border)

    if not rows:
        print(make_row(["No records found."] + [""] * (len(widths) - 1)))
    else:
        for row in rows:
            print(make_row(row))
            print(border)
        return

    print(border)


def clean_spaces(text):
    # "  juan    dela cruz " -> "juan dela cruz"
    return " ".join(text.split())


def format_name(name):
    # "  juan   DELA cruz " -> "Juan Dela Cruz"
    return clean_spaces(name).title()


def format_subject(subject):
    # "math 101" -> "Math 101", but "IT 101" stays "IT 101"
    words = clean_spaces(subject).split(" ")
    return " ".join(word[:1].upper() + word[1:] for word in words)


def is_valid_username(username):
    # 4-30 characters; special characters are allowed, but spaces are not.
    # Examples: rich.glenn_01, rich@glenn!, Glenn#2026
    if not re.fullmatch(r"\S{4,30}", username):
        print("Invalid username. Use 4-30 characters with no spaces. Special characters are allowed.")
        print("Example: rich.glenn_01 or Glenn@2026!")
        return False
    return True


def is_valid_password(password):
    if len(password) < 6 or any(ch.isspace() for ch in password):
        print("Invalid password. Use at least 6 characters with no spaces.")
        print("Special characters are allowed. Example: Glenn@2026!")
        return False
    return True


def is_valid_schedule(schedule):
    # Required format: Mon, Wed, Fri 08:00 AM - 09:30 AM
    pattern = r"^([A-Za-z]+(?:\s*,\s*[A-Za-z]+)*)\s+(\d{1,2}:\d{2}\s*(?:AM|PM))\s*-\s*(\d{1,2}:\d{2}\s*(?:AM|PM))$"
    match = re.fullmatch(pattern, clean_spaces(schedule), re.IGNORECASE)
    if not match:
        print("Invalid schedule format. Use: Mon, Wed, Fri 08:00 AM - 09:30 AM")
        return False
    valid_days = {"mon", "monday", "tue", "tues", "tuesday", "wed", "wednesday",
                  "thu", "thur", "thurs", "thursday", "fri", "friday",
                  "sat", "saturday", "sun", "sunday"}
    days = [day.strip().lower() for day in match.group(1).split(",")]
    if any(day not in valid_days for day in days):
        print("Invalid day. Use day names such as Mon, Monday, or Friday.")
        return False
    try:
        start = datetime.strptime(match.group(2).upper().replace(" ", ""), "%I:%M%p")
        end = datetime.strptime(match.group(3).upper().replace(" ", ""), "%I:%M%p")
    except ValueError:
        print("Invalid time. Use a valid 12-hour time such as 08:30 AM.")
        return False
    if end <= start:
        print("Invalid time range. End time must be later than start time.")
        return False
    return True


def parse_birthday(text):
    # Accepts MM/DD/YYYY. Returns a date, or None if invalid.
    try:
        return datetime.strptime(text.strip(), "%m/%d/%Y").date()
    except ValueError:
        return None


def compute_age(birthday):
    today = date.today()
    had_birthday = (today.month, today.day) >= (birthday.month, birthday.day)
    return today.year - birthday.year - (0 if had_birthday else 1)


def format_birthday(birthday):
    # Example: March 15, 2005
    return birthday.strftime("%B %d, %Y")


def is_valid_birthday(text):
    birthday = parse_birthday(text)
    if birthday is None:
        print("Invalid birthday. Use MM/DD/YYYY. Example: 03/15/2005")
        return False
    if birthday > date.today():
        print("Birthday cannot be in the future.")
        return False
    if not 5 <= compute_age(birthday) <= 100:
        print("Invalid birthday. Student age must be between 5 and 100 years old.")
        return False
    return True


def ask_birthday():
    # Returns a date, or None if the input was invalid.
    print("Birthday format: MM/DD/YYYY  (Example: 03/15/2005)")
    text = ask("Birthday: ")
    if not is_valid_birthday(text):
        return None
    return parse_birthday(text)


def course_label(course):
    # "BSIT" -> "BSIT - BS Information Technology"; custom courses stay as typed.
    for code, name in COURSES:
        if code == course:
            return code + " - " + name
    return course


def ask_course():
    # Returns the chosen course/field, or None if invalid.
    print("\nCOURSE / FIELD")

    for number, (code, name) in enumerate(COURSES, 1):
        print("{:>2}. {} - {}".format(number, code, name))

    other = len(COURSES) + 1
    print("{:>2}. Other (type your own)".format(other))

    choice = ask("\nChoose course/field: ")

    if choice.isdigit() and 1 <= int(choice) <= len(COURSES):
        return COURSES[int(choice) - 1][0]

    if choice == str(other):
        custom = format_subject(ask("Enter course/field: "))

        if len(custom) < 2 or len(custom) > 40 or not any(ch.isalpha() for ch in custom):
            print("Invalid course/field. Use 2-40 characters with at least one letter.")
            return None

        # If they typed a known code (e.g. "bsit"), use the standard code.
        for code, name in COURSES:
            if custom.upper() == code:
                return code

        return custom

    print("Invalid choice.")
    return None


def ask_number(prompt):
    # Returns a whole number, or None if the input is not a number
    value = ask(prompt)

    if not value.isdigit():
        print("Numbers only.")
        return None

    return int(value)


# ============================================================
# CREATE ACCOUNT
# ============================================================

def create_account():

    title("CREATE ACCOUNT")

    print("1. Student")
    print("2. Registrar")
    print("3. Instructor")
    print("4. Back")

    choice = ask("\nChoose account type: ")

    if choice == "4":
        return

    if choice not in ("1", "2", "3"):
        print("Invalid choice.")
        pause()
        return

    username = ask("Create Username (special characters allowed): ")
    password = ask("Create Password (special characters allowed): ")

    if not is_valid_username(username) or not is_valid_password(password):
        pause()
        return

    if choice == "1":

        for account in student_accounts:
            if account[0].lower() == username.lower():
                print("Username taken.")
                pause()
                return

        student_accounts.append([username, password])
        print("\nStudent account created!")

    elif choice == "2":

        for account in registrar_accounts:
            if account[0].lower() == username.lower():
                print("Username taken.")
                pause()
                return

        registrar_accounts.append([username, password])
        print("\nRegistrar account created!")

    elif choice == "3":

        for account in instructor_accounts:
            if account[0].lower() == username.lower():
                print("Username taken.")
                pause()
                return

        instructor_accounts.append([username, password])
        print("\nInstructor account created!")

    pause()


# ============================================================
# LOGIN
# ============================================================

def login(accounts):

    username = ask("Username: ")
    password = ask("Password: ")

    for account in accounts:

        if account[0].lower() == username.lower() and account[1] == password:
            return True

    return False


# ============================================================
# VALIDATION
# ============================================================

def is_valid_name(name):
    # Required format: Last Name, First Name Middle Initial
    name = clean_spaces(name)
    if not name:
        print("Name is required.")
        return False
    if len(name) < 3 or len(name) > 60 or "," not in name:
        print("Invalid name format. Use: Last Name, First Name Middle Initial")
        print("Example: Kilaton, Rich Glenn R.")
        return False

    last_name, given_names = name.split(",", 1)
    if not last_name.strip() or not given_names.strip():
        print("Invalid name format. Use: Last Name, First Name Middle Initial")
        print("Example: Kilaton, Rich Glenn R.")
        return False

    if any(not (ch.isalpha() or ch in " ,.-'") for ch in name):
        print("Invalid name. Use letters, spaces, commas, apostrophes, periods, or hyphens only.")
        return False

    if not any(ch.isalpha() for ch in last_name) or not any(ch.isalpha() for ch in given_names):
        print("Invalid name. Enter a valid last name and first name.")
        return False

    return True


def is_valid_id(student_id):
    # Accept numeric IDs (1-8 digits) or the format YYYY-0000.
    if not student_id:
        print("ID is required.")
        return False
    if not re.fullmatch(r"(?:\d{1,8}|\d{4}-\d{4})", student_id):
        print("Invalid ID. Use 12345 or the format 2024-0001.")
        return False
    return True


def ask_student_id(label="Student ID"):
    # Keeps asking until the ID is valid. ENTER on empty = cancel.
    while True:

        student_id = ask(label + " (ENTER = cancel): ")

        if student_id == "":
            return None

        if is_valid_id(student_id):
            return student_id


# ============================================================
# FIND / SELECT STUDENT
# ============================================================

def find_student(student_id):

    for i in range(len(student_ids)):

        if student_ids[i] == student_id:
            return i

    return -1


def show_student_list(indexes=None, heading="REGISTERED STUDENTS"):
    # Shows students so the user does not have to remember or guess the ID.
    # Pass a list of indexes to show only those students (e.g. search results).

    print("\n" + heading)

    if len(student_ids) == 0:
        print("No students registered yet.")
        return False

    if indexes is None:
        indexes = list(range(len(student_ids)))

    rows = []

    for number, i in enumerate(indexes, 1):

        rows.append([
            str(number),
            student_ids[i],
            student_names[i],
            student_courses[i]
        ])

    print_table(
        ["No.", "Student ID", "Name", "Course / Field"],
        rows,
        [3, 10, 19, 14],
        ["c", "l", "l", "l"]
    )

    if len(indexes) == len(student_ids):
        print("Total students:", len(student_ids))
    else:
        print("Matches found: {} of {}".format(len(indexes), len(student_ids)))

    return True


def search_students(keyword):
    # Every word typed must appear somewhere in the student's
    # ID, name, course/field, or birthday (case-insensitive).
    words = keyword.lower().split()
    matches = []

    for i in range(len(student_ids)):

        text = " ".join([
            student_ids[i],
            student_names[i],
            student_courses[i],
            course_label(student_courses[i]),
            format_birthday(student_birthdays[i])
        ]).lower()

        if all(word in text for word in words):
            matches.append(i)

    return matches


def search_and_select():
    # Search, show the results, and let the user pick one.
    # Returns the student's index, or -1 if cancelled / nothing found.

    keyword = ask("Search ID, name, course, or birthday (ENTER = back): ")

    if keyword == "":
        return -1

    matches = search_students(keyword)

    if len(matches) == 0:
        print('No students matched "{}".'.format(keyword))
        return -1

    show_student_list(matches, "SEARCH RESULTS")
    print()

    while True:

        student_id = ask("Enter Student ID to select (ENTER = back): ")

        if student_id == "":
            return -1

        index = find_student(student_id)

        if index in matches:
            return index

        print("That ID is not in the search results.")


def pick_student(show_list=True):
    # Returns the student's index, or -1 if cancelled.
    # The user can type an ID directly, or type S to search.

    if len(student_ids) == 0:
        print("\nNo students registered yet.")
        pause()
        return -1

    if show_list:
        show_student_list()
        print()

    while True:

        entry = ask("Student ID, or S to search (ENTER = cancel): ")

        if entry == "":
            return -1

        if entry.lower() == "s":

            index = search_and_select()

            if index != -1:
                return index

            continue

        if not is_valid_id(entry):
            continue

        index = find_student(entry)

        if index != -1:
            return index

        print("ID not found. Try again, or type S to search.")


# ============================================================
# DISPLAY STUDENT INFORMATION
# ============================================================

def display_student(index):

    print("\nSTUDENT INFORMATION")

    print_table(
        ["Field", "Details"],
        [
            ["Student ID", student_ids[index]],
            ["Name", student_names[index]],
            ["Course / Field", course_label(student_courses[index])],
            ["Birthday", format_birthday(student_birthdays[index])],
            ["Age", str(compute_age(student_birthdays[index]))],
            ["Status", student_status[index]],
            ["Registered", student_registered[index]]
        ],
        [14, 39]
    )


def show_schedules(index):

    rows = []

    for i in range(len(student_schedules[index])):

        # Stored as "Subject - Schedule"
        parts = student_schedules[index][i].split(" - ", 1)

        subject = parts[0]
        schedule = parts[1] if len(parts) > 1 else ""

        rows.append([str(i + 1), subject, schedule])

    print_table(
        ["No.", "Subject", "Schedule"],
        rows,
        [4, 18, 28],
        ["c", "l", "l"]
    )


def find_schedule(index, subject):
    # Match the exact subject (not just the first letters)

    prefix = subject.lower() + " - "

    for i in range(len(student_schedules[index])):

        if student_schedules[index][i].lower().startswith(prefix):
            return i

    return -1


def show_attendance(index):

    rows = []

    for record in student_attendance[index]:

        subject = record[0]
        total_days = record[1]
        present = record[2]
        absent = record[3]

        if total_days > 0:
            percentage = (present / total_days) * 100
        else:
            percentage = 0

        rows.append([
            subject,
            total_days,
            present,
            absent,
            "{:.1f}%".format(percentage)
        ])

    print_table(
        ["Subject", "Days", "Present", "Absent", "Rate"],
        rows,
        [19, 5, 7, 6, 7],
        ["l", "c", "c", "c", "r"]
    )


def display_full_record(index):
    # Personal information + class schedule + attendance in one view.

    display_student(index)

    print("\nCLASS SCHEDULE")

    if len(student_schedules[index]) == 0:
        print("No class schedule yet.")
    else:
        show_schedules(index)

    print("\nATTENDANCE")

    if len(student_attendance[index]) == 0:
        print("No attendance records yet.")
    else:
        show_attendance(index)


# ============================================================
# STUDENT MENU
# ============================================================

def student_menu():

    title("STUDENT LOGIN")

    if len(student_accounts) == 0:

        print("No student accounts yet.")
        pause()
        return

    if login(student_accounts) == False:

        print("Invalid login.")
        pause()
        return

    print("\nLogin successful!\n")

    student_id = ask_student_id("Your Student ID")

    if student_id is None:
        return

    index = find_student(student_id)

    if index == -1:

        print("ID not found.")
        pause()
        return

    while True:

        title("STUDENT PORTAL", True)

        print("Welcome,", student_names[index])
        print()
        print("1. View Personal Information")
        print("2. View Attendance")
        print("3. View Class Schedule")
        print("4. Logout")

        choice = ask("\nChoose an option: ")

        # PERSONAL INFORMATION
        if choice == "1":

            display_student(index)
            pause()

        # ATTENDANCE
        elif choice == "2":

            title("MY ATTENDANCE")

            if len(student_attendance[index]) == 0:

                print("No attendance records.")

            else:

                show_attendance(index)

            pause()

        # CLASS SCHEDULE
        elif choice == "3":

            title("MY CLASS SCHEDULE")

            if len(student_schedules[index]) == 0:

                print("No class schedule.")

            else:

                show_schedules(index)

            pause()

        # LOGOUT
        elif choice == "4":

            print("Logging out...")
            break

        else:

            print("Invalid choice.")
            pause()


# ============================================================
# REGISTRAR - ADD STUDENT
# ============================================================

def add_student():

    title("ADD STUDENT")

    student_id = ask_student_id()

    if student_id is None:
        return

    if find_student(student_id) != -1:

        print("ID already exists.")
        pause()
        return

    print("Name format: Last Name, First Name Middle Initial")
    print("Example: Kilaton, Rich Glenn R.")
    name = ask("Student Name: ")

    if not is_valid_name(name):
        pause()
        return

    name = format_name(name)

    course = ask_course()

    if course is None:
        pause()
        return

    print()
    birthday = ask_birthday()

    if birthday is None:
        pause()
        return

    print("\n1. Regular")
    print("2. Irregular")

    choice = ask("Choose status: ")

    if choice == "1":

        status = "Regular"

    elif choice == "2":

        status = "Irregular"

    else:

        print("Invalid status.")
        pause()
        return

    student_ids.append(student_id)
    student_names.append(name)
    student_courses.append(course)
    student_birthdays.append(birthday)
    student_status.append(status)
    student_registered.append(datetime.now().strftime("%B %d, %Y"))

    student_schedules.append([])
    student_attendance.append([])

    print("\nStudent added!")
    display_student(len(student_ids) - 1)

    pause()


# ============================================================
# REGISTRAR / INSTRUCTOR - VIEW & SEARCH STUDENT
# ============================================================

def registrar_view_student():

    title("VIEW STUDENT")

    index = pick_student()

    if index == -1:
        return

    display_full_record(index)
    pause()


def search_student_menu():

    title("SEARCH STUDENT")

    if len(student_ids) == 0:

        print("No students registered yet.")
        pause()
        return

    print("Search by ID, name, course/field, or birthday.")
    print("Examples: kilaton | BSIT | 2024 | march\n")

    index = search_and_select()

    if index != -1:
        display_full_record(index)

    pause()


# ============================================================
# REGISTRAR - UPDATE STUDENT
# ============================================================

def update_student():

    title("UPDATE STUDENT")

    index = pick_student()

    if index == -1:
        return

    while True:

        title("UPDATE INFORMATION")

        print("Student:", student_names[index])
        print()
        print("1. Update Student ID")
        print("2. Update Student Name")
        print("3. Update Course / Field")
        print("4. Update Birthday")
        print("5. Update Status")
        print("6. Back")

        choice = ask("\nChoose an option: ")

        if choice == "1":

            new_id = ask_student_id("New Student ID")

            if new_id is None:

                continue

            if new_id == student_ids[index]:

                print("Same as current ID.")

            elif find_student(new_id) != -1:

                print("ID already exists.")

            else:

                student_ids[index] = new_id
                print("ID updated.")

            pause()

        elif choice == "2":

            print("Name format: Last Name, First Name Middle Initial")
            print("Example: Kilaton, Rich Glenn R.")
            new_name = ask("New Student Name: ")

            if is_valid_name(new_name):

                student_names[index] = format_name(new_name)
                print("Name updated.")

            pause()

        elif choice == "3":

            print("Current:", course_label(student_courses[index]))

            course = ask_course()

            if course is not None:

                student_courses[index] = course
                print("Course / Field updated.")

            pause()

        elif choice == "4":

            print("Current:", format_birthday(student_birthdays[index]))

            birthday = ask_birthday()

            if birthday is not None:

                student_birthdays[index] = birthday
                print("Birthday updated.")

            pause()

        elif choice == "5":

            print("\n1. Regular")
            print("2. Irregular")

            status = ask("Choose status: ")

            if status == "1":

                student_status[index] = "Regular"
                print("Status updated.")

            elif status == "2":

                student_status[index] = "Irregular"
                print("Status updated.")

            else:

                print("Invalid choice.")

            pause()

        elif choice == "6":

            break

        else:

            print("Invalid choice.")
            pause()


# ============================================================
# REGISTRAR - REMOVE STUDENT
# ============================================================

def remove_student():

    title("REMOVE STUDENT")

    index = pick_student()

    if index == -1:
        return

    display_student(index)

    print("\nThis will also delete the student's schedule and attendance.")
    confirm = ask("Type YES to confirm removal: ")

    if confirm.upper() != "YES":

        print("Removal cancelled.")
        pause()
        return

    student_ids.pop(index)
    student_names.pop(index)
    student_courses.pop(index)
    student_birthdays.pop(index)
    student_status.pop(index)
    student_registered.pop(index)
    student_schedules.pop(index)
    student_attendance.pop(index)

    print("Student removed.")
    pause()


# ============================================================
# REGISTRAR - MANAGE SCHEDULE
# ============================================================

def registrar_schedule():

    title("MANAGE SCHEDULE")

    index = pick_student()

    if index == -1:
        return

    print("\nStudent:", student_names[index])
    print()
    print("1. Add Schedule")
    print("2. Update Schedule")
    print("3. View Schedule")
    print("4. Back")

    choice = ask("\nChoose an option: ")

    if choice == "1":

        subject = format_subject(ask("Subject: "))
        schedule = clean_spaces(input("Schedule: "))

        if subject == "" or schedule == "":
            print("All fields required.")
        elif not is_valid_schedule(schedule):
            pass
        elif find_schedule(index, subject) != -1:

            print("Subject already scheduled.")

        else:

            student_schedules[index].append(
                subject + " - " + schedule
            )

            print("Schedule added.")

    elif choice == "2":

        if len(student_schedules[index]) == 0:

            print("No schedules yet.")

        else:

            print()
            show_schedules(index)
            print()

            number = ask_number("Schedule number: ")

            if number is None:

                pass

            elif number >= 1 and number <= len(
                student_schedules[index]
            ):

                new_schedule = clean_spaces(input("New Schedule: "))

                if new_schedule == "":
                    print("Schedule required.")
                elif not is_valid_schedule(new_schedule):
                    pass
                else:

                    old = student_schedules[index][number - 1]
                    subject = old.split(" - ")[0]

                    student_schedules[index][number - 1] = (
                        subject + " - " + new_schedule
                    )

                    print("Schedule updated.")

            else:

                print("Invalid number.")

    elif choice == "3":

        if len(student_schedules[index]) == 0:

            print("No schedule yet.")

        else:

            print()
            show_schedules(index)

    elif choice == "4":

        return

    else:

        print("Invalid choice.")

    pause()


# ============================================================
# REGISTRAR MENU
# ============================================================

def registrar_menu():

    title("REGISTRAR LOGIN")

    if len(registrar_accounts) == 0:

        print("No registrar accounts yet.")
        pause()
        return

    if login(registrar_accounts) == False:

        print("Invalid login.")
        pause()
        return

    print("\nLogin successful!")

    while True:

        title("REGISTRAR PORTAL", True)

        print("1. Add Student")
        print("2. View Student")
        print("3. Search Student")
        print("4. Update Student Information")
        print("5. Manage Class Schedule")
        print("6. Remove Student")
        print("7. Logout")

        choice = ask("\nChoose an option: ")

        if choice == "1":

            add_student()

        elif choice == "2":

            registrar_view_student()

        elif choice == "3":

            search_student_menu()

        elif choice == "4":

            update_student()

        elif choice == "5":

            registrar_schedule()

        elif choice == "6":

            remove_student()

        elif choice == "7":

            print("Logging out...")
            break

        else:

            print("Invalid choice.")
            pause()


# ============================================================
# INSTRUCTOR - ATTENDANCE
# ============================================================

def manage_attendance():

    title("ATTENDANCE MANAGEMENT")

    index = pick_student()

    if index == -1:
        return

    print("\nStudent:", student_names[index])

    subject = format_subject(ask("Subject: "))

    if subject == "":

        print("Subject is required.")
        pause()
        return

    print("\nEnter Attendance")

    total_days = ask_number("Total Days: ")

    if total_days is None:
        pause()
        return

    present = ask_number("Total Present: ")

    if present is None:
        pause()
        return

    absent = ask_number("Total Absent: ")

    if absent is None:
        pause()
        return

    if present + absent != total_days:

        print("Present + Absent must equal Total.")

        pause()
        return

    found = False

    for record in student_attendance[index]:

        if record[0].lower() == subject.lower():

            record[1] = total_days
            record[2] = present
            record[3] = absent

            found = True

    if found:

        print("\nAttendance updated.")

    else:

        student_attendance[index].append(
            [subject, total_days, present, absent]
        )

        print("\nAttendance added.")

    print("\nCurrent attendance for", student_names[index])
    show_attendance(index)

    pause()


# ============================================================
# INSTRUCTOR - SCHEDULE
# ============================================================

def instructor_schedule():

    title("SCHEDULE MANAGEMENT")

    index = pick_student()

    if index == -1:
        return

    print("\nStudent:", student_names[index])

    subject = format_subject(ask("Subject: "))
    schedule = clean_spaces(input("Schedule: "))

    if subject == "" or schedule == "":
        print("All fields required.")
        pause()
        return

    if not is_valid_schedule(schedule):
        pause()
        return

    position = find_schedule(index, subject)

    if position != -1:

        student_schedules[index][position] = (
            subject + " - " + schedule
        )

        print("Schedule updated.")

    else:

        student_schedules[index].append(
            subject + " - " + schedule
        )

        print("Schedule added.")

    print("\nCurrent schedule for", student_names[index])
    show_schedules(index)

    pause()


# ============================================================
# INSTRUCTOR MENU
# ============================================================

def instructor_menu():

    title("INSTRUCTOR LOGIN")

    if len(instructor_accounts) == 0:

        print("No instructor accounts yet.")
        pause()
        return

    if login(instructor_accounts) == False:

        print("Invalid login.")
        pause()
        return

    print("\nLogin successful!")

    while True:

        title("INSTRUCTOR PORTAL", True)

        print("1. Add / Update Attendance")
        print("2. Add / Update Class Schedule")
        print("3. View Student Information")
        print("4. Search Student")
        print("5. Logout")

        choice = ask("\nChoose an option: ")

        if choice == "1":

            manage_attendance()

        elif choice == "2":

            instructor_schedule()

        elif choice == "3":

            index = pick_student()

            if index != -1:

                display_full_record(index)
                pause()

        elif choice == "4":

            search_student_menu()

        elif choice == "5":

            print("Logging out...")
            break

        else:

            print("Invalid choice.")
            pause()


# ============================================================
# MAIN MENU
# ============================================================

def main():

    while True:

        title("DIGITAL STUDENT INFORMATION SYSTEM", True)

        print("1. Create Account")
        print("2. Student Login")
        print("3. Registrar Login")
        print("4. Instructor Login")
        print("5. Exit")

        choice = ask("\nChoose an option: ")

        if choice == "1":

            create_account()

        elif choice == "2":

            student_menu()

        elif choice == "3":

            registrar_menu()

        elif choice == "4":

            instructor_menu()

        elif choice == "5":

            print("\nThank you for using the system!")
            break

        else:

            print("Invalid choice.")
            pause()


# ============================================================
# START SYSTEM
# ============================================================

if __name__ == "__main__":
    main()
