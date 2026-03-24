import tkinter as tk
from tkinter import *
import os, cv2
import shutil
import csv
import numpy as np
from PIL import ImageTk, Image
import pandas as pd
import datetime
import time
import tkinter.ttk as ttk
import tkinter.font as font

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

# Paths
haarcasecade_path = "haarcascade_frontalface_default.xml"
trainimagelabel_path = "TrainingImageLabel\\Trainner.yml"
trainimage_path = "TrainingImage"
studentdetail_path = "StudentDetails\\studentdetails.csv"
attendance_path = "Attendance"

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

def subjectChoose(text_to_speech):
    """Take attendance screen"""
    root = Tk()
    root.title("Take Attendance")
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
    
    # Variable to track if camera is currently active
    camera_active = False
    
    # Function to properly clean up resources when window is closed
    def on_root_closing():
        # Make sure all OpenCV windows are closed and camera released
        cv2.destroyAllWindows()
        root.destroy()
    
    # Set protocol for window close
    root.protocol("WM_DELETE_WINDOW", on_root_closing)
    
    # Header
    header = tk.Frame(scrollable_frame, bg=PRIMARY, height=70)
    header.pack(fill=X)
    
    header_title = tk.Label(
        header, 
        text="TAKE ATTENDANCE", 
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
        command=on_root_closing,
        cursor="hand2"
    )
    close_btn.pack(side=RIGHT, padx=30, pady=15)
    
    # Main content area
    content = tk.Frame(scrollable_frame, bg=DARK_BG)
    content.pack(fill=BOTH, expand=True, padx=50, pady=40)
    
    # Left column - Form
    left_column = tk.Frame(content, bg=DARK_BG)
    left_column.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 20))
    
    form_card = tk.Frame(left_column, bg=MEDIUM_BG, padx=40, pady=40)
    form_card.pack(fill=BOTH, expand=True)
    
    form_title = tk.Label(
        form_card, 
        text="Subject Information", 
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
        text="Enter the subject name and click 'Start Attendance'", 
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
    
    def FillAttendance():
        """Handle start attendance button click"""
        sub = tx.get()
        
        if not sub:
            show_popup(root, "Error", "Please enter a subject name", "error")
            return
            
        status_label.config(text="Initializing camera... Please wait")
        root.update()
        
        try:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            try:
                recognizer.read(trainimagelabel_path)
            except Exception as e:
                error_msg = "Model not found. Please train the system first."
                status_label.config(text=error_msg, fg=RED)
                text_to_speech(error_msg)
                return
                
            facecasCade = cv2.CascadeClassifier(haarcasecade_path)
            
            # More flexible CSV loading with better error handling
            try:
                # Check if file exists first
                if not os.path.exists(studentdetail_path):
                    # Create the directory and file if it doesn't exist
                    os.makedirs(os.path.dirname(studentdetail_path), exist_ok=True)
                    with open(studentdetail_path, 'w', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(["Enrollment", "Name"])
                    error_msg = "No students registered yet. Please register students first."
                    status_label.config(text=error_msg, fg=RED)
                    text_to_speech(error_msg)
                    return
                
                # Try different loading approaches
                try:
                    # First attempt: Try standard load
                    df = pd.read_csv(studentdetail_path)
                except:
                    try:
                        # Second attempt: Try with explicit encoding
                        df = pd.read_csv(studentdetail_path, encoding='latin1')
                    except:
                        # Third attempt: Create a minimal dataframe if all else fails
                        df = pd.DataFrame(columns=["Enrollment", "Name"])
                
                # If no columns or completely different format, try to adapt
                if set(["Enrollment", "Name"]).issubset(set(df.columns)):
                    # Correct format with our expected columns
                    pass
                elif len(df.columns) >= 2:
                    # Assume the first two columns are enrollment and name
                    df = df.iloc[:, 0:2]
                    df.columns = ["Enrollment", "Name"]
                else:
                    # Create empty dataframe with correct structure
                    df = pd.DataFrame(columns=["Enrollment", "Name"])
                    error_msg = "Student details file has incorrect format. Using empty database."
                    status_label.config(text=error_msg, fg=RED)
                    text_to_speech(error_msg)
                
                # Check if there are any students in the file
                if len(df) == 0:
                    error_msg = "No students found in the database. Please register students first."
                    status_label.config(text=error_msg, fg=RED)
                    text_to_speech(error_msg)
                    return
                
                # Convert enrollment to string for consistent comparison
                df["Enrollment"] = df["Enrollment"].astype(str)
                
                # Print student count for debugging
                print(f"Loaded {len(df)} students from the database")
                
            except Exception as e:
                print(f"Error details: {str(e)}")
                # Just create a basic dataframe and continue
                df = pd.DataFrame(columns=["Enrollment", "Name"])
                error_msg = "Student details file has incorrect format. Please check the file."
                status_label.config(text=error_msg, fg=RED)
                text_to_speech(error_msg)
                return
            
            cam = cv2.VideoCapture(0)
            font = cv2.FONT_HERSHEY_SIMPLEX
            col_names = ["Enrollment", "Name"]
            attendance = pd.DataFrame(columns=col_names)
            
            # Show processing status
            status_label.config(text="Camera activated. Looking for faces... Please look at the camera.")
            root.update()
            
            now = time.time()
            future = now + 20  
            
            # Flag to track if we should break the loop
            should_break = False
            
            while not should_break:
                try:
                    ret, im = cam.read()
                    if not ret:
                        print("Failed to grab frame from camera")
                        break
                        
                    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                    faces = facecasCade.detectMultiScale(gray, 1.2, 5)
                    
                    for (x, y, w, h) in faces:
                        global Id
                        
                        Id, conf = recognizer.predict(gray[y : y + h, x : x + w])
                        if conf < 70:
                            global Subject
                            global aa
                            global date
                            global timeStamp
                            
                            Subject = sub
                            ts = time.time()
                            date = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                            timeStamp = datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S")
                            
                            # Better error handling for enrollment lookup
                            try:
                                # Handle different ID formats
                                try:
                                    # Try to convert to integer first (handles numeric IDs)
                                    str_id = str(int(Id))
                                except:
                                    # If that fails, just use as string
                                    str_id = str(Id)
                                
                                # Try multiple matching approaches
                                matched_rows = None
                                
                                # Approach 1: Direct string comparison
                                direct_match = df[df["Enrollment"] == str_id]
                                if not direct_match.empty:
                                    matched_rows = direct_match
                                else:
                                    # Approach 2: Case insensitive comparison
                                    case_match = df[df["Enrollment"].str.lower() == str_id.lower()]
                                    if not case_match.empty:
                                        matched_rows = case_match
                                    else:
                                        # Approach 3: Partial matching (if ID is longer than 4 chars)
                                        if len(str_id) > 4:
                                            partial_matches = df[df["Enrollment"].str.contains(str_id, na=False)]
                                            if not partial_matches.empty:
                                                matched_rows = partial_matches
                                
                                if matched_rows is not None and not matched_rows.empty:
                                    aa = matched_rows["Name"].values
                                    
                                    # Convert to simple string if it's an array or series
                                    if isinstance(aa, (np.ndarray, list)) and len(aa) > 0:
                                        aa_str = str(aa[0])
                                    else:
                                        aa_str = "Unknown"
                                        
                                    global tt
                                    tt = str_id + "-" + aa_str
                                    
                                    # Add to attendance dataframe
                                    attendance.loc[len(attendance)] = [str_id, aa_str]
                                    
                                    # Draw rectangle around face
                                    cv2.rectangle(im, (x, y), (x + w, y + h), (0, 260, 0), 4)
                                    cv2.putText(im, str(tt), (x + h, y), font, 1, (255, 255, 0,), 4)
                                else:
                                    # ID recognized but not in database
                                    Id = "Unknown"
                                    tt = str(Id) + " (ID not in database)"
                                    cv2.rectangle(im, (x, y), (x + w, y + h), (0, 165, 255), 7)
                                    cv2.putText(im, str(tt), (x + h, y), font, 1, (0, 165, 255), 4)
                            except Exception as e:
                                print(f"Error with enrollment: {e}")
                                Id = "Error"
                                tt = "Error enrollment!"
                                cv2.rectangle(im, (x, y), (x + w, y + h), (0, 0, 255), 7)
                                cv2.putText(im, str(tt), (x + h, y), font, 1, (0, 0, 255), 4)
                    
                    if time.time() > future:
                        should_break = True
                        
                    attendance = attendance.drop_duplicates(["Enrollment"], keep="first")
                    
                    # Create the window with proper name and flags
                    cv2.namedWindow("Taking Attendance...", cv2.WINDOW_NORMAL)
                    cv2.imshow("Taking Attendance...", im)
                    
                    key = cv2.waitKey(30) & 0xFF
                    if key == 27 or key == ord('q'):  # ESC or q key
                        should_break = True
                        
                except Exception as e:
                    print(f"Error in camera loop: {e}")
                    should_break = True
            
            # Always release camera before processing data
            cam.release()
            cv2.destroyAllWindows()
            
            # Process the attendance data
            ts = time.time()
            date = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
            timeStamp = datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S")
            Hour, Minute, Second = timeStamp.split(":")
            
            # Create directory if it doesn't exist
            path = os.path.join(attendance_path, Subject)
            if not os.path.exists(path):
                os.makedirs(path)
            
            # Make sure we have valid entries with proper string values
            cleaned_attendance = pd.DataFrame(columns=col_names)
            
            # Clean up the data before saving
            for index, row in attendance.iterrows():
                try:
                    enrollment = str(row["Enrollment"])
                    
                    # Handle name values that could be arrays or series
                    name_val = row["Name"]
                    if isinstance(name_val, (np.ndarray, list, pd.Series)):
                        if hasattr(name_val, 'size') and name_val.size > 0:
                            name = str(name_val[0])
                        elif len(name_val) > 0:
                            name = str(name_val[0])
                        else:
                            name = "Unknown"
                    else:
                        name = str(name_val)
                    
                    # Remove any brackets or quotes
                    name = name.replace("[", "").replace("]", "").replace("'", "").strip()
                    
                    # Add to cleaned dataframe
                    cleaned_attendance.loc[len(cleaned_attendance)] = [enrollment, name]
                except Exception as e:
                    print(f"Error cleaning attendance entry: {e}")
            
            # Add date column with 1s (present)
            cleaned_attendance[date] = 1
                
            # Save attendance file
            fileName = (
                f"{path}/"
                + Subject
                + "_"
                + date
                + "_"
                + Hour
                + "-"
                + Minute
                + "-"
                + Second
                + ".csv"
            )
            
            # Ensure no duplicate enrollments
            cleaned_attendance = cleaned_attendance.drop_duplicates(["Enrollment"], keep="first")
            cleaned_attendance.to_csv(fileName, index=False)
            
            # Update status
            success_msg = f"Attendance recorded successfully for {Subject}"
            status_label.config(text=success_msg, fg=GREEN)
            text_to_speech(success_msg)
            
            # Show results in a new window
            show_results(root, fileName, Subject, date, timeStamp, cleaned_attendance)
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            status_label.config(text=error_msg, fg=RED)
            text_to_speech("An error occurred while taking attendance")
            
            # Ensure camera and windows are always released/closed on error
            try:
                cam.release()
            except:
                pass
            cv2.destroyAllWindows()
    
    def Attf():
        """Open attendance folder"""
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
    
    # Start attendance button
    start_btn = create_button(
        button_frame, 
        "Start Attendance", 
        FillAttendance,
        bg=GREEN,
        width=18,
        height=2
    )
    start_btn.pack(side=LEFT, padx=(0, 10))
    
    # View records button
    view_btn = create_button(
        button_frame, 
        "View Records", 
        Attf,
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
        text="How to Take Attendance", 
        font=("Segoe UI", 20, "bold"),
        bg=MEDIUM_BG,
        fg=TEXT_WHITE
    )
    instruction_title.pack(anchor=W, pady=(0, 20))
    
    instructions = [
        "1. Enter the subject name in the field",
        "2. Click 'Start Attendance' to begin the process",
        "3. Look directly at the camera when prompted",
        "4. The system will automatically recognize faces",
        "5. Attendance will be recorded for recognized students",
        "6. The process will stop after 20 seconds",
        "7. Results will be displayed automatically"
    ]
    
    for instruction in instructions:
        instr_label = tk.Label(
            instruction_card, 
            text=instruction, 
            font=("Segoe UI", 12),
            bg=MEDIUM_BG,
            fg=TEXT_LIGHT,
            anchor=W,
            justify=LEFT
        )
        instr_label.pack(anchor=W, pady=10)
    
    # Add example image
    try:
        img = Image.open("UI_Image/attendance.png")
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

def show_results(parent, file_path, subject, date, time_stamp, attendance_df):
    """Show attendance results in a modern UI"""
    results = Toplevel(parent)
    results.title(f"Attendance Results - {subject}")
    results.configure(bg=DARK_BG)
    make_fullscreen(results)
    
    # Make sure all OpenCV windows are closed
    cv2.destroyAllWindows()
    
    # Function to handle window close
    def on_closing():
        cv2.destroyAllWindows()
        results.destroy()
    
    # Header
    header = tk.Frame(results, bg=PRIMARY, height=70)
    header.pack(fill=X)
    
    header_title = tk.Label(
        header, 
        text=f"ATTENDANCE RESULTS - {subject.upper()}", 
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
        command=on_closing,
        cursor="hand2"
    )
    close_btn.pack(side=RIGHT, padx=30, pady=15)
    
    # Set protocol for when window is closed with X button
    results.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Main content
    content = tk.Frame(results, bg=DARK_BG)
    content.pack(fill=BOTH, expand=True, padx=50, pady=20)
    
    # Info panel
    info_panel = tk.Frame(content, bg=MEDIUM_BG, padx=30, pady=20)
    info_panel.pack(fill=X, pady=(0, 20))
    
    # Date, time, and count info
    info_text = f"Date: {date} | Time: {time_stamp} | Students Present: {len(attendance_df)}"
    info_label = tk.Label(
        info_panel,
        text=info_text,
        font=("Segoe UI", 14),
        bg=MEDIUM_BG,
        fg=TEXT_WHITE
    )
    info_label.pack(anchor=W)
    
    # Table frame
    table_frame = tk.Frame(content, bg=MEDIUM_BG)
    table_frame.pack(fill=BOTH, expand=True)
    
    # Create table with ttk.Treeview
    table_title = tk.Label(
        table_frame,
        text="Attendance Details",
        font=("Segoe UI", 18, "bold"),
        bg=MEDIUM_BG,
        fg=TEXT_WHITE,
        padx=30,
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
    tree_container = tk.Frame(table_frame, bg=MEDIUM_BG, padx=30, pady=15)
    tree_container.pack(fill=BOTH, expand=True)
    
    # Create the treeview
    tree = ttk.Treeview(tree_container)
    
    # Get the column names from the CSV
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)
        
        # Configure columns
        tree["columns"] = headers
        tree["show"] = "headings"
        
        # Set column headings
        for col in headers:
            tree.heading(col, text=col)
            tree.column(col, anchor=CENTER, width=200)
        
        # Insert data
        for row in reader:
            tree.insert("", END, values=row)
    
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
        "Open File Location",
        lambda: os.startfile(os.path.dirname(file_path)),
        bg=SECONDARY,
        width=18,
        height=2
    )
    export_btn.pack(side=LEFT, padx=(0, 10))
    
    # Close button
    close_btn = create_button(
        button_panel,
        "Close",
        results.destroy,
        bg=RED,
        width=12,
        height=2
    )
    close_btn.pack(side=RIGHT)
    
    # Footer
    footer = tk.Frame(results, bg=MEDIUM_BG, height=40)
    footer.pack(fill=X, side=BOTTOM)
    
    footer_text = tk.Label(
        footer, 
        text="© 2024 Smart Attendance System", 
        font=("Segoe UI", 10),
        bg=MEDIUM_BG,
        fg=TEXT_GRAY
    )
    footer_text.pack(pady=10)

if __name__ == "__main__":
    # For testing
    def dummy_tts(text):
        print(f"TTS: {text}")
    
    subjectChoose(dummy_tts) 