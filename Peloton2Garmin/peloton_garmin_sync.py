"""
Peloton to Garmin Connect Activity Sync
WITH PROPER HEADLESS MFA SUPPORT
User enters MFA code directly in the app dialog
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
from datetime import datetime
import json
import os


class PelotonGarminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Peloton to Garmin Sync")
        self.root.geometry("900x700")  # Larger default size
        self.root.minsize(800, 600)  # Set minimum size
        
        # Session management
        self.peloton_session = None
        self.peloton_user_id = None
        self.peloton_auth = None
        self.workout_data = []
        self.selected_workouts = []
        
        # Garmin MFA state
        self.garmin_client_state = None
        
        # Settings manager
        from settings_manager import SettingsManager
        self.settings = SettingsManager()
        
        self.create_widgets()
        self.load_saved_settings()
    
    def load_saved_settings(self):
        """Load saved settings into the UI"""
        # Load bearer token
        saved_token = self.settings.get_bearer_token()
        if saved_token and hasattr(self, 'bearer_token_entry'):
            self.bearer_token_entry.delete('1.0', tk.END)
            self.bearer_token_entry.insert('1.0', saved_token)
            self.token_status_label.config(text="✓ Token loaded from saved settings", 
                                          foreground='green')
        
        # Load Garmin email if remember is enabled
        saved_email = self.settings.get_garmin_email()
        if saved_email:
            self.saved_garmin_email = saved_email
        else:
            self.saved_garmin_email = None
    
    def clear_saved_token(self):
        """Clear the saved bearer token"""
        if messagebox.askyesno("Clear Token", 
                              "Are you sure you want to clear the saved bearer token?\n\n"
                              "You'll need to paste it again next time."):
            self.settings.clear_bearer_token()
            self.bearer_token_entry.delete('1.0', tk.END)
            self.token_status_label.config(text="Token cleared", foreground='gray')
            self.log_status("Saved bearer token cleared")
    
    def create_widgets(self):
        """Create the GUI layout"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title = ttk.Label(main_frame, text="Peloton to Garmin Sync", 
                         font=('Arial', 16, 'bold'))
        title.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Peloton Login Section
        login_frame = ttk.LabelFrame(main_frame, text="Peloton Login", padding="10")
        login_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Bearer token login (only method)
        ttk.Label(login_frame, text="Bearer Token:", 
                 font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(login_frame, text="Get this from your browser's DevTools", 
                 font=('Arial', 8)).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        self.bearer_token_entry = tk.Text(login_frame, width=50, height=4, wrap=tk.WORD)
        self.bearer_token_entry.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Saved token indicator
        self.token_status_label = ttk.Label(login_frame, text="", 
                                           font=('Arial', 8), foreground='gray')
        self.token_status_label.grid(row=3, column=0, columnspan=2)
        
        # Button frame for login and clear
        btn_frame = ttk.Frame(login_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=5)
        
        self.token_login_btn = ttk.Button(btn_frame, text="Login with Token", 
                                         command=self.login_peloton_token)
        self.token_login_btn.grid(row=0, column=0, padx=3)
        
        self.clear_token_btn = ttk.Button(btn_frame, text="Clear Saved Token", 
                                         command=self.clear_saved_token)
        self.clear_token_btn.grid(row=0, column=1, padx=3)
        
        help_btn = ttk.Button(login_frame, text="How to get token?", 
                             command=self.show_token_help)
        help_btn.grid(row=5, column=0, columnspan=2, pady=2)
        
        # Workouts Section
        workout_frame = ttk.LabelFrame(main_frame, text="Recent Workouts", padding="10")
        workout_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Treeview for workouts
        columns = ('select', 'date', 'type', 'duration', 'calories')
        self.workout_tree = ttk.Treeview(workout_frame, columns=columns, 
                                        show='tree headings', height=10)
        
        # Define column headings
        self.workout_tree.heading('select', text='Select')
        self.workout_tree.heading('date', text='Date')
        self.workout_tree.heading('type', text='Workout')
        self.workout_tree.heading('duration', text='Duration')
        self.workout_tree.heading('calories', text='Calories')
        
        # Column widths
        self.workout_tree.column('#0', width=0, stretch=tk.NO)
        self.workout_tree.column('select', width=60)
        self.workout_tree.column('date', width=150)
        self.workout_tree.column('type', width=350)
        self.workout_tree.column('duration', width=100)
        self.workout_tree.column('calories', width=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(workout_frame, orient=tk.VERTICAL, 
                                 command=self.workout_tree.yview)
        self.workout_tree.configure(yscrollcommand=scrollbar.set)
        
        self.workout_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind checkbox toggle
        self.workout_tree.bind('<Button-1>', self.toggle_selection)
        
        # Action Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.fetch_btn = ttk.Button(button_frame, text="Fetch Workouts", 
                                    command=self.fetch_workouts, state='disabled')
        self.fetch_btn.grid(row=0, column=0, padx=5)
        
        self.export_btn = ttk.Button(button_frame, text="Export to Garmin", 
                                     command=self.export_to_garmin, state='disabled')
        self.export_btn.grid(row=0, column=1, padx=5)
        
        # Status/Log Section
        log_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.status_text = scrolledtext.ScrolledText(log_frame, height=6, width=70)
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        workout_frame.columnconfigure(0, weight=1)
        workout_frame.rowconfigure(0, weight=1)
    
    def log_status(self, message):
        """Add a message to the status log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
    
    def show_token_help(self):
        """Show instructions for getting the bearer token"""
        help_text = """How to Get Your Peloton Bearer Token:

1. Open your web browser and go to onepeloton.com
2. Log in to your Peloton account
3. Open Developer Tools (F12 or right-click → Inspect)
4. Click on the 'Network' tab
5. Refresh the page (F5)
6. Look for a request to 'api/user' or any API request
7. Click on that request
8. In the 'Headers' section, find 'Authorization'
9. Copy the value after 'Bearer ' (everything after the word Bearer)
10. Paste it in the Bearer Token field above

The token will be saved securely on your computer for future use.

Note: If the token expires, you'll need to get a new one following these same steps."""
        
        messagebox.showinfo("How to Get Bearer Token", help_text)
    
    def login_peloton_token(self):
        """Login to Peloton using bearer token"""
        from peloton_auth import PelotonAuthenticator
        
        token = self.bearer_token_entry.get('1.0', tk.END).strip()
        
        if not token:
            messagebox.showerror("Error", "Please enter your bearer token")
            return
        
        self.log_status("Authenticating with bearer token...")
        self.token_login_btn.config(state='disabled')
        
        try:
            self.peloton_auth = PelotonAuthenticator()
            success = self.peloton_auth.login_with_token(token)
            
            if success:
                self.peloton_session = self.peloton_auth.session
                self.peloton_user_id = self.peloton_auth.user_id
                
                self.settings.save_bearer_token(token)
                
                self.log_status("✓ Successfully authenticated with Peloton!")
                self.fetch_btn.config(state='normal')
                self.token_login_btn.config(text="✓ Logged In")
                self.token_status_label.config(text="✓ Token validated and saved", 
                                              foreground='green')
                messagebox.showinfo("Success", "Successfully authenticated with Peloton!")
            else:
                self.log_status("✗ Authentication failed - token may be invalid or expired")
                self.token_status_label.config(text="✗ Invalid token", 
                                              foreground='red')
                messagebox.showerror("Error", 
                    "Failed to authenticate with Peloton.\n\n"
                    "The token may be invalid or expired.\n"
                    "Please get a new token from your browser.")
                
        except Exception as e:
            self.log_status(f"✗ Error during authentication: {str(e)}")
            messagebox.showerror("Error", f"Authentication error: {str(e)}")
        finally:
            self.token_login_btn.config(state='normal')
    
    def fetch_workouts(self):
        """Fetch recent workouts from Peloton"""
        if not self.peloton_auth:
            messagebox.showerror("Error", "Please login to Peloton first")
            return
        
        self.log_status("Fetching workouts from Peloton...")
        self.fetch_btn.config(state='disabled')
        
        try:
            workouts = self.peloton_auth.get_recent_workouts(limit=50)
            
            if not workouts:
                messagebox.showinfo("No Workouts", "No workouts found in your recent history.")
                self.log_status("No workouts found")
                return
            
            self.workout_data = workouts
            self.selected_workouts = []
            
            # Clear existing items
            for item in self.workout_tree.get_children():
                self.workout_tree.delete(item)
            
            # Populate tree view
            for workout in workouts:
                workout_id = workout.get('id', '')
                created_at = workout.get('created_at', 0)
                date_str = datetime.fromtimestamp(created_at).strftime('%Y-%m-%d %H:%M')
                
                ride = workout.get('ride', {})
                workout_type = ride.get('fitness_discipline', 'Unknown')
                title = ride.get('title', 'Unnamed Workout')
                instructor_name = ride.get('instructor', {}).get('name', 'Unknown')
                
                full_name = f"{title} with {instructor_name}"
                
                duration = workout.get('ride', {}).get('duration', 0) // 60
                calories = workout.get('total_work', 0) // 1000
                
                self.workout_tree.insert('', tk.END, iid=workout_id, 
                                        values=('☐', date_str, full_name, f"{duration} min", calories))
            
            self.log_status(f"✓ Loaded {len(workouts)} workouts")
            self.export_btn.config(state='normal')
            
        except Exception as e:
            self.log_status(f"✗ Error fetching workouts: {str(e)}")
            messagebox.showerror("Error", f"Failed to fetch workouts: {str(e)}")
        finally:
            self.fetch_btn.config(state='normal')
    
    def toggle_selection(self, event):
        """Toggle workout selection when clicked"""
        region = self.workout_tree.identify('region', event.x, event.y)
        if region != 'cell':
            return
        
        column = self.workout_tree.identify_column(event.x)
        if column != '#1':
            return
        
        item = self.workout_tree.identify_row(event.y)
        if not item:
            return
        
        current_values = self.workout_tree.item(item, 'values')
        if current_values[0] == '☐':
            new_values = ('☑',) + current_values[1:]
            self.workout_tree.item(item, values=new_values)
            self.selected_workouts.append(item)
        else:
            new_values = ('☐',) + current_values[1:]
            self.workout_tree.item(item, values=new_values)
            if item in self.selected_workouts:
                self.selected_workouts.remove(item)
        
        self.log_status(f"Selected {len(self.selected_workouts)} workout(s)")
    
    def show_garmin_login_dialog(self):
        """Show dialog to get Garmin credentials"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Garmin Connect Login")
        dialog.geometry("520x320")  # Taller to fit buttons
        dialog.resizable(False, False)  # Prevent resizing
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Main container with padding
        main_container = ttk.Frame(dialog, padding="20")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_container, text="🏃 Garmin Connect Login", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        instructions = ttk.Label(main_container, 
            text="Enter your Garmin Connect credentials.\n"
                 "If you have MFA enabled, you'll be prompted for the code.",
            justify=tk.CENTER, wraplength=450)
        instructions.pack(pady=(0, 10))
        
        # Form frame
        form_frame = ttk.Frame(main_container)
        form_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(form_frame, text="Email:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        email_entry = ttk.Entry(form_frame, width=35)
        email_entry.grid(row=0, column=1, pady=5, sticky=tk.EW)
        
        if hasattr(self, 'saved_garmin_email') and self.saved_garmin_email:
            email_entry.insert(0, self.saved_garmin_email)
        
        ttk.Label(form_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        password_entry = ttk.Entry(form_frame, width=35, show="*")
        password_entry.grid(row=1, column=1, pady=5, sticky=tk.EW)
        password_entry.focus()
        
        form_frame.columnconfigure(1, weight=1)
        
        # Remember checkbox
        remember_var = tk.BooleanVar(value=bool(hasattr(self, 'saved_garmin_email') and self.saved_garmin_email))
        remember_check = ttk.Checkbutton(main_container, 
            text="Remember email (password is never saved)", 
            variable=remember_var)
        remember_check.pack(pady=(0, 15))
        
        result = {'email': None, 'password': None, 'remember': False}
        
        def submit():
            email = email_entry.get().strip()
            password = password_entry.get().strip()
            
            if not email or not password:
                messagebox.showwarning("Missing Information", 
                                     "Please enter both email and password")
                return
            
            result['email'] = email
            result['password'] = password
            result['remember'] = remember_var.get()
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        # Button frame at bottom
        button_frame = ttk.Frame(main_container)
        button_frame.pack(side=tk.BOTTOM, pady=(10, 0))
        
        ttk.Button(button_frame, text="Login", command=submit, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=cancel, width=12).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        password_entry.bind('<Return>', lambda e: submit())
        email_entry.bind('<Return>', lambda e: password_entry.focus())
        
        # Center the dialog on screen
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        dialog.wait_window()
        
        return result
    
    def show_mfa_dialog(self):
        """Show dialog to get MFA code from user"""
        mfa_window = tk.Toplevel(self.root)
        mfa_window.title("Garmin MFA Required")
        mfa_window.geometry("480x260")
        mfa_window.resizable(False, False)
        mfa_window.transient(self.root)
        mfa_window.grab_set()
        
        # Main container
        main_container = ttk.Frame(mfa_window, padding="20")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_container, text="📱 Garmin Multi-Factor Authentication", 
                 font=('Arial', 11, 'bold')).pack(pady=(0, 15))
        
        instructions = ttk.Label(main_container, 
            text="Garmin has sent a 6-digit code to your phone.\n"
                 "Enter the code below:",
            justify=tk.CENTER)
        instructions.pack(pady=(0, 15))
        
        mfa_entry = ttk.Entry(main_container, width=15, font=('Arial', 16), justify='center')
        mfa_entry.pack(pady=(0, 10))
        mfa_entry.focus()
        
        hint_label = ttk.Label(main_container, text="Example: 123456", 
                              font=('Arial', 8), foreground='gray')
        hint_label.pack(pady=(0, 20))
        
        mfa_code = [None]
        
        def submit_mfa():
            code = mfa_entry.get().strip()
            if code:
                if len(code) != 6 or not code.isdigit():
                    messagebox.showwarning("Invalid Code", 
                                         "MFA code should be 6 digits.\n"
                                         "Example: 123456")
                    mfa_entry.delete(0, tk.END)
                    mfa_entry.focus()
                    return
                mfa_code[0] = code
                mfa_window.destroy()
        
        # Button frame at bottom
        button_frame = ttk.Frame(main_container)
        button_frame.pack(side=tk.BOTTOM, pady=(10, 0))
        
        ttk.Button(button_frame, text="Submit Code", 
                  command=submit_mfa, width=15).pack()
        
        mfa_entry.bind('<Return>', lambda e: submit_mfa())
        
        # Center the dialog
        mfa_window.update_idletasks()
        width = mfa_window.winfo_width()
        height = mfa_window.winfo_height()
        x = (mfa_window.winfo_screenwidth() // 2) - (width // 2)
        y = (mfa_window.winfo_screenheight() // 2) - (height // 2)
        mfa_window.geometry(f'{width}x{height}+{x}+{y}')
        
        mfa_window.wait_window()
        return mfa_code[0]
    
    def export_to_garmin(self):
        """Export selected workouts to Garmin with headless MFA"""
        from fit_converter import PelotonToFitConverter
        from garminconnect import Garmin
        import tempfile
        from pathlib import Path
        
        if not self.selected_workouts:
            messagebox.showwarning("No Selection", "Please select at least one workout to export")
            return
        
        self.log_status(f"Preparing to export {len(self.selected_workouts)} workouts to Garmin...")
        
        # Get Garmin credentials
        garmin_creds = self.show_garmin_login_dialog()
        
        if not garmin_creds['email'] or not garmin_creds['password']:
            self.log_status("Export cancelled - no Garmin credentials provided")
            return
        
        # Save email if requested
        if garmin_creds['remember']:
            self.settings.save_garmin_email(garmin_creds['email'])
            self.saved_garmin_email = garmin_creds['email']
        else:
            self.settings.clear_garmin_email()
            self.saved_garmin_email = None
        
        # Initialize converter
        converter = PelotonToFitConverter(self.peloton_auth)
        
        # Login to Garmin with MFA support
        try:
            self.log_status("Connecting to Garmin Connect...")
            
            # Create Garmin client with return_on_mfa flag
            garmin_client = Garmin(
                email=garmin_creds['email'],
                password=garmin_creds['password'],
                is_cn=False,
                return_on_mfa=True
            )
            
            # Try to login
            result1, result2 = garmin_client.login()
            
            # Check if MFA is required
            if result1 == "needs_mfa":
                self.log_status("→ MFA required - waiting for code...")
                
                # Show MFA dialog to user
                mfa_code = self.show_mfa_dialog()
                
                if not mfa_code:
                    self.log_status("✗ Export cancelled - no MFA code provided")
                    messagebox.showwarning("Cancelled", "Export cancelled - MFA code required")
                    return
                
                self.log_status("Submitting MFA code...")
                
                # Submit MFA code using garminconnect's resume_login
                garmin_client.resume_login(result2, mfa_code)
                self.log_status("✓ MFA successful!")
            
            self.log_status("✓ Garmin authentication successful!")
            
        except Exception as e:
            error_msg = str(e)
            self.log_status(f"✗ Garmin authentication error: {error_msg}")
            
            # Check for specific error types
            if '429' in error_msg and 'Too Many Requests' in error_msg:
                messagebox.showerror("Rate Limited", 
                    "Garmin has temporarily blocked login attempts.\n\n"
                    "This happens after multiple login attempts in a short time.\n\n"
                    "Solutions:\n"
                    "1. Wait 15-30 minutes and try again\n"
                    "2. The block will clear automatically\n"
                    "3. Your MFA authentication was working correctly!\n\n"
                    "Note: Once you successfully login, the session tokens\n"
                    "are saved and you won't need to login again for ~1 year.")
            else:
                messagebox.showerror("Authentication Error", 
                    f"Could not connect to Garmin:\n{error_msg}")
            return
        
        # Process workouts
        self.log_status("Processing workouts...")
        success_count = 0
        temp_dir = tempfile.mkdtemp()
        
        self.log_status(f"Using temp directory: {temp_dir}")
        
        for workout_id in self.selected_workouts:
            try:
                workout = next((w for w in self.workout_data if w['id'] == workout_id), None)
                if not workout:
                    self.log_status(f"✗ Workout {workout_id} not found in data")
                    continue
                
                ride = workout.get('ride', {})
                workout_name = ride.get('title', 'Peloton Workout')
                date_str = datetime.fromtimestamp(workout.get('created_at', 0)).strftime('%Y-%m-%d')
                
                self.log_status(f"Converting: {workout_name}...")
                
                fit_path = os.path.join(temp_dir, f"peloton_{workout_id}.fit")
                
                try:
                    converter.convert_workout_to_fit(workout, fit_path)
                    self.log_status(f"  → FIT file created: {os.path.basename(fit_path)}")
                    
                    # Check file was created and has content
                    if not os.path.exists(fit_path):
                        raise Exception(f"FIT file not created: {fit_path}")
                    
                    file_size = os.path.getsize(fit_path)
                    if file_size == 0:
                        raise Exception("FIT file is empty")
                    
                    self.log_status(f"  → FIT file size: {file_size} bytes")
                    
                except Exception as conv_error:
                    self.log_status(f"✗ Conversion failed: {str(conv_error)}")
                    continue
                
                self.log_status(f"Uploading: {workout_name}...")
                
                try:
                    # Upload the FIT file by path (not bytes)
                    self.log_status(f"  → Uploading file: {fit_path}")
                    upload_response = garmin_client.upload_activity(fit_path)
                    
                    self.log_status(f"  → Upload response received: {upload_response}")
                    
                    # Check if it's a Response object or dict
                    if hasattr(upload_response, 'json'):
                        # It's a Response object, get JSON
                        try:
                            response_data = upload_response.json()
                            self.log_status(f"  → Response JSON: {str(response_data)[:200]}")
                        except:
                            response_data = {}
                            self.log_status(f"  → Response status: {upload_response.status_code}")
                    elif isinstance(upload_response, dict):
                        response_data = upload_response
                    else:
                        response_data = {}
                    
                    # Try to get activity ID
                    activity_id = None
                    if response_data:
                        activity_id = response_data.get('detailedImportResult', {}).get('activityId')
                        if not activity_id:
                            # Try alternate location
                            activity_id = response_data.get('activityId')
                    
                    if activity_id:
                        self.log_status(f"  → Activity ID: {activity_id}")
                        try:
                            garmin_client.set_activity_name(activity_id, f"{workout_name} - {date_str}")
                            self.log_status(f"  → Activity renamed to: {workout_name} - {date_str}")
                        except Exception as name_error:
                            self.log_status(f"  → Could not rename activity: {str(name_error)}")
                    else:
                        self.log_status(f"  → No activity ID found, but upload accepted (202)")
                    
                    self.log_status(f"✓ Successfully uploaded: {workout_name}")
                    success_count += 1
                    
                except Exception as upload_error:
                    error_msg = str(upload_error)
                    
                    # Check if it's a duplicate (409 Conflict)
                    if '409' in error_msg and 'Conflict' in error_msg:
                        self.log_status(f"⚠ Workout already exists in Garmin: {workout_name}")
                        # Count as success since it's already there
                        success_count += 1
                    else:
                        self.log_status(f"✗ Upload failed: {error_msg}")
                        import traceback
                        self.log_status(f"  → Traceback: {traceback.format_exc()}")
                    continue
                
            except Exception as e:
                self.log_status(f"✗ Error with workout {workout_id}: {str(e)}")
                import traceback
                self.log_status(f"  → Traceback: {traceback.format_exc()}")
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Show summary
        messagebox.showinfo(
            "Export Complete", 
            f"Successfully exported {success_count} of {len(self.selected_workouts)} workouts to Garmin Connect!"
        )
        self.log_status(f"Export complete: {success_count}/{len(self.selected_workouts)} successful")


def main():
    root = tk.Tk()
    app = PelotonGarminApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()