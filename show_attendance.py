import pandas as pd
import os
import tkinter as tk
from tkinter import *
import tkinter.ttk as ttk
import csv
import glob
from PIL import ImageTk, Image
import matplotlib.pyplot as plt
import matplotlib.figure as figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# From main.py - reuse color scheme
PRIMARY = "#2962FF"      # Primary blue color
SECONDARY = "#FF6D00"    # Orange accent color
DARK_BG = "#121212"      # Dark background
MEDIUM_BG = "#1E1E1E"    # Medium dark for cards
LIGHT_BG = "#2C2C2C"     # Light dark for input fields
TEXT_WHITE = "#FFFFFF"   # White text
TEXT_LIGHT = "#E0E0E0"   # Light text
TEXT_GRAY = "#9E9E9E"    # Gray text
GREEN = "#00C853"        # Success green
RED = "#F44336"          # Error red
YELLOW = "#FFD600"       # Warning yellow
ACCENT_HOVER = "#0039CB" # Hover color for primary buttons

def make_fullscreen(window):
    """Make a window fullscreen"""
    window.attributes('-fullscreen', True)
    
    # Add escape key binding to exit fullscreen
    def exit_fullscreen(event=None):
        window.attributes('-fullscreen', False)
        window.geometry('1280x720')
    
    # Close window with Ctrl+W
    def close_window(event=None):
        window.destroy()
    
    window.bind('<Escape>', exit_fullscreen)
    window.bind('<Control-w>', close_window)
    window.bind('<Control-q>', close_window)

def create_button(parent, text, command, bg=PRIMARY, fg=TEXT_WHITE, width=None, height=None):
    """Create a beautiful button with hover effect"""
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        font=("Segoe UI", 11, "bold"),
        bd=0,
        relief="flat",
        activebackground=ACCENT_HOVER,
        activeforeground=fg,
        cursor="hand2",
        padx=20,
        pady=10
    )
    
    if width:
        btn.config(width=width)
    if height:
        btn.config(height=height)
    
    # Add hover effect
    def on_enter(e):
        btn['background'] = ACCENT_HOVER if bg == PRIMARY else bg
    def on_leave(e):
        btn['background'] = bg
        
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    
    return btn

def create_entry(parent, width=None, placeholder=None):
    """Create a beautiful entry field with focus highlight"""
    # Create container frame with highlight effect
    container = tk.Frame(parent, bg=PRIMARY)
    
    # Create actual entry
    entry = tk.Entry(
        container,
        bg=LIGHT_BG,
        fg=TEXT_WHITE,
        font=("Segoe UI", 12),
        relief="flat",
        bd=0,
        insertbackground=TEXT_WHITE
    )
    
    if width:
        entry.config(width=width)
    
    # Pack with padding for better look
    entry.pack(padx=1, pady=1, fill=X, ipady=8)
    
    # Add focus effects
    def on_focus_in(event):
        container.config(bg=PRIMARY)
        
    def on_focus_out(event):
        container.config(bg=TEXT_GRAY)
        
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
    
    # Add placeholder text if provided
    if placeholder:
        entry.insert(0, placeholder)
        entry.config(fg=TEXT_GRAY)
        
        def on_entry_click(event):
            if entry.get() == placeholder:
                entry.delete(0, END)
                entry.config(fg=TEXT_WHITE)
                
        def on_focusout(event):
            if entry.get() == '':
                entry.insert(0, placeholder)
                entry.config(fg=TEXT_GRAY)
                
        entry.bind('<FocusIn>', on_entry_click)
        entry.bind('<FocusOut>', on_focusout)
    
    return container, entry

def show_popup(parent, title, message, type="info"):
    """Show a beautiful popup message"""
    popup = Toplevel(parent)
    popup.title(title)
    popup.configure(bg=DARK_BG)
    
    # Calculate position
    width, height = 400, 220
    x = (popup.winfo_screenwidth() - width) // 2
    y = (popup.winfo_screenheight() - height) // 2
    popup.geometry(f'{width}x{height}+{x}+{y}')
    popup.resizable(False, False)
    
    # Make modal
    popup.grab_set()
    popup.transient(parent)
    
    # Set icon based on type
    if type == "error":
        color = RED
        icon = "❌"
    elif type == "warning":
        color = YELLOW
        icon = "⚠️"
    else:  # info
        color = PRIMARY
        icon = "ℹ️"
    
    # Create content
    content = tk.Frame(popup, bg=DARK_BG, padx=20, pady=20)
    content.pack(fill=BOTH, expand=True)
    
    # Icon
    icon_label = tk.Label(content, text=icon, font=("Segoe UI", 32), bg=DARK_BG, fg=color)
    icon_label.pack(pady=(0, 15))
    
    # Message
    msg_label = tk.Label(
        content, 
        text=message, 
        font=("Segoe UI", 12), 
        bg=DARK_BG, 
        fg=TEXT_WHITE,
        wraplength=350,
        justify=CENTER
    )
    msg_label.pack(pady=(0, 20))
    
    # OK Button
    ok_btn = create_button(content, "OK", popup.destroy, bg=color, width=10)
    ok_btn.pack()
    
    return popup

def create_stat_card(parent, title, value, icon, color):
    """Create a statistics card with title, value, and icon"""
    card = tk.Frame(parent, bg=MEDIUM_BG, padx=20, pady=15, relief="flat")
    
    # Icon and title in top row
    top_row = tk.Frame(card, bg=MEDIUM_BG)
    top_row.pack(fill=X, anchor=W)
    
    icon_label = tk.Label(top_row, text=icon, font=("Segoe UI", 16), bg=MEDIUM_BG, fg=color)
    icon_label.pack(side=LEFT)
    
    title_label = tk.Label(
        top_row, 
        text=title, 
        font=("Segoe UI", 12),
        bg=MEDIUM_BG,
        fg=TEXT_GRAY
    )
    title_label.pack(side=LEFT, padx=10)
    
    # Value in bottom row
    value_label = tk.Label(
        card, 
        text=value, 
        font=("Segoe UI", 24, "bold"),
        bg=MEDIUM_BG,
        fg=TEXT_WHITE
    )
    value_label.pack(anchor=W, pady=(10, 0))
    
    return card

def subjectchoose():
    """Show attendance screen"""
    root = Tk()
    root.title("Attendance Records")
    root.configure(bg=DARK_BG)
    
    # Set a reasonable initial size instead of fullscreen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Use 80% of screen size or 1024x768, whichever is larger
    width = max(int(screen_width * 0.8), 1024)
    height = max(int(screen_height * 0.8), 768)
    
    # Center the window
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    root.geometry(f"{width}x{height}+{x}+{y}")
    root.minsize(800, 600)  # Set minimum size
    
    # Create a main frame with scrollbar
    main_container = Frame(root, bg=DARK_BG)
    main_container.pack(fill=BOTH, expand=True)
    
    # Add a canvas for scrolling
    canvas = Canvas(main_container, bg=DARK_BG, highlightthickness=0)
    scrollbar = Scrollbar(main_container, orient=VERTICAL, command=canvas.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    
    canvas.pack(side=LEFT, fill=BOTH, expand=True)
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Scrollable frame inside canvas
    scrollable_frame = Frame(canvas, bg=DARK_BG)
    scrollable_frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    
    # Configure scrolling
    def configure_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        
    def configure_window_size(event):
        canvas.itemconfig(scrollable_frame_id, width=event.width)
        
    scrollable_frame.bind("<Configure>", configure_scroll_region)
    canvas.bind("<Configure>", configure_window_size)
    
    # Add mouse wheel scrolling
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    # Header
    header = tk.Frame(scrollable_frame, bg=PRIMARY, height=70)
    header.pack(fill=X)
    
    header_title = tk.Label(
        header, 
        text="ATTENDANCE RECORDS", 
        bg=PRIMARY, 
        fg=TEXT_WHITE, 
        font=("Segoe UI", 18, "bold")
    )
    header_title.pack(side=LEFT, padx=30, pady=15)
    
    # Close button
    close_btn = tk.Button(
        header,
        text="✕",
        font=("Segoe UI", 18),
        bg=PRIMARY,
        fg=TEXT_WHITE,
        bd=0,
        relief="flat",
        activebackground=ACCENT_HOVER,
        activeforeground=TEXT_WHITE,
        command=root.destroy,
        cursor="hand2"
    )
    close_btn.pack(side=RIGHT, padx=30, pady=15)
    
    # Main content area with two-column layout
    content = tk.Frame(scrollable_frame, bg=DARK_BG)
    content.pack(fill=BOTH, expand=True, padx=50, pady=40)
    
    # Left column - Form
    left_column = tk.Frame(content, bg=DARK_BG)
    left_column.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 20))
    
    form_card = tk.Frame(left_column, bg=MEDIUM_BG, padx=40, pady=40)
    form_card.pack(fill=BOTH, expand=True)
    
    form_title = tk.Label(
        form_card, 
        text="Select Subject", 
        font=("Segoe UI", 20, "bold"),
        bg=MEDIUM_BG,
        fg=TEXT_WHITE
    )
    form_title.pack(anchor=W, pady=(0, 30))
    
    # Form fields
    fields_frame = tk.Frame(form_card, bg=MEDIUM_BG)
    fields_frame.pack(fill=X)
    
    # Subject field
    subject_label = tk.Label(
        fields_frame, 
        text="Subject Name", 
        font=("Segoe UI", 12),
        bg=MEDIUM_BG,
        fg=TEXT_WHITE,
        anchor=W
    )
    subject_label.pack(anchor=W, pady=(0, 10))
    
    subject_container, tx = create_entry(
        fields_frame, 
        width=30,
        placeholder="Enter subject name"
    )
    subject_container.pack(fill=X, pady=(0, 20))
    
    # Status message
    status_frame = tk.Frame(form_card, bg=MEDIUM_BG, height=100)
    status_frame.pack(fill=X, pady=20)
    
    status_label = tk.Label(
        status_frame, 
        text="Enter the subject name and click 'Check Attendance'", 
        font=("Segoe UI", 12),
        bg=MEDIUM_BG,
        fg=TEXT_LIGHT,
        anchor=W,
        wraplength=400,
        justify=LEFT
    )
    status_label.pack(fill=X)
    
    # Buttons
    button_frame = tk.Frame(form_card, bg=MEDIUM_BG)
    button_frame.pack(fill=X, pady=(30, 0))
    
    def calculate_attendance():
        """Handle check attendance button click"""
        sub = tx.get()
        
        if not sub:
            show_popup(root, "Error", "Please enter a subject name", "error")
            return
            
        status_label.config(text="Calculating attendance... Please wait")
        root.update()
        
        try:
            # Check if the subject directory exists
            path = f"Attendance\\{sub}"
            if not os.path.exists(path):
                error_msg = f"No attendance records found for subject: {sub}"
                status_label.config(text=error_msg, fg=RED)
                show_popup(root, "Error", error_msg, "error")
                return
                
            # Get all CSV files in the directory
            csv_files = glob.glob(os.path.join(path, f"{sub}*.csv"))
            
            if not csv_files:
                error_msg = f"No attendance records found for subject: {sub}"
                status_label.config(text=error_msg, fg=RED)
                show_popup(root, "Error", error_msg, "error")
                return
            
            # Create an empty DataFrame with just Enrollment and Name columns
            all_attendance = pd.DataFrame(columns=["Enrollment", "Name"])
            all_dates = []
            
            # First, collect all unique students from all files
            all_students = set()
            for file in csv_files:
                try:
                    # Read the CSV
                    df = pd.read_csv(file, dtype={"Enrollment": str, "Name": str})
                    # Add students to set
                    for _, row in df.iterrows():
                        if "Enrollment" in df.columns and "Name" in df.columns:
                            student_id = str(row["Enrollment"])
                            name = str(row["Name"]) 
                            all_students.add((student_id, name))
                except Exception as e:
                    print(f"Error reading file {file}: {e}")
            
            # Create the base DataFrame with all students
            student_data = []
            for student_id, name in all_students:
                student_data.append({"Enrollment": student_id, "Name": name})
            
            all_attendance = pd.DataFrame(student_data)
            
            # Process each file to extract date attendance
            for file in csv_files:
                try:
                    # Extract date from filename
                    filename = os.path.basename(file)
                    parts = filename.split('_')
                    if len(parts) >= 2:
                        date = parts[1].replace('-', '_')
                    else:
                        date = f"date_{len(all_dates)}"
                    
                    all_dates.append(date)
                    
                    # Create a column for this date with all zeros
                    all_attendance[date] = 0
                    
                    # Read the file
                    df = pd.read_csv(file, dtype={"Enrollment": str, "Name": str})
                    
                    # Mark present students
                    for _, row in df.iterrows():
                        if "Enrollment" in df.columns:
                            student_id = str(row["Enrollment"])
                            # Find this student in the all_attendance DataFrame
                            for i, student_row in all_attendance.iterrows():
                                if str(student_row["Enrollment"]) == student_id:
                                    all_attendance.at[i, date] = 1
                                    break
                except Exception as e:
                    print(f"Error processing attendance for {file}: {e}")
            
            # Calculate total and percentage
            all_attendance["Total"] = 0
            for date in all_dates:
                all_attendance["Total"] += all_attendance[date]
            
            total_classes = len(all_dates)
            if total_classes > 0:
                all_attendance["Percentage"] = (all_attendance["Total"] / total_classes) * 100
            else:
                all_attendance["Percentage"] = 0
            
            # Round percentage and ensure not above 100%
            all_attendance["Percentage"] = all_attendance["Percentage"].round(2)
            all_attendance["Percentage"] = all_attendance["Percentage"].apply(lambda x: min(x, 100))
            
            # Save the consolidated report
            report_path = os.path.join(path, f"{sub}_consolidated_report.csv")
            all_attendance.to_csv(report_path, index=False)
            
            # Update status
            success_msg = f"Attendance calculated for {sub}. Total classes: {total_classes}"
            status_label.config(text=success_msg, fg=GREEN)
            
            # Show the detailed report
            show_report(root, report_path, sub, total_classes, all_attendance)
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            status_label.config(text=error_msg, fg=RED)
            show_popup(root, "Error", error_msg, "error")
    
    def open_reports():
        """Open attendance reports folder"""
        sub = tx.get()
        if not sub:
            show_popup(root, "Warning", "Please enter a subject name", "warning")
            return
            
        path = f"Attendance\\{sub}"
        if os.path.exists(path):
            os.startfile(path)
            status_label.config(text=f"Opening records for: {sub}")
        else:
            show_popup(root, "Warning", f"No records found for subject: {sub}", "warning")
    
    # Check attendance button
    check_btn = create_button(
        button_frame, 
        "Check Attendance", 
        calculate_attendance,
        bg=GREEN,
        width=18,
        height=2
    )
    check_btn.pack(side=LEFT, padx=(0, 10))
    
    # View reports button
    view_btn = create_button(
        button_frame, 
        "View Reports", 
        open_reports,
        bg=PRIMARY,
        width=18,
        height=2
    )
    view_btn.pack(side=LEFT, padx=10)
    
    # Right column - Instructions & Info
    right_column = tk.Frame(content, bg=DARK_BG)
    right_column.pack(side=RIGHT, fill=BOTH, expand=True, padx=(20, 0))
    
    instruction_card = tk.Frame(right_column, bg=MEDIUM_BG, padx=40, pady=40)
    instruction_card.pack(fill=BOTH, expand=True)
    
    instruction_title = tk.Label(
        instruction_card, 
        text="Attendance Report Features", 
        font=("Segoe UI", 20, "bold"),
        bg=MEDIUM_BG,
        fg=TEXT_WHITE
    )
    instruction_title.pack(anchor=W, pady=(0, 20))
    
    features = [
        "1. View attendance statistics for any subject",
        "2. See detailed attendance for each student",
        "3. Check attendance percentage for the entire class",
        "4. Identify students with poor attendance",
        "5. Export attendance reports to CSV files",
        "6. Visualize attendance trends with charts",
        "7. View attendance by date"
    ]
    
    for feature in features:
        feature_label = tk.Label(
            instruction_card, 
            text=feature, 
            font=("Segoe UI", 12),
            bg=MEDIUM_BG,
            fg=TEXT_LIGHT,
            anchor=W,
            justify=LEFT
        )
        feature_label.pack(anchor=W, pady=10)
    
    # Add example image
    try:
        img = Image.open("UI_Image/attendance_report.png")
        img = img.resize((180, 180), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        img_label = tk.Label(instruction_card, image=photo, bg=MEDIUM_BG)
        img_label.image = photo
        img_label.pack(pady=20)
    except Exception as e:
        print(f"Could not load image: {e}")
    
    # Footer
    footer = tk.Frame(scrollable_frame, bg=MEDIUM_BG, height=40)
    footer.pack(fill=X, side=BOTTOM, pady=(20, 0))
    
    footer_text = tk.Label(
        footer, 
        text="© 2024 Smart Attendance System", 
        font=("Segoe UI", 10),
        bg=MEDIUM_BG,
        fg=TEXT_GRAY
    )
    footer_text.pack(pady=10)
    
    root.mainloop()

def show_report(parent, file_path, subject, total_classes, attendance_df):
    """Show consolidated attendance report in a modern UI"""
    report = Toplevel(parent)
    report.title(f"Attendance Report - {subject}")
    report.configure(bg=DARK_BG)
    make_fullscreen(report)
    
    # Header
    header = tk.Frame(report, bg=PRIMARY, height=70)
    header.pack(fill=X)
    
    header_title = tk.Label(
        header, 
        text=f"ATTENDANCE REPORT - {subject.upper()}", 
        bg=PRIMARY, 
        fg=TEXT_WHITE, 
        font=("Segoe UI", 18, "bold")
    )
    header_title.pack(side=LEFT, padx=30, pady=15)
    
    # Close button
    close_btn = tk.Button(
        header,
        text="✕",
        font=("Segoe UI", 18),
        bg=PRIMARY,
        fg=TEXT_WHITE,
        bd=0,
        relief="flat",
        activebackground=ACCENT_HOVER,
        activeforeground=TEXT_WHITE,
        command=report.destroy,
        cursor="hand2"
    )
    close_btn.pack(side=RIGHT, padx=30, pady=15)
    
    # Main content
    content = tk.Frame(report, bg=DARK_BG)
    content.pack(fill=BOTH, expand=True, padx=50, pady=20)
    
    # Statistics row
    stats_frame = tk.Frame(content, bg=DARK_BG)
    stats_frame.pack(fill=X, pady=(0, 20))
    
    # Calculate statistics
    try:
        avg_attendance = float(attendance_df["Percentage"].mean().round(2))
    except:
        avg_attendance = 0.0
    
    total_students = len(attendance_df)
    
    # Count categories using loops instead of direct filtering
    good_attendance = 0
    average_attendance = 0
    poor_attendance = 0
    
    for _, row in attendance_df.iterrows():
        try:
            percentage = float(row["Percentage"])
            if percentage >= 75:
                good_attendance += 1
            elif percentage >= 60:
                average_attendance += 1
            else:
                poor_attendance += 1
        except (ValueError, TypeError):
            # Handle problematic data
            poor_attendance += 1
    
    # Create stat cards
    # Average attendance
    avg_card = create_stat_card(
        stats_frame, 
        "Average Attendance", 
        f"{avg_attendance}%", 
        "📊", 
        PRIMARY
    )
    avg_card.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
    
    # Total students
    students_card = create_stat_card(
        stats_frame, 
        "Total Students", 
        str(total_students), 
        "👥", 
        SECONDARY
    )
    students_card.pack(side=LEFT, fill=BOTH, expand=True, padx=10)
    
    # Classes recorded
    classes_card = create_stat_card(
        stats_frame, 
        "Classes Recorded", 
        str(total_classes), 
        "📅", 
        SECONDARY
    )
    classes_card.pack(side=LEFT, fill=BOTH, expand=True, padx=10)
    
    # Add second row for attendance categories
    cats_frame = tk.Frame(content, bg=DARK_BG)
    cats_frame.pack(fill=X, pady=(0, 20))
    
    # Good attendance
    good_card = create_stat_card(
        cats_frame, 
        "Good Attendance (≥75%)", 
        str(good_attendance), 
        "🌟", 
        GREEN
    )
    good_card.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
    
    # Average attendance
    avg_att_card = create_stat_card(
        cats_frame, 
        "Average Attendance (60-74%)", 
        str(average_attendance), 
        "⚠️", 
        YELLOW
    )
    avg_att_card.pack(side=LEFT, fill=BOTH, expand=True, padx=10)
    
    # Poor attendance
    poor_card = create_stat_card(
        cats_frame, 
        "Poor Attendance (<60%)", 
        str(poor_attendance), 
        "⛔", 
        RED
    )
    poor_card.pack(side=LEFT, fill=BOTH, expand=True, padx=10)
    
    # Table frame
    table_frame = tk.Frame(content, bg=MEDIUM_BG)
    table_frame.pack(fill=BOTH, expand=True)
    
    # Create table with ttk.Treeview
    table_title = tk.Label(
        table_frame,
        text="Detailed Attendance Report",
        font=("Segoe UI", 16, "bold"),
        bg=MEDIUM_BG,
        fg=TEXT_WHITE,
        padx=20,
        pady=15
    )
    table_title.pack(anchor=W)
    
    # Create a styled treeview
    style = ttk.Style()
    style.theme_use("default")
    style.configure(
        "Treeview",
        background=LIGHT_BG,
        foreground=TEXT_WHITE,
        rowheight=40,
        fieldbackground=LIGHT_BG,
        font=("Segoe UI", 11)
    )
    style.configure(
        "Treeview.Heading",
        background=PRIMARY,
        foreground=TEXT_WHITE,
        relief="flat",
        font=("Segoe UI", 12, "bold")
    )
    style.map("Treeview", background=[("selected", SECONDARY)])
    
    # Create treeview inside a frame for padding
    tree_container = tk.Frame(table_frame, bg=MEDIUM_BG, padx=20, pady=15)
    tree_container.pack(fill=BOTH, expand=True)
    
    # Create the treeview
    cols = ["Enrollment", "Name", "Percentage"]
    tree = ttk.Treeview(tree_container, columns=cols, show='headings')
    
    # Set column headings
    tree.heading("Enrollment", text="Enrollment")
    tree.heading("Name", text="Student Name")
    tree.heading("Percentage", text="Attendance %")
    
    # Set column widths
    tree.column("Enrollment", anchor=CENTER, width=150)
    tree.column("Name", anchor=W, width=300)
    tree.column("Percentage", anchor=CENTER, width=150)
    
    # Insert data
    for index, row in attendance_df.iterrows():
        try:
            # Convert values to strings and handle any Series objects safely
            enrollment = str(row["Enrollment"]).strip() if not pd.isna(row["Enrollment"]) else ""
            
            # Handle name field - convert any complex objects to simple strings
            name = ""
            if not pd.isna(row["Name"]):
                name_val = row["Name"]
                if isinstance(name_val, (list, pd.Series)):
                    # Get first value from series or list
                    first_val = name_val.iloc[0] if hasattr(name_val, 'iloc') else name_val[0]
                    name = str(first_val).strip("[]'\"")
                else:
                    name = str(name_val).strip("[]'\"")
            
            # Handle percentage - ensure it's a valid number
            try:
                percentage = float(row["Percentage"])
                percentage_str = f"{percentage:.1f}%"
            except (ValueError, TypeError):
                percentage = 0.0
                percentage_str = "0.0%"
            
            # Set tag based on percentage value
            if percentage >= 75:
                tag = "good"
            elif percentage >= 60:
                tag = "average"
            else:
                tag = "poor"
                
            # Insert the row with proper string values
            tree.insert("", END, values=(enrollment, name, percentage_str), tags=(tag,))
            
        except Exception as e:
            print(f"Error adding row {index}: {e}")
            # Insert a placeholder row for problematic data
            tree.insert("", END, values=(f"Error in row {index}", "", "0.0%"), tags=("poor",))
    
    # Configure tags for color coding
    tree.tag_configure("good", background=LIGHT_BG, foreground=GREEN)
    tree.tag_configure("average", background=LIGHT_BG, foreground=YELLOW)
    tree.tag_configure("poor", background=LIGHT_BG, foreground=RED)
    
    # Add scrollbars
    vsb = ttk.Scrollbar(tree_container, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(tree_container, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    # Grid layout for tree and scrollbars
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    
    tree_container.grid_rowconfigure(0, weight=1)
    tree_container.grid_columnconfigure(0, weight=1)
    
    # Button panel
    button_panel = tk.Frame(content, bg=DARK_BG, pady=20)
    button_panel.pack(fill=X)
    
    # Export button
    export_btn = create_button(
        button_panel,
        "Open Report Location",
        lambda: os.startfile(os.path.dirname(file_path)),
        bg=SECONDARY,
        width=18,
        height=2
    )
    export_btn.pack(side=LEFT, padx=(0, 10))
    
    # View detailed button
    detailed_btn = create_button(
        button_panel,
        "Export Full Report",
        lambda: export_full_report(file_path, subject),
        bg=PRIMARY,
        width=18,
        height=2
    )
    detailed_btn.pack(side=LEFT, padx=10)
    
    # Close button
    close_btn = create_button(
        button_panel,
        "Close",
        report.destroy,
        bg=RED,
        width=12,
        height=2
    )
    close_btn.pack(side=RIGHT)
    
    # Footer
    footer = tk.Frame(report, bg=MEDIUM_BG, height=40)
    footer.pack(fill=X, side=BOTTOM)
    
    footer_text = tk.Label(
        footer, 
        text="© 2024 Smart Attendance System", 
        font=("Segoe UI", 10),
        bg=MEDIUM_BG,
        fg=TEXT_GRAY
    )
    footer_text.pack(pady=10)

def export_full_report(file_path, subject):
    """Export full attendance report to Excel"""
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Create a new Excel file with additional analysis
        export_path = file_path.replace('.csv', '_full_report.csv')
        df.to_csv(export_path, index=False)
        
        # Open the file
        os.startfile(export_path)
        
    except Exception as e:
        print(f"Error exporting full report: {e}")

if __name__ == "__main__":
    subjectchoose() 