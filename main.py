import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
import os
import cv2
import csv
import time
import numpy as np
import pandas as pd
from PIL import ImageTk, Image
import datetime
import pyttsx3

# Paths
haarcasecade_path = "haarcascade_frontalface_default.xml"
trainimagelabel_path = "TrainingImageLabel\\Trainner.yml"
trainimage_path = "TrainingImage"
studentdetail_path = "StudentDetails\\studentdetails.csv"
attendance_path = "Attendance"

# Modern color scheme
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

# Initialize text to speech engine
engine = pyttsx3.init()

def text_to_speech(text):
    """Convert text to speech"""
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"TTS Error: {e}")

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

def check_haarcascade_file():
    """Check if haarcascade file exists"""
    if not os.path.exists(haarcasecade_path):
        print(f"Error: {haarcasecade_path} not found")
        return False
    return True

def check_directories():
    """Create required directories if they don't exist"""
    if not os.path.exists(trainimage_path):
        os.makedirs(trainimage_path)
    
    if not os.path.exists("TrainingImageLabel"):
        os.makedirs("TrainingImageLabel")
    
    if not os.path.exists("StudentDetails"):
        os.makedirs("StudentDetails")
        # Create the CSV file with headers
        try:
            with open(studentdetail_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Enrollment", "Name"])
            print("Created studentdetails.csv with headers")
        except Exception as e:
            print(f"Error creating studentdetails.csv: {e}")
    elif not os.path.exists(studentdetail_path):
        # File directory exists but file doesn't
        try:
            with open(studentdetail_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Enrollment", "Name"])
            print("Created missing studentdetails.csv with headers")
        except Exception as e:
            print(f"Error creating studentdetails.csv: {e}")
    
    if not os.path.exists(attendance_path):
        os.makedirs(attendance_path)
    
    return True

def register_student_screen():
    """Register new student screen"""
    root = Tk()
    root.title("Register Student")
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
        text="REGISTER & TRAIN STUDENTS", 
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
        text="Student Information", 
        font=("Segoe UI", 20, "bold"),
        bg=MEDIUM_BG,
        fg=TEXT_WHITE
    )
    form_title.pack(anchor=W, pady=(0, 30))
    
    # Form fields
    fields_frame = tk.Frame(form_card, bg=MEDIUM_BG)
    fields_frame.pack(fill=X)
    
    # Enrollment field
    enrollment_label = tk.Label(
        fields_frame, 
        text="Enrollment Number", 
        font=("Segoe UI", 12),
        bg=MEDIUM_BG,
        fg=TEXT_WHITE,
        anchor=W
    )
    enrollment_label.pack(anchor=W, pady=(0, 10))
    
    enrollment_container, enrollment_entry = create_entry(
        fields_frame, 
        width=30,
        placeholder="Enter enrollment number"
    )
    enrollment_container.pack(fill=X, pady=(0, 20))
    
    # Name field
    name_label = tk.Label(
        fields_frame, 
        text="Student Name", 
        font=("Segoe UI", 12),
        bg=MEDIUM_BG,
        fg=TEXT_WHITE,
        anchor=W
    )
    name_label.pack(anchor=W, pady=(0, 10))
    
    name_container, name_entry = create_entry(
        fields_frame, 
        width=30,
        placeholder="Enter student name"
    )
    name_container.pack(fill=X, pady=(0, 20))
    
    # Status message
    status_frame = tk.Frame(form_card, bg=MEDIUM_BG, height=100)
    status_frame.pack(fill=X, pady=20)
    
    status_label = tk.Label(
        status_frame, 
        text="Fill in the details and click 'Take Images' to capture student images", 
        font=("Segoe UI", 12),
        bg=MEDIUM_BG,
        fg=TEXT_LIGHT,
        anchor=W,
        wraplength=400,
        justify=LEFT
    )
    status_label.pack(fill=X)
    
    # Image counter display
    counter_frame = tk.Frame(form_card, bg=MEDIUM_BG)
    counter_frame.pack(fill=X, pady=(0, 20))
    
    counter_label = tk.Label(
        counter_frame,
        text="Images: 0/50",
        font=("Segoe UI", 14, "bold"),
        bg=MEDIUM_BG,
        fg=TEXT_WHITE
    )
    counter_label.pack(side=LEFT)
    
    # Variables to store student info
    global Id
    global name
    
    def clear_fields():
        """Clear input fields"""
        enrollment_entry.delete(0, END)
        name_entry.delete(0, END)
        status_label.config(text="Form cleared. Ready for new entry.", fg=TEXT_LIGHT)
        counter_label.config(text="Images: 0/50")
    
    def take_images():
        """Capture images for student registration"""
        # Get the enrollment ID and name
        Id = enrollment_entry.get()
        name = name_entry.get()
        
        # Validate fields
        if not Id or Id == "Enter enrollment number":
            show_popup(root, "Error", "Please enter enrollment number", "error")
            text_to_speech("Please enter enrollment number")
            return
        
        if not name or name == "Enter student name":
            show_popup(root, "Error", "Please enter student name", "error")
            text_to_speech("Please enter student name")
            return
        
        # Check if ID already exists
        try:
            csv_file = open(studentdetail_path, "r")
            reader = csv.reader(csv_file)
            for row in reader:
                if row and row[0] == Id:
                    show_popup(root, "Error", f"Enrollment ID {Id} already exists", "error")
                    text_to_speech(f"Enrollment ID {Id} already exists")
                    csv_file.close()
                    return
            csv_file.close()
        except:
            pass
        
        # Update status
        status_label.config(text="Initializing camera... Please look at the camera and wait for captures to complete.", fg=TEXT_WHITE)
        root.update()
        
        try:
            # Check for haarcascade file
            if not check_haarcascade_file():
                show_popup(root, "Error", "Haarcascade file not found", "error")
                return
            
            # Initialize camera
            cam = cv2.VideoCapture(0)
            detector = cv2.CascadeClassifier(haarcasecade_path)
            
            # Create directory for student if it doesn't exist
            student_path = os.path.join(trainimage_path, name)
            if not os.path.exists(student_path):
                os.makedirs(student_path)
            
            # Counter for number of images
            img_counter = 0
            
            # Capture images
            while True:
                ret, img = cam.read()
                if not ret:
                    show_popup(root, "Error", "Camera not accessible", "error")
                    break
                
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = detector.detectMultiScale(gray, 1.3, 5)
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    
                    # Increment counter
                    img_counter += 1
                    
                    # Save the captured face
                    file_name = f"{student_path}/{name}_{Id}_{img_counter}.jpg"
                    cv2.imwrite(file_name, gray[y : y + h, x : x + w])
                    
                    # Update counter display
                    counter_label.config(text=f"Images: {img_counter}/50")
                    root.update()
                
                cv2.imshow("Taking Images", img)
                
                # Wait for 200 milliseconds
                if cv2.waitKey(100) & 0xFF == ord("q"):
                    break
                
                # If image count reaches 50, stop capturing
                if img_counter >= 50:
                    status_label.config(text="Image capture complete. You can now train the model.", fg=GREEN)
                    text_to_speech("Image capture complete. You can now train the model.")
                    break
            
            # Release resources
            cam.release()
            cv2.destroyAllWindows()
            
            # Save student details to CSV - Fix file format issues
            try:
                # Check if the directory exists, create if not
                if not os.path.exists(os.path.dirname(studentdetail_path)):
                    os.makedirs(os.path.dirname(studentdetail_path))
                
                # Check if file exists and has proper headers
                file_exists = os.path.isfile(studentdetail_path)
                if file_exists:
                    with open(studentdetail_path, 'r', newline='') as csvFile:
                        reader = csv.reader(csvFile)
                        first_row = next(reader, None)
                        
                        # If file exists but has wrong headers, recreate it
                        if not first_row or len(first_row) < 2 or "Enrollment" not in first_row[0]:
                            # Create backup
                            if os.path.getsize(studentdetail_path) > 0:
                                import shutil
                                backup_path = studentdetail_path + ".bak"
                                shutil.copy2(studentdetail_path, backup_path)
                            
                            # Create new file with correct headers
                            with open(studentdetail_path, 'w', newline='') as csvFile:
                                writer = csv.writer(csvFile)
                                writer.writerow(["Enrollment", "Name"])
                else:
                    # Create new file with headers
                    with open(studentdetail_path, 'w', newline='') as csvFile:
                        writer = csv.writer(csvFile)
                        writer.writerow(["Enrollment", "Name"])
                
                # Now append the new student
                with open(studentdetail_path, "a", newline="") as csvFile:
                    writer = csv.writer(csvFile)
                    writer.writerow([Id, name])
            except Exception as e:
                print(f"Error saving student details: {e}")
                # Try direct write as a fallback
                try:
                    with open(studentdetail_path, "w", newline="") as csvFile:
                        writer = csv.writer(csvFile)
                        writer.writerow(["Enrollment", "Name"])
                        writer.writerow([Id, name])
                except Exception as inner_e:
                    print(f"Final error saving student details: {inner_e}")
            
            # Show success message if images were captured
            if img_counter > 0:
                status_label.config(text=f"Images captured successfully. {img_counter} images stored for {name}.", fg=GREEN)
                text_to_speech(f"Images captured successfully. {img_counter} images stored for {name}.")
            else:
                status_label.config(text="No faces detected. Please try again.", fg=RED)
                text_to_speech("No faces detected. Please try again.")
                
        except Exception as e:
            print(f"Error: {e}")
            status_label.config(text=f"Error: {str(e)}", fg=RED)
            text_to_speech("An error occurred while capturing images.")
    
    def train_model():
        """Train the model with captured images"""
        # Check if there are images to train
        if not os.path.exists(trainimage_path) or len(os.listdir(trainimage_path)) == 0:
            show_popup(root, "Error", "No training images found. Please capture images first.", "error")
            text_to_speech("No training images found. Please capture images first.")
            return
        
        # Update status
        status_label.config(text="Training model... Please wait, this may take a few minutes.", fg=TEXT_WHITE)
        root.update()
        
        try:
            # Get all training image paths and IDs
            faces = []
            ids = []
            
            # Navigate through all folders in training path
            for root_dir, dirs, files in os.walk(trainimage_path):
                for file in files:
                    if file.endswith((".jpg", ".jpeg", ".png")):
                        # Get ID from file name
                        try:
                            id = int(file.split("_")[1])
                            img_path = os.path.join(root_dir, file)
                            
                            # Read and convert image
                            img = cv2.imread(img_path)
                            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                            
                            # Detect face in image
                            detector = cv2.CascadeClassifier(haarcasecade_path)
                            face = detector.detectMultiScale(gray, 1.3, 5)
                            
                            # If face detected, add to training data
                            for (x, y, w, h) in face:
                                faces.append(gray[y : y + h, x : x + w])
                                ids.append(id)
                        except Exception as e:
                            print(f"Error processing {file}: {e}")
                            continue
            
            # Train LBPH Face Recognizer
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            
            # Check if there are enough faces to train
            if len(faces) < 5:
                show_popup(root, "Error", "Not enough faces detected in training images. Please capture more images.", "error")
                text_to_speech("Not enough faces detected in training images. Please capture more images.")
                return
            
            # Train the model
            recognizer.train(faces, np.array(ids))
            
            # Save the model
            recognizer.save(trainimagelabel_path)
            
            # Show success message
            status_label.config(text="Model trained successfully! The system is now ready to recognize students.", fg=GREEN)
            show_popup(root, "Success", "Model trained successfully! The system is now ready to recognize students.", "info")
            text_to_speech("Model trained successfully! The system is now ready to recognize students.")
            
        except Exception as e:
            print(f"Error: {e}")
            status_label.config(text=f"Error: {str(e)}", fg=RED)
            text_to_speech("An error occurred while training the model.")
    
    # Buttons
    button_frame = tk.Frame(form_card, bg=MEDIUM_BG)
    button_frame.pack(fill=X, pady=(30, 0))
    
    # Take images button
    take_btn = create_button(
        button_frame, 
        "Take Images", 
        take_images,
        bg=PRIMARY,
        width=14,
        height=2
    )
    take_btn.pack(side=LEFT, padx=(0, 10))
    
    # Train model button
    train_btn = create_button(
        button_frame, 
        "Train Model", 
        train_model,
        bg=GREEN,
        width=14,
        height=2
    )
    train_btn.pack(side=LEFT, padx=10)
    
    # Clear button
    clear_btn = create_button(
        button_frame, 
        "Clear", 
        clear_fields,
        bg=RED,
        width=10,
        height=2
    )
    clear_btn.pack(side=RIGHT)
    
    # Right column - Instructions & Info
    right_column = tk.Frame(content, bg=DARK_BG)
    right_column.pack(side=RIGHT, fill=BOTH, expand=True, padx=(20, 0))
    
    instruction_card = tk.Frame(right_column, bg=MEDIUM_BG, padx=40, pady=40)
    instruction_card.pack(fill=BOTH, expand=True)
    
    instruction_title = tk.Label(
        instruction_card, 
        text="Registration Process", 
        font=("Segoe UI", 20, "bold"),
        bg=MEDIUM_BG,
        fg=TEXT_WHITE
    )
    instruction_title.pack(anchor=W, pady=(0, 20))
    
    instructions = [
        "1. Enter Enrollment number and name",
        "2. Click 'Take Images' to start the camera",
        "3. Look directly at the camera",
        "4. The system will capture 50 images of your face",
        "5. Wait for the capture process to complete",
        "6. Click 'Train Model' to train the system",
        "7. Once trained, the system can recognize you"
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
        img = Image.open("UI_Image/face-scan.png")
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

def launch_take_attendance():
    """Launch the take attendance module"""
    # Import module at runtime to avoid circular imports
    import new_automaticAttedance as attendance
    attendance.subjectChoose(text_to_speech)

def launch_view_attendance():
    """Launch the view attendance module"""
    # Import module at runtime to avoid circular imports
    import new_show_attendance as show_attendance
    show_attendance.subjectchoose()

def main_screen():
    """Main application screen"""
    root = Tk()
    root.title("Smart Attendance System")
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
    
    # Check and create required directories
    check_directories()
    
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
        text="SMART ATTENDANCE SYSTEM", 
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
    
    # Banner section
    banner_frame = tk.Frame(scrollable_frame, bg=MEDIUM_BG, padx=20, pady=20)
    banner_frame.pack(fill=X, pady=(20, 0), padx=20)
    
    # Banner content
    banner_text_frame = tk.Frame(banner_frame, bg=MEDIUM_BG)
    banner_text_frame.pack(side=LEFT, fill=BOTH, expand=True)
    
    welcome_label = tk.Label(
        banner_text_frame,
        text="Welcome to Smart Attendance System",
        font=("Segoe UI", 24, "bold"),
        bg=MEDIUM_BG,
        fg=TEXT_WHITE,
        justify=LEFT
    )
    welcome_label.pack(anchor=W)
    
    description_label = tk.Label(
        banner_text_frame,
        text="Modernized Facial Recognition Attendance Solution",
        font=("Segoe UI", 14),
        bg=MEDIUM_BG,
        fg=TEXT_LIGHT,
        justify=LEFT
    )
    description_label.pack(anchor=W, pady=(10, 20))
    
    # Add banner image
    try:
        img_frame = tk.Frame(banner_frame, bg=MEDIUM_BG)
        img_frame.pack(side=RIGHT, padx=(30, 0))
        
        img = Image.open("UI_Image/banner.png")
        img = img.resize((200, 133), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        img_label = tk.Label(img_frame, image=photo, bg=MEDIUM_BG)
        img_label.image = photo
        img_label.pack()
    except Exception as e:
        print(f"Could not load banner image: {e}")
    
    # Main content - Feature cards in responsive grid
    content_frame = tk.Frame(scrollable_frame, bg=DARK_BG, padx=20, pady=20)
    content_frame.pack(fill=BOTH, expand=True, padx=20)
    
    # Use grid layout for better responsiveness
    content_frame.columnconfigure(0, weight=1)
    content_frame.columnconfigure(1, weight=1)
    content_frame.columnconfigure(2, weight=1)
    content_frame.rowconfigure(0, weight=1)
    
    # 1. Register & Train
    register_card = tk.Frame(content_frame, bg=MEDIUM_BG, padx=20, pady=20)
    register_card.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    
    register_title = tk.Label(
        register_card,
        text="Register & Train",
        font=("Segoe UI", 18, "bold"),
        bg=MEDIUM_BG,
        fg=TEXT_WHITE
    )
    register_title.pack(anchor=W, pady=(0, 10))
    
    register_desc = tk.Label(
        register_card,
        text="Register new students and train the facial recognition model.",
        font=("Segoe UI", 11),
        bg=MEDIUM_BG,
        fg=TEXT_LIGHT,
        wraplength=250,
        justify=LEFT
    )
    register_desc.pack(anchor=W, pady=(0, 15), fill=X)
    
    # Add icon
    try:
        register_img = Image.open("UI_Image/register.png")
        register_img = register_img.resize((60, 60), Image.LANCZOS)
        register_photo = ImageTk.PhotoImage(register_img)
        register_img_label = tk.Label(register_card, image=register_photo, bg=MEDIUM_BG)
        register_img_label.image = register_photo
        register_img_label.pack(pady=10)
    except Exception as e:
        print(f"Could not load register image: {e}")
    
    register_btn = create_button(
        register_card,
        "Register Students",
        register_student_screen,
        width=18,
        height=2
    )
    register_btn.pack(pady=(10, 0))
    
    # 2. Take Attendance
    attendance_card = tk.Frame(content_frame, bg=MEDIUM_BG, padx=20, pady=20)
    attendance_card.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    
    attendance_title = tk.Label(
        attendance_card,
        text="Take Attendance",
        font=("Segoe UI", 18, "bold"),
        bg=MEDIUM_BG,
        fg=TEXT_WHITE
    )
    attendance_title.pack(anchor=W, pady=(0, 10))
    
    attendance_desc = tk.Label(
        attendance_card,
        text="Use facial recognition to automatically mark attendance.",
        font=("Segoe UI", 11),
        bg=MEDIUM_BG,
        fg=TEXT_LIGHT,
        wraplength=250,
        justify=LEFT
    )
    attendance_desc.pack(anchor=W, pady=(0, 15), fill=X)
    
    # Add icon
    try:
        attendance_img = Image.open("UI_Image/attendance.png")
        attendance_img = attendance_img.resize((60, 60), Image.LANCZOS)
        attendance_photo = ImageTk.PhotoImage(attendance_img)
        attendance_img_label = tk.Label(attendance_card, image=attendance_photo, bg=MEDIUM_BG)
        attendance_img_label.image = attendance_photo
        attendance_img_label.pack(pady=10)
    except Exception as e:
        print(f"Could not load attendance image: {e}")
    
    attendance_btn = create_button(
        attendance_card,
        "Take Attendance",
        launch_take_attendance,
        bg=GREEN,
        width=18,
        height=2
    )
    attendance_btn.pack(pady=(10, 0))
    
    # 3. View Reports
    reports_card = tk.Frame(content_frame, bg=MEDIUM_BG, padx=20, pady=20)
    reports_card.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
    
    reports_title = tk.Label(
        reports_card,
        text="View Reports",
        font=("Segoe UI", 18, "bold"),
        bg=MEDIUM_BG,
        fg=TEXT_WHITE
    )
    reports_title.pack(anchor=W, pady=(0, 10))
    
    reports_desc = tk.Label(
        reports_card,
        text="View and analyze attendance reports and monitor patterns.",
        font=("Segoe UI", 11),
        bg=MEDIUM_BG,
        fg=TEXT_LIGHT,
        wraplength=250,
        justify=LEFT
    )
    reports_desc.pack(anchor=W, pady=(0, 15), fill=X)
    
    # Add icon
    try:
        reports_img = Image.open("UI_Image/reports.png")
        reports_img = reports_img.resize((60, 60), Image.LANCZOS)
        reports_photo = ImageTk.PhotoImage(reports_img)
        reports_img_label = tk.Label(reports_card, image=reports_photo, bg=MEDIUM_BG)
        reports_img_label.image = reports_photo
        reports_img_label.pack(pady=10)
    except Exception as e:
        print(f"Could not load reports image: {e}")
    
    reports_btn = create_button(
        reports_card,
        "View Reports",
        launch_view_attendance,
        bg=SECONDARY,
        width=18,
        height=2
    )
    reports_btn.pack(pady=(10, 0))
    
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
    
    # Start text-to-speech welcome
    text_to_speech("Welcome to Smart Attendance System")
    
    root.mainloop()

# Create UI_Image directory if it doesn't exist
if not os.path.exists("UI_Image"):
    os.makedirs("UI_Image")

if __name__ == "__main__":
    main_screen() 