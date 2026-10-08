import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from PIL import Image, ImageTk
import os
from complex_queries import ComplexQueries, get_all_complex_queries
try:
    from enhanced_reports import EnhancedReportGenerator
except ImportError:
    pass

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class ModernCarbonTracker:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🌱 Modern Carbon Footprint Tracker")
        self.root.geometry("1400x900")
        
        # Database connection
        self.conn = sqlite3.connect('carbon_tracker.db')
        self.cursor = self.conn.cursor()
        
        # Navigation history
        self.page_history = []
    
        # Bind cleanup on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Show home page by default
        self.show_home_page()
    
    def create_background(self):
        """Create background image for home page"""
        try:
            # Check if background image exists
            bg_path = os.path.join("static", "background.jpg")
            if not os.path.exists(bg_path):
                # Create a default gradient background if no image exists
                self.create_default_background()
                return
            
            # Load and resize background image
            bg_image = Image.open(bg_path)
            
            # Get container size
            self.main_container.update_idletasks()
            width = self.main_container.winfo_width() or 1380
            height = self.main_container.winfo_height() or 880
            
            # Resize image to fit container
            bg_image = bg_image.resize((width, height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            
            # Create canvas for background
            self.bg_canvas = tk.Canvas(self.main_container, highlightthickness=0)
            self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
            
            # Add background image
            self.bg_canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            
        except Exception as e:
            print(f"Background image error: {e}")
            self.create_default_background()
    
    def create_default_background(self):
        """Create a default gradient background"""
        try:
            # Get container size
            self.main_container.update_idletasks()
            width = self.main_container.winfo_width() or 1380
            height = self.main_container.winfo_height() or 880
            
            # Create gradient image
            gradient = Image.new('RGB', (width, height), color='#1a4d3a')
            
            # Create a simple gradient effect
            for y in range(height):
                # Calculate color based on position
                ratio = y / height
                r = int(26 + (45 - 26) * ratio)  # From dark green to lighter green
                g = int(77 + (120 - 77) * ratio)
                b = int(58 + (85 - 58) * ratio)
                
                # Draw horizontal line with calculated color
                for x in range(width):
                    gradient.putpixel((x, y), (r, g, b))
            
            # Convert to PhotoImage
            self.bg_photo = ImageTk.PhotoImage(gradient)
            
            # Create canvas for background
            self.bg_canvas = tk.Canvas(self.main_container, highlightthickness=0)
            self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
            
            # Add background
            self.bg_canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            
        except Exception as e:
            print(f"Default background error: {e}")
    
    def show_home_page(self):
        """Show the home page with title and main buttons"""
        # Clear main container
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Title section
        title_frame = ctk.CTkFrame(self.main_container)
        title_frame.pack(fill="x", padx=50, pady=(50, 30))
        
        # Main title
        main_title = ctk.CTkLabel(title_frame, text="🌱 Carbon Footprint Tracker", 
                                 font=ctk.CTkFont(size=36, weight="bold"))
        main_title.pack(pady=(30, 10))
        
        # Subtitle
        subtitle = ctk.CTkLabel(title_frame, text="Track and Monitor Your Environmental Impact", 
                               font=ctk.CTkFont(size=16))
        subtitle.pack(pady=(0, 30))
        
        # Main buttons section
        buttons_frame = ctk.CTkFrame(self.main_container)
        buttons_frame.pack(expand=True, padx=50, pady=50)
        
        # Center the buttons
        center_frame = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        center_frame.pack(expand=True)
        
        # Button container
        button_container = ctk.CTkFrame(center_frame, fg_color="transparent")
        button_container.pack(expand=True)
        
        # Add Records button
        add_btn = ctk.CTkButton(button_container, text="+ Add Records", 
                               command=self.show_add_entry,
                               font=ctk.CTkFont(size=20, weight="bold"),
                               height=80, width=200)
        add_btn.pack(side="left", padx=20, pady=50)
        
        # View Records button  
        view_btn = ctk.CTkButton(button_container, text="View Records", 
                                command=self.show_records_page,
                                font=ctk.CTkFont(size=20, weight="bold"),
                                height=80, width=200,
                                fg_color="gray", hover_color="darkgray")
        view_btn.pack(side="left", padx=20, pady=50)
    
    def show_add_entry(self):
        """Show add entry page"""
        self.page_history.append('home')
        
        # Clear main container
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Create back button
        back_frame = ctk.CTkFrame(self.main_container)
        back_frame.pack(fill="x", padx=20, pady=(10, 0))
        
        back_btn = ctk.CTkButton(back_frame, text="← Back", 
                                command=self.go_back,
                                height=35, width=150)
        back_btn.pack(side="left", padx=10, pady=10)
        
        self.setup_entry_form()
    
    def setup_entry_form(self):
        """Setup entry tab"""
        entry_frame = self.main_container
        
        # Left frame for inputs
        left_frame = ctk.CTkFrame(entry_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=10)
        
        # Title
        title_label = ctk.CTkLabel(left_frame, text="Add Carbon Activity", 
                                  font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)
        
        # User Information Section
        user_frame = ctk.CTkFrame(left_frame)
        user_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(user_frame, text="User Information", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        # User input fields
        self.user_name = ctk.CTkEntry(user_frame, placeholder_text="Full Name")
        self.user_name.pack(pady=5, padx=20, fill="x")
        
        # Activity Section
        activities_frame = ctk.CTkFrame(left_frame)
        activities_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(activities_frame, text="Activity Details", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        # Activity text input
        self.activity_entry = ctk.CTkEntry(activities_frame, placeholder_text="Activity (e.g., Car Travel, Electricity Usage, Flight)")
        self.activity_entry.pack(pady=5, padx=20, fill="x")
        self.activity_entry.bind("<KeyRelease>", lambda e: self.on_activity_change())
        
        # Unit display (auto-detected)
        self.unit_label = ctk.CTkLabel(activities_frame, text="Unit: Type an activity")
        self.unit_label.pack(pady=5)
        
        # Quantity input with real-time calculation
        self.quantity = ctk.CTkEntry(activities_frame, placeholder_text="Quantity")
        self.quantity.pack(pady=5, padx=20, fill="x")
        self.quantity.bind("<KeyRelease>", lambda e: self.calculate_emission())
        
        # Emission display (calculated automatically)
        self.emission_label = ctk.CTkLabel(activities_frame, text="Emission: 0.00 kg CO2", 
                                          font=ctk.CTkFont(size=14, weight="bold"))
        self.emission_label.pack(pady=10)
        
        # Date input
        self.date_entry = ctk.CTkEntry(activities_frame, placeholder_text="Date (YYYY-MM-DD)")
        self.date_entry.pack(pady=5, padx=20, fill="x")
        
        # Set today's date
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Buttons
        button_frame = ctk.CTkFrame(left_frame)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        save_button = ctk.CTkButton(button_frame, text="Save Entry", 
                                   command=self.save_entry, height=40)
        save_button.pack(side="left", padx=10, fill="x", expand=True)
        
        reset_button = ctk.CTkButton(button_frame, text="Reset Form", 
                                    command=self.reset_form, height=40)
        reset_button.pack(side="left", padx=10, fill="x", expand=True)
        
        # Right frame for info
        right_frame = ctk.CTkFrame(entry_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0), pady=10)
        
        # Info section
        info_frame = ctk.CTkFrame(right_frame)
        info_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(info_frame, text="Activity Information", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        self.info_label = ctk.CTkLabel(info_frame, text="Enter an activity in the text field above (e.g., 'car travel', 'electricity usage', 'flight') to see emission factors and units.", 
                                      wraplength=300)
        self.info_label.pack(pady=10)
        
        # Recent entries
        self.recent_frame = ctk.CTkFrame(right_frame)
        self.recent_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(self.recent_frame, text="Recent Entries", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        self.load_recent_entries()
    

    
    def get_activity_data(self):
        """Get predefined activity data with emission factors"""
        return {
            "Car Travel": {"unit": "km", "factor": 0.12},
            "Bus Travel": {"unit": "km", "factor": 0.03},
            "Flight Travel": {"unit": "km", "factor": 0.18},
            "Electricity Usage": {"unit": "kWh", "factor": 0.82},
            "Cooking Gas": {"unit": "kg", "factor": 2.9},
            "Food Consumption": {"unit": "kg", "factor": 1.6},
            "Plastic Waste": {"unit": "kg", "factor": 1.2},
            "Organic Waste": {"unit": "kg", "factor": 0.3},
            "AC Usage": {"unit": "hours", "factor": 1.0},
            "Water Usage": {"unit": "liters", "factor": 0.002}
        }
    
    def on_activity_change(self):
        """Auto-detect activity type and set unit/factor using generic carbon formula"""
        activity_text = self.activity_entry.get().lower().strip()
        
        # FUEL COMBUSTION: Emissions = Fuel used (L or kg) × Fuel EF (kg CO₂e per L or kg)
        if any(word in activity_text for word in ['petrol', 'gasoline', 'car fuel']):
            self.current_unit = "liters"
            self.current_factor = 2.31  # kg CO₂e per liter petrol
        elif any(word in activity_text for word in ['diesel', 'diesel fuel']):
            self.current_unit = "liters"
            self.current_factor = 2.68  # kg CO₂e per liter diesel
        elif any(word in activity_text for word in ['lpg', 'cooking gas', 'gas cylinder']):
            self.current_unit = "kg"
            self.current_factor = 3.0   # kg CO₂e per kg LPG
        elif any(word in activity_text for word in ['natural gas', 'png']):
            self.current_unit = "cubic meters"
            self.current_factor = 2.0   # kg CO₂e per cubic meter
        
        # ELECTRICITY USE: Emissions = Electricity (kWh) × Grid EF (kg CO₂e per kWh)
        elif any(word in activity_text for word in ['electric', 'power', 'energy', 'electricity']):
            self.current_unit = "kWh"
            self.current_factor = 0.82  # kg CO₂e per kWh (India grid average)
        
        # TRAVEL: Emissions = Distance (km) × EF (kg CO₂e per passenger-km)
        elif any(word in activity_text for word in ['car', 'drive', 'vehicle', 'auto']):
            self.current_unit = "km"
            self.current_factor = 0.12  # kg CO₂e per passenger-km (average car)
        elif any(word in activity_text for word in ['bus', 'public transport']):
            self.current_unit = "km"
            self.current_factor = 0.03  # kg CO₂e per passenger-km (bus)
        elif any(word in activity_text for word in ['train', 'railway', 'metro']):
            self.current_unit = "km"
            self.current_factor = 0.014 # kg CO₂e per passenger-km (train)
        elif any(word in activity_text for word in ['flight', 'plane', 'air', 'airplane']):
            self.current_unit = "km"
            self.current_factor = 0.255 # kg CO₂e per passenger-km (domestic flight)
        elif any(word in activity_text for word in ['bike', 'motorcycle', 'scooter']):
            self.current_unit = "km"
            self.current_factor = 0.06  # kg CO₂e per km (motorcycle)
        
        # GOODS & SERVICES
        elif any(word in activity_text for word in ['food', 'meal', 'eat', 'restaurant']):
            self.current_unit = "kg"
            self.current_factor = 2.5   # kg CO₂e per kg food (average)
        elif any(word in activity_text for word in ['meat', 'beef', 'chicken']):
            self.current_unit = "kg"
            self.current_factor = 6.0   # kg CO₂e per kg meat
        elif any(word in activity_text for word in ['vegetable', 'veg', 'plant']):
            self.current_unit = "kg"
            self.current_factor = 0.5   # kg CO₂e per kg vegetables
        
        # WASTE TREATMENT
        elif any(word in activity_text for word in ['waste', 'trash', 'garbage', 'landfill']):
            self.current_unit = "kg"
            self.current_factor = 0.5   # kg CO₂e per kg waste
        elif any(word in activity_text for word in ['plastic', 'plastic waste']):
            self.current_unit = "kg"
            self.current_factor = 1.8   # kg CO₂e per kg plastic waste
        elif any(word in activity_text for word in ['paper', 'cardboard']):
            self.current_unit = "kg"
            self.current_factor = 0.9   # kg CO₂e per kg paper waste
        
        # DIGITAL & SERVICES
        elif any(word in activity_text for word in ['internet', 'data', 'streaming', 'cloud']):
            self.current_unit = "GB"
            self.current_factor = 0.006 # kg CO₂e per GB data
        elif any(word in activity_text for word in ['email', 'emails']):
            self.current_unit = "emails"
            self.current_factor = 0.004 # kg CO₂e per email
        
        # HEATING/COOLING
        elif any(word in activity_text for word in ['ac', 'air condition', 'cooling', 'heating']):
            self.current_unit = "hours"
            self.current_factor = 1.5   # kg CO₂e per hour AC usage
        
        # WATER
        elif any(word in activity_text for word in ['water', 'shower', 'bath']):
            self.current_unit = "liters"
            self.current_factor = 0.0015 # kg CO₂e per liter water
        
        # SPEND-BASED: Emissions = Spending (₹, $, etc.) × EF (kg CO₂e per currency unit)
        elif any(word in activity_text for word in ['shopping', 'purchase', 'buy', 'spent']):
            self.current_unit = "₹"
            self.current_factor = 0.0005 # kg CO₂e per ₹ spent (average)
        elif any(word in activity_text for word in ['hotel', 'accommodation']):
            self.current_unit = "nights"
            self.current_factor = 30.0  # kg CO₂e per night hotel stay
        
        # MANUFACTURING & MATERIALS
        elif any(word in activity_text for word in ['cement', 'concrete']):
            self.current_unit = "kg"
            self.current_factor = 0.9   # kg CO₂e per kg cement
        elif any(word in activity_text for word in ['steel', 'iron']):
            self.current_unit = "kg"
            self.current_factor = 2.3   # kg CO₂e per kg steel
        elif any(word in activity_text for word in ['aluminum', 'aluminium']):
            self.current_unit = "kg"
            self.current_factor = 8.2   # kg CO₂e per kg aluminum
        
        else:
            # Default for unknown activities
            self.current_unit = "units"
            self.current_factor = 1.0
        
        self.unit_label.configure(text=f"Unit: {self.current_unit}")
        self.info_label.configure(text=f"Emission Factor: {self.current_factor} kg CO₂e per {self.current_unit}")
        
        # Update emission calculation
        self.calculate_emission()
    
    def calculate_emission(self):
        """Calculate emission using generic formula: Emissions = Activity Data × Emission Factor"""
        try:
            quantity_text = self.quantity.get().strip()
            
            if quantity_text and hasattr(self, 'current_factor'):
                activity_data = float(quantity_text)  # Activity data (L, kWh, km, kg, etc.)
                emission_factor = self.current_factor  # Emission factor (kg CO₂e per unit)
                
                # Generic Formula: Emissions (kg CO₂e) = Activity data × Emission factor
                total_emissions = activity_data * emission_factor
                
                self.emission_label.configure(text=f"Emission: {total_emissions:.3f} kg CO₂e")
                return total_emissions
        except:
            pass
        
        self.emission_label.configure(text="Emission: 0.000 kg CO₂e")
        return 0
    
    def save_entry(self):
        """Save entry to database"""
        try:
            user_name = self.user_name.get().strip()
            activity_name = self.activity_entry.get().strip()
            quantity = self.quantity.get().strip()
            date = self.date_entry.get().strip()
            
            if not all([user_name, activity_name, quantity, date]):
                messagebox.showerror("Error", "All fields are required!")
                return
            
            if not hasattr(self, 'current_unit') or not hasattr(self, 'current_factor'):
                messagebox.showerror("Error", "Please enter an activity to detect emission factor!")
                return
            
            unit = self.current_unit
            emission_factor = self.current_factor
            
            # Get or create user
            self.cursor.execute("SELECT user_id FROM users WHERE name = ?", (user_name,))
            user_result = self.cursor.fetchone()
            
            if user_result:
                user_id = user_result[0]
            else:
                self.cursor.execute("INSERT INTO users (name, age, city) VALUES (?, ?, ?)", 
                                   (user_name, 25, "Unknown"))
                user_id = self.cursor.lastrowid
            
            # Get or create activity
            self.cursor.execute("SELECT activity_id FROM activities WHERE activity_name = ?", 
                               (activity_name,))
            activity_result = self.cursor.fetchone()
            
            if activity_result:
                activity_id = activity_result[0]
            else:
                self.cursor.execute("""
                    INSERT INTO activities (activity_name, unit, emission_factor) 
                    VALUES (?, ?, ?)
                """, (activity_name, unit, emission_factor))
                activity_id = self.cursor.lastrowid
            
            # Insert record
            self.cursor.execute("""
                INSERT INTO records (user_id, activity_id, quantity, date) 
                VALUES (?, ?, ?, ?)
            """, (user_id, activity_id, float(quantity), date))
            
            self.conn.commit()
            
            # Calculate and show emission
            total_emission = float(quantity) * emission_factor
            messagebox.showinfo("Success", f"Entry saved!\nEmission: {total_emission:.2f} kg CO2")
            self.reset_form()
            self.load_recent_entries()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def load_recent_entries(self):
        """Load recent entries"""
        try:
            # Clear existing entries safely
            children = list(self.recent_frame.winfo_children())
            for widget in children:
                if isinstance(widget, ctk.CTkLabel):
                    try:
                        if widget.cget("text") != "Recent Entries":
                            widget.destroy()
                    except:
                        pass
            
            self.cursor.execute("""
                SELECT u.name, a.activity_name, r.quantity, r.date,
                       ROUND(r.quantity * a.emission_factor, 2) as emission
                FROM records r
                JOIN users u ON r.user_id = u.user_id
                JOIN activities a ON r.activity_id = a.activity_id
                ORDER BY r.record_id DESC
                LIMIT 5
            """)
            
            entries = self.cursor.fetchall()
            
            for entry in entries:
                name, activity, quantity, date, emission = entry
                text = f"{name}: {quantity} {activity} ({emission} kg CO2)"
                try:
                    label = ctk.CTkLabel(self.recent_frame, text=text, font=ctk.CTkFont(size=14))
                    label.pack(pady=3, padx=10, anchor="w")
                except:
                    pass
                
        except Exception as e:
            try:
                error_label = ctk.CTkLabel(self.recent_frame, text=f"Error: {str(e)}")
                error_label.pack(pady=5)
            except:
                pass
    
    def show_records_page(self):
        """Show records page"""
        self.page_history.append('home')
        
        # Clear main container
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Create back button
        back_frame = ctk.CTkFrame(self.main_container)
        back_frame.pack(fill="x", padx=20, pady=(10, 0))
        
        back_btn = ctk.CTkButton(back_frame, text="← Back", 
                                command=self.go_back,
                                height=35, width=150)
        back_btn.pack(side="left", padx=10, pady=10)
        
        self.setup_records_view()
    
    def setup_records_view(self):
        """Setup records view"""
        records_frame = self.main_container
        
        # Header
        header = ctk.CTkLabel(records_frame, text="Carbon Activity Records", 
                             font=ctk.CTkFont(size=24, weight="bold"))
        header.pack(pady=20)
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(records_frame)
        nav_frame.pack(fill="x", padx=20, pady=10)
        
        refresh_btn = ctk.CTkButton(nav_frame, text="🔄 Refresh", command=self.load_records)
        refresh_btn.pack(side="left", padx=10, pady=10)
        
        delete_btn = ctk.CTkButton(nav_frame, text="🗑️ Delete Selected", 
                                  command=self.delete_record, fg_color="red")
        delete_btn.pack(side="left", padx=10, pady=10)
        
        edit_btn = ctk.CTkButton(nav_frame, text="✏️ Edit Selected", 
                                command=self.edit_record, fg_color="orange")
        edit_btn.pack(side="left", padx=10, pady=10)
        
        charts_btn = ctk.CTkButton(nav_frame, text="📊 Analytics", 
                                  command=self.show_charts_page)
        charts_btn.pack(side="right", padx=10, pady=10)
        
        reports_btn = ctk.CTkButton(nav_frame, text="📄 Reports", 
                                   command=self.show_reports_page)
        reports_btn.pack(side="right", padx=10, pady=10)
        
        analytics_btn = ctk.CTkButton(nav_frame, text="🔬 Advanced Analytics", 
                                     command=self.show_advanced_analytics,
                                     fg_color="purple", hover_color="darkviolet")
        analytics_btn.pack(side="right", padx=10, pady=10)
        
        # Treeview frame
        tree_frame = ctk.CTkFrame(records_frame)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create treeview
        import tkinter.ttk as ttk
        
        # Configure style for larger font
        style = ttk.Style()
        style.configure("Treeview", font=('Segoe UI', 12))
        style.configure("Treeview.Heading", font=('Segoe UI', 12, 'bold'))
        
        columns = ('ID', 'User', 'Activity', 'Quantity', 'Date', 'Emission (kg CO2)')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        self.load_records()
    
    def show_charts_page(self):
        """Show charts page"""
        self.page_history.append('records')
        
        # Clear main container
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Create back button
        back_frame = ctk.CTkFrame(self.main_container)
        back_frame.pack(fill="x", padx=20, pady=(10, 0))
        
        back_btn = ctk.CTkButton(back_frame, text="← Back", 
                                command=self.go_back,
                                height=35, width=150)
        back_btn.pack(side="left", padx=10, pady=10)
        
        self.setup_charts_view()
    
    def setup_charts_view(self):
        """Setup charts view"""
        charts_frame = self.main_container
        
        # Header
        header = ctk.CTkLabel(charts_frame, text="Analytics Dashboard", 
                             font=ctk.CTkFont(size=24, weight="bold"))
        header.pack(pady=20)
        
        # Chart buttons
        btn_frame = ctk.CTkFrame(charts_frame)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(btn_frame, text="📊 Top Activities", 
                     command=self.show_top_activities_chart).pack(side="left", padx=10, pady=10)
        ctk.CTkButton(btn_frame, text="🥧 Activity Breakdown", 
                     command=self.show_activity_chart).pack(side="left", padx=10, pady=10)
        ctk.CTkButton(btn_frame, text="📈 Monthly Trends", 
                     command=self.show_monthly_chart).pack(side="left", padx=10, pady=10)
        
        # Chart area
        self.chart_frame = ctk.CTkFrame(charts_frame)
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    def show_reports_page(self):
        """Show reports page"""
        self.page_history.append('records')
        
        # Clear main container
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Create back button
        back_frame = ctk.CTkFrame(self.main_container)
        back_frame.pack(fill="x", padx=20, pady=(10, 0))
        
        back_btn = ctk.CTkButton(back_frame, text="← Back", 
                                command=self.go_back,
                                height=35, width=150)
        back_btn.pack(side="left", padx=10, pady=10)
        
        self.setup_reports_view()
    
    def setup_reports_view(self):
        """Setup reports view"""
        reports_frame = self.main_container
        
        # Header
        header = ctk.CTkLabel(reports_frame, text="Generate Reports", 
                             font=ctk.CTkFont(size=24, weight="bold"))
        header.pack(pady=50)
        
        # Report buttons
        report_frame = ctk.CTkFrame(reports_frame)
        report_frame.pack(pady=50)
        
        summary_btn = ctk.CTkButton(report_frame, text="📋 Executive Summary (PDF)", 
                                   command=self.generate_summary_report, height=60,
                                   font=ctk.CTkFont(size=16, weight="bold"))
        summary_btn.pack(pady=15, padx=40)
        
        detailed_btn = ctk.CTkButton(report_frame, text="📊 Detailed Analysis (PDF)", 
                                    command=self.generate_detailed_report, height=60,
                                    font=ctk.CTkFont(size=16, weight="bold"),
                                    fg_color="green", hover_color="darkgreen")
        detailed_btn.pack(pady=15, padx=40)
        
        excel_btn = ctk.CTkButton(report_frame, text="📈 Excel Data Export", 
                                 command=self.generate_excel_report, height=60,
                                 font=ctk.CTkFont(size=16, weight="bold"),
                                 fg_color="#4A90E2", hover_color="#357ABD")
        excel_btn.pack(pady=15, padx=40)
        
        # Enhanced PG-Level Reports
        ctk.CTkLabel(report_frame, text="PG-Level Advanced Reports", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(30, 10))
        
        dashboard_btn = ctk.CTkButton(report_frame, text="🎯 Executive Dashboard", 
                                     command=self.generate_enhanced_dashboard, height=60,
                                     font=ctk.CTkFont(size=16, weight="bold"),
                                     fg_color="#8B5A2B", hover_color="#654321")
        dashboard_btn.pack(pady=10, padx=40)
        
        technical_btn = ctk.CTkButton(report_frame, text="🔬 Technical Analysis", 
                                     command=self.generate_technical_report, height=60,
                                     font=ctk.CTkFont(size=16, weight="bold"),
                                     fg_color="#4B0082", hover_color="#301934")
        technical_btn.pack(pady=10, padx=40)
        
        scorecard_btn = ctk.CTkButton(report_frame, text="🏆 Sustainability Scorecard", 
                                     command=self.generate_scorecard_report, height=60,
                                     font=ctk.CTkFont(size=16, weight="bold"),
                                     fg_color="#DC143C", hover_color="#B22222")
        scorecard_btn.pack(pady=10, padx=40)
    
    def load_records(self):
        """Load records into treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            self.cursor.execute("""
                SELECT r.record_id, u.name, a.activity_name, r.quantity, r.date,
                       ROUND(r.quantity * a.emission_factor, 2) as emission
                FROM records r
                JOIN users u ON r.user_id = u.user_id
                JOIN activities a ON r.activity_id = a.activity_id
                ORDER BY r.record_id ASC
            """)
            
            for row in self.cursor.fetchall():
                self.tree.insert('', 'end', values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load records: {str(e)}")
    
    def delete_record(self):
        """Delete selected record"""
        selected = self.tree.selection()
        if selected:
            record_id = self.tree.item(selected[0])['values'][0]
            if messagebox.askyesno("Confirm", "Delete this record?"):
                try:
                    self.cursor.execute("DELETE FROM records WHERE record_id = ?", (record_id,))
                    self.conn.commit()
                    self.load_records()
                    self.load_recent_entries()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete: {str(e)}")
    
    def edit_record(self):
        """Edit selected record"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a record to edit")
            return
        
        # Get record data
        values = self.tree.item(selected[0])['values']
        record_id, user_name, activity_name, quantity, date, emission = values
        
        # Create edit window
        edit_window = ctk.CTkToplevel(self.root)
        edit_window.title("Edit Record")
        edit_window.geometry("450x600")
        edit_window.resizable(False, False)
        edit_window.grab_set()  # Make window modal
        
        # Form fields
        ctk.CTkLabel(edit_window, text="Edit Record", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 30))
        
        # User Name
        ctk.CTkLabel(edit_window, text="User Name:", font=ctk.CTkFont(size=14)).pack(pady=(10, 5))
        user_entry = ctk.CTkEntry(edit_window, width=350, height=35)
        user_entry.pack(pady=(0, 15))
        user_entry.insert(0, user_name)
        
        # Activity
        ctk.CTkLabel(edit_window, text="Activity:", font=ctk.CTkFont(size=14)).pack(pady=(0, 5))
        activity_entry = ctk.CTkEntry(edit_window, width=350, height=35)
        activity_entry.pack(pady=(0, 15))
        activity_entry.insert(0, activity_name)
        
        # Quantity
        ctk.CTkLabel(edit_window, text="Quantity:", font=ctk.CTkFont(size=14)).pack(pady=(0, 5))
        quantity_entry = ctk.CTkEntry(edit_window, width=350, height=35)
        quantity_entry.pack(pady=(0, 15))
        quantity_entry.insert(0, str(quantity))
        
        # Date
        ctk.CTkLabel(edit_window, text="Date (YYYY-MM-DD):", font=ctk.CTkFont(size=14)).pack(pady=(0, 5))
        date_entry = ctk.CTkEntry(edit_window, width=350, height=35)
        date_entry.pack(pady=(0, 20))
        date_entry.insert(0, date)
        
        # Update button
        def update_record():
            try:
                new_user = user_entry.get().strip()
                new_activity = activity_entry.get().strip()
                new_quantity = float(quantity_entry.get().strip())
                new_date = date_entry.get().strip()
                
                # Get or create user
                self.cursor.execute("SELECT user_id FROM users WHERE name = ?", (new_user,))
                user_result = self.cursor.fetchone()
                if user_result:
                    user_id = user_result[0]
                else:
                    self.cursor.execute("INSERT INTO users (name, age, city) VALUES (?, ?, ?)", 
                                       (new_user, 25, "Unknown"))
                    user_id = self.cursor.lastrowid
                
                # Get or create activity
                self.cursor.execute("SELECT activity_id FROM activities WHERE activity_name = ?", 
                                   (new_activity,))
                activity_result = self.cursor.fetchone()
                if activity_result:
                    activity_id = activity_result[0]
                else:
                    self.cursor.execute("INSERT INTO activities (activity_name, unit, emission_factor) VALUES (?, ?, ?)", 
                                       (new_activity, "units", 1.0))
                    activity_id = self.cursor.lastrowid
                
                # Update record
                self.cursor.execute("""
                    UPDATE records 
                    SET user_id = ?, activity_id = ?, quantity = ?, date = ?
                    WHERE record_id = ?
                """, (user_id, activity_id, new_quantity, new_date, record_id))
                
                self.conn.commit()
                messagebox.showinfo("Success", "Record updated successfully!")
                edit_window.destroy()
                self.load_records()
                self.load_recent_entries()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update: {str(e)}")
        
        # Create button frame for better layout
        button_frame = ctk.CTkFrame(edit_window)
        button_frame.pack(pady=30, padx=20, fill="x")
        
        update_btn = ctk.CTkButton(button_frame, text="Update Record", command=update_record, 
                                  height=45, width=200, font=ctk.CTkFont(size=16, weight="bold"),
                                  fg_color="green", hover_color="darkgreen")
        update_btn.pack(pady=15)
        
        cancel_btn = ctk.CTkButton(button_frame, text="Cancel", command=edit_window.destroy,
                                  height=35, width=150, fg_color="gray", hover_color="darkgray")
        cancel_btn.pack(pady=10)
    

    
    def clear_chart_frame(self):
        """Safely clear chart frame"""
        try:
            plt.close('all')  # Close all matplotlib figures
            for widget in list(self.chart_frame.winfo_children()):
                try:
                    widget.destroy()
                except:
                    pass
        except:
            pass
    
    def show_top_activities_chart(self):
        """Show top carbon-producing activities"""
        try:
            self.cursor.execute("""
                SELECT a.activity_name, SUM(r.quantity * a.emission_factor) as total_emission
                FROM records r
                JOIN activities a ON r.activity_id = a.activity_id
                GROUP BY a.activity_name
                ORDER BY total_emission DESC
                LIMIT 8
            """)
            
            data = self.cursor.fetchall()
            if not data:
                messagebox.showinfo("Info", "No data available")
                return
            
            activities = [row[0] for row in data]
            emissions = [row[1] for row in data]
            
            self.clear_chart_frame()
            
            fig, ax = plt.subplots(figsize=(10, 5))
            bars = ax.bar(activities, emissions, color='#87CEEB', alpha=0.9)
            ax.set_title('Top Carbon-Producing Activities', fontsize=16, fontweight='bold')
            ax.set_ylabel('Total Emissions (kg CO₂)')
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}', ha='center', va='bottom')
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            plt.close(fig)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate chart: {str(e)}")
    
    def show_activity_chart(self):
        """Show activity breakdown chart"""
        try:
            self.cursor.execute("""
                SELECT a.activity_name, SUM(r.quantity * a.emission_factor) as total_emission
                FROM records r
                JOIN activities a ON r.activity_id = a.activity_id
                GROUP BY a.activity_name
                ORDER BY total_emission DESC
            """)
            
            data = self.cursor.fetchall()
            if not data:
                messagebox.showinfo("Info", "No data available")
                return
            
            activities = [row[0] for row in data]
            emissions = [row[1] for row in data]
            
            self.clear_chart_frame()
            
            fig, ax = plt.subplots(figsize=(10, 6))
            colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc', '#c2c2f0']
            
            wedges, texts, autotexts = ax.pie(emissions, autopct='%1.1f%%', 
                                             colors=colors, startangle=90, pctdistance=1.1, 
                                             textprops={'fontsize': 10})
            ax.set_title('Emissions by Activity Type', fontsize=16, fontweight='bold')
            ax.legend(wedges, activities, title="Activities", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            
            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            plt.close(fig)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate chart: {str(e)}")
    
    def show_monthly_chart(self):
        """Show monthly emissions trends"""
        try:
            self.cursor.execute("""
                SELECT strftime('%Y-%m', r.date) as month, 
                       SUM(r.quantity * a.emission_factor) as total_emission
                FROM records r
                JOIN activities a ON r.activity_id = a.activity_id
                GROUP BY strftime('%Y-%m', r.date)
                ORDER BY month
            """)
            
            data = self.cursor.fetchall()
            if not data:
                messagebox.showinfo("Info", "No data available")
                return
            
            months = [row[0] for row in data]
            emissions = [row[1] for row in data]
            
            self.clear_chart_frame()
            
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(months, emissions, marker='o', linewidth=3, markersize=8, color='#2ca02c')
            ax.fill_between(months, emissions, alpha=0.3, color='#2ca02c')
            ax.set_title('Monthly Carbon Emissions Trend', fontsize=16, fontweight='bold')
            ax.set_ylabel('Total Emissions (kg CO₂)')
            ax.set_xlabel('Month')
            
            # Add value labels on points
            for i, (month, emission) in enumerate(zip(months, emissions)):
                ax.text(i, emission + max(emissions)*0.02, f'{emission:.1f}', 
                       ha='center', va='bottom', fontweight='bold')
            
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            plt.close(fig)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate chart: {str(e)}")
    

    
    def generate_summary_report(self):
        """Generate executive summary report"""
        try:
            filename = f"executive_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            c = canvas.Canvas(filename, pagesize=letter)
            
            # Header
            c.setStrokeColorRGB(0.1, 0.3, 0.7)
            c.setLineWidth(3)
            c.rect(40, 720, 520, 60)
            
            c.setFont("Helvetica-Bold", 22)
            c.drawString(60, 750, "EXECUTIVE SUMMARY")
            c.setFont("Helvetica", 12)
            c.drawString(60, 730, f"Carbon Footprint Overview - {datetime.now().strftime('%B %Y')}")
            
            y = 680
            
            # Key Metrics Box
            self.cursor.execute("""
                SELECT COUNT(*), SUM(r.quantity * a.emission_factor), AVG(r.quantity * a.emission_factor)
                FROM records r JOIN activities a ON r.activity_id = a.activity_id
            """)
            total_records, total_emissions, avg_emission = self.cursor.fetchone()
            
            c.setStrokeColorRGB(0.8, 0.8, 0.8)
            c.setFillColorRGB(0.95, 0.98, 1.0)
            c.rect(50, y-80, 500, 100, fill=1)
            
            c.setFillColorRGB(0, 0, 0)
            c.setFont("Helvetica-Bold", 18)
            c.drawString(70, y-15, "KEY PERFORMANCE INDICATORS")
            
            c.setFont("Helvetica-Bold", 14)
            c.drawString(70, y-35, f"Total Footprint: {total_emissions:.1f} kg CO2")
            c.drawString(300, y-35, f"Activities: {total_records}")
            c.drawString(70, y-55, f"Daily Average: {total_emissions/30:.1f} kg CO2")
            c.drawString(300, y-55, f"Per Activity: {avg_emission:.1f} kg CO2")
            
            y -= 120
            
            # Top 3 Impact Areas
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, y, "TOP 3 IMPACT AREAS")
            y -= 25
            
            self.cursor.execute("""
                SELECT a.activity_name, SUM(r.quantity * a.emission_factor) as total
                FROM records r JOIN activities a ON r.activity_id = a.activity_id
                GROUP BY a.activity_name ORDER BY total DESC LIMIT 3
            """)
            
            colors = [(0.8, 0.2, 0.2), (0.9, 0.6, 0.1), (0.2, 0.7, 0.3)]
            for i, (activity, emission) in enumerate(self.cursor.fetchall()):
                c.setFillColorRGB(*colors[i])
                c.rect(50, y-15, 30, 20, fill=1)
                c.setFillColorRGB(0, 0, 0)
                c.setFont("Helvetica-Bold", 14)
                c.drawString(90, y-10, f"{i+1}. {activity}")
                c.setFont("Helvetica", 12)
                c.drawString(350, y-10, f"{emission:.1f} kg CO2 ({emission/total_emissions*100:.1f}%)")
                y -= 30
            
            y -= 20
            
            # Quick Wins
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, y, "IMMEDIATE ACTION ITEMS")
            y -= 25
            
            c.setFont("Helvetica", 12)
            actions = [
                "1. Target your #1 emission source for 20% reduction",
                "2. Set weekly tracking goals using this app",
                "3. Implement one energy-saving measure this month"
            ]
            
            for action in actions:
                c.setFillColorRGB(0.9, 0.95, 0.9)
                c.rect(50, y-15, 500, 20, fill=1)
                c.setFillColorRGB(0, 0, 0)
                c.drawString(60, y-8, action)
                y -= 30
            
            # Footer
            c.setFont("Helvetica-Bold", 10)
            c.drawString(50, 80, "EXECUTIVE RECOMMENDATION:")
            c.setFont("Helvetica", 10)
            c.drawString(50, 65, f"Focus on reducing {self.cursor.execute('SELECT a.activity_name FROM records r JOIN activities a ON r.activity_id = a.activity_id GROUP BY a.activity_name ORDER BY SUM(r.quantity * a.emission_factor) DESC LIMIT 1').fetchone()[0] if self.cursor.execute('SELECT COUNT(*) FROM records').fetchone()[0] > 0 else 'top activities'} to achieve maximum impact.")
            c.drawString(50, 50, "Next review recommended in 30 days.")
            
            c.save()
            messagebox.showinfo("Success", f"Executive Summary generated: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate summary: {str(e)}")
    
    def generate_detailed_report(self):
        """Generate comprehensive PDF report"""
        try:
            filename = f"carbon_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            c = canvas.Canvas(filename, pagesize=letter)
            
            # Header with border
            c.setStrokeColorRGB(0.2, 0.5, 0.3)
            c.setLineWidth(2)
            c.rect(40, 720, 520, 60)
            
            c.setFont("Helvetica-Bold", 20)
            c.drawString(60, 750, "CARBON FOOTPRINT ANALYSIS REPORT")
            c.setFont("Helvetica", 12)
            c.drawString(60, 730, f"Report Date: {datetime.now().strftime('%B %d, %Y at %H:%M')}")
            
            y = 680
            
            # Overall Statistics with box
            self.cursor.execute("""
                SELECT COUNT(*), SUM(r.quantity * a.emission_factor), AVG(r.quantity * a.emission_factor)
                FROM records r JOIN activities a ON r.activity_id = a.activity_id
            """)
            total_records, total_emissions, avg_emission = self.cursor.fetchone()
            
            # Summary box
            c.setStrokeColorRGB(0.8, 0.8, 0.8)
            c.setFillColorRGB(0.95, 0.95, 0.95)
            c.rect(50, y-60, 500, 80, fill=1)
            
            c.setFillColorRGB(0, 0, 0)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(70, y-10, "EXECUTIVE SUMMARY")
            
            c.setFont("Helvetica-Bold", 12)
            c.drawString(70, y-30, f"Total Carbon Footprint: {total_emissions:.2f} kg CO2 equivalent")
            c.setFont("Helvetica", 11)
            c.drawString(70, y-45, f"Average per Activity: {avg_emission:.2f} kg CO2  |  Total Activities: {total_records}")
            
            y -= 100
            
            # Environmental Impact Assessment
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y, "ENVIRONMENTAL IMPACT ASSESSMENT")
            y -= 20
            
            # Calculate equivalent impacts
            trees_needed = total_emissions / 22  # 1 tree absorbs ~22kg CO2/year
            car_miles = total_emissions / 0.404  # 1 mile = ~0.404 kg CO2
            
            c.setFont("Helvetica", 11)
            c.drawString(50, y, f"Your carbon footprint is equivalent to:")
            y -= 15
            c.drawString(70, y, f"• {trees_needed:.1f} trees needed to offset for 1 year")
            y -= 15
            c.drawString(70, y, f"• {car_miles:.0f} miles of car driving")
            y -= 15
            c.drawString(70, y, f"• {total_emissions/1000:.2f} tons of CO2 emissions")
            y -= 30
            
            # Top Activities with visual bars
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y, "TOP CARBON-PRODUCING ACTIVITIES")
            y -= 25
            
            self.cursor.execute("""
                SELECT a.activity_name, SUM(r.quantity * a.emission_factor) as total
                FROM records r JOIN activities a ON r.activity_id = a.activity_id
                GROUP BY a.activity_name ORDER BY total DESC LIMIT 5
            """)
            
            activities = self.cursor.fetchall()
            max_emission = activities[0][1] if activities else 1
            
            c.setFont("Helvetica", 11)
            for i, (activity, emission) in enumerate(activities):
                # Draw bar
                bar_width = (emission / max_emission) * 200
                c.setFillColorRGB(0.2, 0.7, 0.3)
                c.rect(250, y-10, bar_width, 12, fill=1)
                
                # Draw text
                c.setFillColorRGB(0, 0, 0)
                percentage = (emission/total_emissions*100)
                c.drawString(50, y, f"{i+1}. {activity[:25]}")
                c.drawString(460, y, f"{emission:.1f} kg ({percentage:.1f}%)")
                y -= 20
            
            y -= 20
            
            # Monthly Trends
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y, "MONTHLY EMISSION TRENDS")
            y -= 20
            
            self.cursor.execute("""
                SELECT strftime('%Y-%m', r.date) as month, SUM(r.quantity * a.emission_factor) as total
                FROM records r JOIN activities a ON r.activity_id = a.activity_id
                GROUP BY month ORDER BY month DESC LIMIT 6
            """)
            
            c.setFont("Helvetica", 11)
            monthly_data = self.cursor.fetchall()
            for month, emission in monthly_data:
                month_name = datetime.strptime(month, '%Y-%m').strftime('%B %Y')
                c.drawString(50, y, f"• {month_name}: {emission:.2f} kg CO2")
                y -= 15
            
            y -= 20
            
            # Action Plan
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y, "PERSONALIZED ACTION PLAN")
            y -= 20
            
            # Get top activity for personalized recommendations
            top_activity = activities[0][0] if activities else "general"
            
            c.setFont("Helvetica", 11)
            if "electricity" in top_activity.lower():
                c.drawString(50, y, "Priority: Reduce electricity consumption")
                y -= 15
                c.drawString(70, y, "• Switch to LED bulbs and energy-efficient appliances")
                y -= 15
                c.drawString(70, y, "• Consider solar panels or renewable energy plans")
            elif "travel" in top_activity.lower() or "car" in top_activity.lower():
                c.drawString(50, y, "Priority: Optimize transportation")
                y -= 15
                c.drawString(70, y, "• Use public transport, bike, or walk when possible")
                y -= 15
                c.drawString(70, y, "• Consider carpooling or electric/hybrid vehicles")
            else:
                c.drawString(50, y, "General recommendations:")
                y -= 15
                c.drawString(70, y, "• Focus on your top emission sources above")
                y -= 15
                c.drawString(70, y, "• Set monthly reduction targets")
            
            y -= 15
            c.drawString(70, y, "• Track progress monthly using this app")
            y -= 15
            c.drawString(70, y, "• Consider carbon offset programs")
            
            # Footer
            c.setFont("Helvetica-Oblique", 9)
            c.drawString(50, 50, "Generated by Carbon Footprint Tracker - Take action today for a sustainable tomorrow!")
            
            c.save()
            messagebox.showinfo("Success", f"Comprehensive PDF report generated: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF: {str(e)}")
    
    def generate_detailed_report(self):
        """Generate detailed analysis report"""
        try:
            filename = f"detailed_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            c = canvas.Canvas(filename, pagesize=letter)
            
            # Header
            c.setStrokeColorRGB(0.2, 0.5, 0.3)
            c.setLineWidth(2)
            c.rect(40, 720, 520, 60)
            
            c.setFont("Helvetica-Bold", 20)
            c.drawString(60, 750, "DETAILED CARBON FOOTPRINT ANALYSIS")
            c.setFont("Helvetica", 12)
            c.drawString(60, 730, f"Comprehensive Report - {datetime.now().strftime('%B %d, %Y')}")
            
            y = 680
            
            # Statistical Overview
            self.cursor.execute("""
                SELECT COUNT(*), SUM(r.quantity * a.emission_factor), AVG(r.quantity * a.emission_factor),
                       MIN(r.quantity * a.emission_factor), MAX(r.quantity * a.emission_factor)
                FROM records r JOIN activities a ON r.activity_id = a.activity_id
            """)
            total_records, total_emissions, avg_emission, min_emission, max_emission = self.cursor.fetchone()
            
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y, "STATISTICAL ANALYSIS")
            y -= 20
            
            c.setFont("Helvetica", 11)
            c.drawString(50, y, f"Total Emissions: {total_emissions:.2f} kg CO2 | Mean: {avg_emission:.2f} | Range: {min_emission:.2f} - {max_emission:.2f}")
            y -= 15
            c.drawString(50, y, f"Standard Deviation: {((total_emissions - avg_emission * total_records) / total_records)**.5:.2f} kg CO2")
            y -= 30
            
            # Activity Breakdown
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y, "ACTIVITY BREAKDOWN ANALYSIS")
            y -= 25
            
            self.cursor.execute("""
                SELECT a.activity_name, COUNT(*) as freq, SUM(r.quantity * a.emission_factor) as total,
                       AVG(r.quantity * a.emission_factor) as avg, a.unit
                FROM records r JOIN activities a ON r.activity_id = a.activity_id
                GROUP BY a.activity_name ORDER BY total DESC
            """)
            
            c.setFont("Helvetica-Bold", 10)
            c.drawString(50, y, "Activity")
            c.drawString(200, y, "Frequency")
            c.drawString(280, y, "Total (kg CO2)")
            c.drawString(380, y, "Avg (kg CO2)")
            c.drawString(480, y, "Unit")
            y -= 15
            
            c.setFont("Helvetica", 9)
            for activity, freq, total, avg, unit in self.cursor.fetchall():
                if y < 100:
                    break
                c.drawString(50, y, activity[:20])
                c.drawString(200, y, str(freq))
                c.drawString(280, y, f"{total:.2f}")
                c.drawString(380, y, f"{avg:.2f}")
                c.drawString(480, y, unit[:8])
                y -= 12
            
            y -= 20
            
            # Trend Analysis
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y, "TEMPORAL TREND ANALYSIS")
            y -= 20
            
            self.cursor.execute("""
                SELECT strftime('%Y-%m', r.date) as month, SUM(r.quantity * a.emission_factor) as total
                FROM records r JOIN activities a ON r.activity_id = a.activity_id
                GROUP BY month ORDER BY month
            """)
            
            monthly_data = self.cursor.fetchall()
            if len(monthly_data) > 1:
                trend = "increasing" if monthly_data[-1][1] > monthly_data[0][1] else "decreasing"
                c.setFont("Helvetica", 11)
                c.drawString(50, y, f"Trend Direction: {trend.upper()}")
                y -= 15
                
                for month, emission in monthly_data[-6:]:
                    month_name = datetime.strptime(month, '%Y-%m').strftime('%b %Y')
                    c.drawString(50, y, f"{month_name}: {emission:.2f} kg CO2")
                    y -= 12
            
            y -= 20
            
            # Recommendations
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y, "STRATEGIC RECOMMENDATIONS")
            y -= 20
            
            c.setFont("Helvetica", 11)
            recommendations = [
                "Short-term (1-3 months): Focus on behavioral changes",
                "Medium-term (3-12 months): Invest in efficiency improvements", 
                "Long-term (1+ years): Consider renewable energy solutions",
                "Monitoring: Track progress monthly using this application"
            ]
            
            for rec in recommendations:
                c.drawString(50, y, f"• {rec}")
                y -= 15
            
            c.save()
            messagebox.showinfo("Success", f"Detailed Analysis generated: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate detailed report: {str(e)}")
    
    def generate_excel_report(self):
        """Generate comprehensive Excel report with multiple sheets"""
        try:
            filename = f"carbon_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            # All Records
            df_records = pd.read_sql_query("""
                SELECT r.record_id, u.name as user_name, a.activity_name, 
                       r.quantity, r.date, a.unit,
                       ROUND(r.quantity * a.emission_factor, 2) as emission_kg_co2
                FROM records r
                JOIN users u ON r.user_id = u.user_id
                JOIN activities a ON r.activity_id = a.activity_id
                ORDER BY r.date
            """, self.conn)
            
            # Activity Summary
            df_activity_summary = pd.read_sql_query("""
                SELECT a.activity_name, COUNT(*) as frequency,
                       SUM(r.quantity * a.emission_factor) as total_emissions,
                       AVG(r.quantity * a.emission_factor) as avg_emissions,
                       a.unit
                FROM records r
                JOIN activities a ON r.activity_id = a.activity_id
                GROUP BY a.activity_name
                ORDER BY total_emissions DESC
            """, self.conn)
            
            # Monthly Trends
            df_monthly = pd.read_sql_query("""
                SELECT strftime('%Y-%m', r.date) as month,
                       COUNT(*) as activities_count,
                       SUM(r.quantity * a.emission_factor) as total_emissions
                FROM records r
                JOIN activities a ON r.activity_id = a.activity_id
                GROUP BY month
                ORDER BY month
            """, self.conn)
            
            # User Analysis
            df_users = pd.read_sql_query("""
                SELECT u.name, COUNT(*) as total_activities,
                       SUM(r.quantity * a.emission_factor) as total_emissions,
                       AVG(r.quantity * a.emission_factor) as avg_per_activity
                FROM records r
                JOIN users u ON r.user_id = u.user_id
                JOIN activities a ON r.activity_id = a.activity_id
                GROUP BY u.name
                ORDER BY total_emissions DESC
            """, self.conn)
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df_records.to_excel(writer, sheet_name='All Records', index=False)
                df_activity_summary.to_excel(writer, sheet_name='Activity Analysis', index=False)
                df_monthly.to_excel(writer, sheet_name='Monthly Trends', index=False)
                df_users.to_excel(writer, sheet_name='User Analysis', index=False)
            
            messagebox.showinfo("Success", f"Comprehensive Excel analysis generated: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate Excel: {str(e)}")
    
    def generate_enhanced_dashboard(self):
        """Generate PG-level executive dashboard"""
        try:
            from enhanced_reports import EnhancedReportGenerator
            enhanced_gen = EnhancedReportGenerator(self.conn)
            filename = enhanced_gen.generate_executive_dashboard()
            messagebox.showinfo("Success", f"Executive Dashboard generated: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate dashboard: {str(e)}")
    
    def generate_technical_report(self):
        """Generate technical analysis report"""
        try:
            from enhanced_reports import EnhancedReportGenerator
            enhanced_gen = EnhancedReportGenerator(self.conn)
            filename = enhanced_gen.generate_technical_analysis_report()
            messagebox.showinfo("Success", f"Technical Analysis generated: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate technical report: {str(e)}")
    
    def generate_scorecard_report(self):
        """Generate sustainability scorecard"""
        try:
            from enhanced_reports import EnhancedReportGenerator
            enhanced_gen = EnhancedReportGenerator(self.conn)
            filename = enhanced_gen.generate_sustainability_scorecard()
            messagebox.showinfo("Success", f"Sustainability Scorecard generated: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate scorecard: {str(e)}")
    
    def show_advanced_analytics(self):
        """Show advanced analytics page with complex queries"""
        self.page_history.append('records')
        
        # Clear main container
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Create back button
        back_frame = ctk.CTkFrame(self.main_container)
        back_frame.pack(fill="x", padx=20, pady=(10, 0))
        
        back_btn = ctk.CTkButton(back_frame, text="← Back", 
                                command=self.go_back,
                                height=35, width=150)
        back_btn.pack(side="left", padx=10, pady=10)
        
        self.setup_advanced_analytics()
    
    def setup_advanced_analytics(self):
        """Setup advanced analytics view with complex queries"""
        analytics_frame = self.main_container
        
        # Header
        header = ctk.CTkLabel(analytics_frame, text="Advanced Analytics Dashboard", 
                             font=ctk.CTkFont(size=24, weight="bold"))
        header.pack(pady=20)
        
        # Query buttons
        btn_frame = ctk.CTkFrame(analytics_frame)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        # Row 1
        row1 = ctk.CTkFrame(btn_frame)
        row1.pack(fill="x", pady=5)
        
        ctk.CTkButton(row1, text="User Rankings", command=lambda: self.show_query_result(1),
                     fg_color="#FF6B6B", text_color="white", width=180, height=40, font=ctk.CTkFont(size=12)).pack(side="left", padx=3, pady=5)
        ctk.CTkButton(row1, text="Growth Analysis", command=lambda: self.show_query_result(2),
                     fg_color="#4ECDC4", text_color="white", width=180, height=40, font=ctk.CTkFont(size=12)).pack(side="left", padx=3, pady=5)
        ctk.CTkButton(row1, text="Activity Correlations", command=lambda: self.show_query_result(3),
                     fg_color="#45B7D1", text_color="white", width=180, height=40, font=ctk.CTkFont(size=12)).pack(side="left", padx=3, pady=5)
        ctk.CTkButton(row1, text="Top Contributors", command=lambda: self.show_query_result(4),
                     fg_color="#96CEB4", text_color="white", width=180, height=40, font=ctk.CTkFont(size=12)).pack(side="left", padx=3, pady=5)
        ctk.CTkButton(row1, text="Anomaly Detection", command=lambda: self.show_query_result(5),
                     fg_color="#FFEAA7", text_color="black", width=180, height=40, font=ctk.CTkFont(size=12)).pack(side="left", padx=3, pady=5)
        
        # Row 2
        row2 = ctk.CTkFrame(btn_frame)
        row2.pack(fill="x", pady=5)
        
        ctk.CTkButton(row2, text="Seasonal Patterns", command=lambda: self.show_query_result(6),
                     fg_color="#DDA0DD", text_color="white", width=180, height=40, font=ctk.CTkFont(size=12)).pack(side="left", padx=3, pady=5)
        ctk.CTkButton(row2, text="User Clustering", command=lambda: self.show_query_result(7),
                     fg_color="#98D8C8", text_color="white", width=180, height=40, font=ctk.CTkFont(size=12)).pack(side="left", padx=3, pady=5)
        ctk.CTkButton(row2, text="Forecasting Data", command=lambda: self.show_query_result(8),
                     fg_color="#F7DC6F", text_color="black", width=180, height=40, font=ctk.CTkFont(size=12)).pack(side="left", padx=3, pady=5)
        ctk.CTkButton(row2, text="Efficiency Analysis", command=lambda: self.show_query_result(9),
                     fg_color="#BB8FCE", text_color="white", width=180, height=40, font=ctk.CTkFont(size=12)).pack(side="left", padx=3, pady=5)
        ctk.CTkButton(row2, text="Impact Assessment", command=lambda: self.show_query_result(10),
                     fg_color="#85C1E9", text_color="white", width=180, height=40, font=ctk.CTkFont(size=12)).pack(side="left", padx=3, pady=5)
        
        # Results area
        self.analytics_frame = ctk.CTkScrollableFrame(analytics_frame)
        self.analytics_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    def show_query_result(self, query_num):
        """Show result of specific complex query"""
        # Clear previous results
        for widget in self.analytics_frame.winfo_children():
            widget.destroy()
        
        try:
            cq = ComplexQueries(self.conn)
            
            query_methods = {
                1: (cq.query_1_user_ranking_with_percentiles, "User Rankings with Percentiles"),
                2: (cq.query_2_monthly_growth_analysis, "Monthly Growth Analysis"),
                3: (cq.query_3_activity_correlation_matrix, "Activity Correlation Matrix"),
                4: (cq.query_4_top_contributors_by_category, "Top Contributors by Category"),
                5: (cq.query_5_emission_anomaly_detection, "Emission Anomaly Detection"),
                6: (cq.query_6_seasonal_pattern_analysis, "Seasonal Pattern Analysis"),
                7: (cq.query_7_user_behavior_clustering, "User Behavior Clustering"),
                8: (cq.query_8_emission_forecasting_data, "Emission Forecasting Data"),
                9: (cq.query_9_carbon_efficiency_analysis, "Carbon Efficiency Analysis"),
                10: (cq.query_10_comprehensive_impact_assessment, "Comprehensive Impact Assessment")
            }
            
            method, title = query_methods[query_num]
            results = method()
            
            # Display title
            title_label = ctk.CTkLabel(self.analytics_frame, text=title, 
                                      font=ctk.CTkFont(size=18, weight="bold"))
            title_label.pack(pady=10)
            
            # Display results in a table-like format
            if results:
                # Create headers (first row keys)
                if len(results) > 0 and len(results[0]) > 0:
                    # Show first 10 results
                    for i, row in enumerate(results[:10]):
                        row_frame = ctk.CTkFrame(self.analytics_frame)
                        row_frame.pack(fill="x", padx=10, pady=2)
                        
                        row_text = " | ".join([str(item)[:20] for item in row])
                        ctk.CTkLabel(row_frame, text=f"{i+1}. {row_text}", 
                                    font=ctk.CTkFont(size=12)).pack(pady=5, padx=10, anchor="w")
                    
                    if len(results) > 10:
                        ctk.CTkLabel(self.analytics_frame, text=f"... and {len(results)-10} more rows",
                                    font=ctk.CTkFont(size=10)).pack(pady=5)
            else:
                ctk.CTkLabel(self.analytics_frame, text="No data available for this analysis").pack(pady=20)
                
        except Exception as e:
            error_label = ctk.CTkLabel(self.analytics_frame, text=f"Error: {str(e)}", 
                                      text_color="red")
            error_label.pack(pady=20)
    
    def reset_form(self):
        """Reset form fields"""
        self.user_name.delete(0, 'end')
        self.activity_entry.delete(0, 'end')
        self.quantity.delete(0, 'end')
        self.date_entry.delete(0, 'end')
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.unit_label.configure(text="Unit: Type an activity")
        self.emission_label.configure(text="Emission: 0.00 kg CO2")
        self.info_label.configure(text="Type an activity to see details")
        
        # Reset current values
        if hasattr(self, 'current_unit'):
            delattr(self, 'current_unit')
        if hasattr(self, 'current_factor'):
            delattr(self, 'current_factor')
    
    def go_back(self):
        """Go back to previous page"""
        if self.page_history:
            previous_page = self.page_history.pop()
            if previous_page == 'home':
                self.show_home_page()
            elif previous_page == 'records':
                self.show_records_page()
    
    def on_closing(self):
        """Handle application closing"""
        try:
            plt.close('all')  # Close all matplotlib figures
            self.conn.close()
        except:
            pass
        self.root.destroy()
    
    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"Application error: {e}")
        finally:
            try:
                self.conn.close()
            except:
                pass

if __name__ == "__main__":
    app = ModernCarbonTracker()
    app.run()