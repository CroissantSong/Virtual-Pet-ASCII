import json
import os
import random
from datetime import datetime
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, scrolledtext
from tkinter import font as tkFont


# Attempt to import Pillow (PIL)
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Pillow library not found. Icons will not be loaded. Please install Pillow: pip install Pillow")

# Compatibility for json.JSONDecodeError
try:
    JSONDecodeError = json.JSONDecodeError
except AttributeError:
    JSONDecodeError = ValueError # Fallback for older Python versions

PET_FILE = "my_pet.json"
ASCII_ART_FILE = "pet_ascii_art.json"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DAY_DURATION = 24 * 60 * 60
DAYS_PER_WEEK = 7

# --- Pet Class (Unchanged) ---
class Pet:
    def __init__(self, name, species, gender, neutered=False, stamina=30):
        self.name = name
        self.species = species
        self.gender = gender
        self.hunger = 50
        self.happiness = 50
        self.health = 100
        self.age = 1
        self.alive = True
        self.neutered = neutered
        self.stamina = 20

    def feed(self):
        if not self.alive:
            return f"{self.name} is no longer here, cannot feed."
        if self.stamina < 8:
            return "Not enough stamina to feed!"
        self.stamina -= 8
        self.hunger = min(100, self.hunger + 20)
        self.happiness = min(100, self.happiness + 5)
        return f"You fed {self.name}. Hunger increased, mood improved, stamina -8."

    def play(self):
        if not self.alive:
            return f"{self.name} is no longer here, cannot play."
        if self.stamina < 15:
            return "Not enough stamina to play!"
        self.stamina -= 15
        self.happiness = min(100, self.happiness + 15)
        self.hunger = max(0, self.hunger - 10)
        return f"You played with {self.name}. Mood greatly improved, but a bit hungry, stamina -15."

    def clean(self):
        if not self.alive:
            return f"{self.name} is no longer here, cannot clean."
        if self.stamina < 12:
            return "Not enough stamina to clean!"
        self.stamina -= 12
        self.health = min(100, self.health + 10)
        self.happiness = min(100, self.happiness + 5)
        return f"You bathed {self.name}. Health and mood both improved, stamina -12."

    def rest(self, rested_today):
        if not self.alive:
            return f"{self.name} is no longer here, cannot rest.", rested_today
        if rested_today:
            return "Already rested once today, cannot rest again.", rested_today
        self.stamina = min(30, self.stamina + 5)
        self.health = min(100, self.health + 10)
        self.hunger = max(0, self.hunger - 5)
        return f"{self.name} rested for a while. Health recovered, stamina +5.", True

    def grow(self):
        messages = []
        if not self.alive:
            return messages
        self.age += 1
        self.hunger = max(0, self.hunger - 10)
        self.happiness = max(0, self.happiness - 5)
        self.stamina = 20
        health_decrease = 0
        if self.hunger < 20:
            health_decrease = 10
        elif self.hunger < 50:
            health_decrease = 5
        self.health = max(0, self.health - health_decrease)
        if self.hunger <= 0 or self.health <= 0:
            self.alive = False
            messages.append(f"\nUnfortunately, {self.name} has passed away due to neglect.")
        elif self.age % 7 == 0:
            messages.append(f"\n{self.name} has grown a little older!")
        return messages

    def to_dict(self):
        return {
            "name": self.name, "species": self.species, "gender": self.gender,
            "hunger": self.hunger, "happiness": self.happiness, "health": self.health,
            "age": self.age, "alive": self.alive, "neutered": self.neutered, "stamina": self.stamina
        }

    @classmethod
    def from_dict(cls, data):
        pet = cls(
            data["name"], data["species"], data.get("gender", "Male"),
            data.get("neutered", False), data.get("stamina", 20)
        )
        pet.hunger = data["hunger"]
        pet.happiness = data["happiness"]
        pet.health = data["health"]
        pet.age = data["age"]
        pet.alive = data["alive"]
        pet.stamina = min(30, max(0, data.get("stamina", 20)))
        return pet

# --- Helper Functions ---
def get_now():
    return datetime.now()

def save_pet_data(pet_obj, current_day, current_week, last_time_obj):
    data = {
        "pet": pet_obj.to_dict(), "current_day": current_day,
        "current_week": current_week, "last_time": last_time_obj.strftime(TIME_FORMAT)
    }
    with open(PET_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_pet_data():
    if os.path.exists(PET_FILE):
        try:
            with open(PET_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            pet = Pet.from_dict(data["pet"])
            current_day = data.get("current_day", 1)
            current_week = data.get("current_week", 1)
            last_time_str = data.get("last_time", get_now().strftime(TIME_FORMAT))
            last_time = datetime.strptime(last_time_str, TIME_FORMAT)
            return pet, current_day, current_week, last_time
        except (JSONDecodeError, KeyError, FileNotFoundError) as e: # Use the new JSONDecodeError variable
            print(f"Error loading pet file: {e}. Starting fresh.")
            if os.path.exists(PET_FILE):
                try: os.remove(PET_FILE)
                except OSError: pass
            return None, 1, 1, get_now()
    return None, 1, 1, get_now()

def load_ascii_art():
    if os.path.exists(ASCII_ART_FILE):
        try:
            with open(ASCII_ART_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (JSONDecodeError, FileNotFoundError) as e: # Use the new JSONDecodeError variable
            print(f"Error loading ASCII art file: {e}. Using default empty art.")
            return {"_default_": {"idle": ["ASCII Art", "Not Found"]}}
    return {"_default_": {"idle": ["ASCII Art", "File Missing"]}}


def advance_days_on_load(pet_obj, last_time_obj, current_day_val, current_week_val, app_ref):
    now = get_now()
    elapsed = (now - last_time_obj).total_seconds()
    days_passed = int(elapsed // DAY_DURATION)
    MAX_CATCH_UP_DAYS = 365
    if days_passed > MAX_CATCH_UP_DAYS:
        app_ref.log_message(f"Time since last play is very long. Capping catch-up to {MAX_CATCH_UP_DAYS} days.")
        days_passed = MAX_CATCH_UP_DAYS
    new_current_day, new_current_week = current_day_val, current_week_val
    if days_passed > 0 and pet_obj and pet_obj.alive:
        app_ref.log_message(f"Advancing {days_passed} day(s) due to time passed...")
        for _ in range(days_passed):
            if not pet_obj.alive:
                app_ref.log_message(f"{pet_obj.name} did not survive the time away.")
                break
            for msg in pet_obj.grow(): app_ref.log_message(msg)
            for msg in trigger_event_auto(pet_obj, new_current_day, app_ref): app_ref.log_message(msg)
            if random.random() < 0.1:
                pet_obj.stamina = min(30, pet_obj.stamina + 10)
                app_ref.log_message(f"\n【Lucky Event】{pet_obj.name} seemed energetic, stamina +10!")
            new_current_day += 1
            if new_current_day > DAYS_PER_WEEK:
                new_current_week += 1
                new_current_day = 1
                app_ref.log_message(f"A new week (Week {new_current_week}) started for {pet_obj.name}.")
        app_ref.log_message("Day advancement complete.")
    return pet_obj, new_current_day, new_current_week, now

def trigger_event_auto(pet, current_day, app):
    messages = []
    if not pet.alive: return messages
    if pet.age >= 15 and not pet.neutered and random.random() < 0.1:
        messages.append(f"\n【Event】{pet.species} ({pet.gender}) seemed restless (Estrus). Mood slightly affected.")
        pet.happiness = max(0, pet.happiness - 10)
    if random.random() < 0.1:
        messages.append(f"\n【Event】{pet.name} made a new friend outside today! Mood improved!.")
        pet.happiness = min(0, pet.happiness + 10)
    if random.random() < 0.1:
        messages.append(f"\n【Event】{pet.name} rolled around in the mud today. Happiness up, health down.")
        pet.happiness = min(0, pet.happiness + 10); pet.health = max(0, pet.health - 10)
    if random.random() < 0.1:
        messages.append(f"\n【Event】{pet.name} was fed a small piece of chocolate by a kind youth today! Mood improved, health decreased.")
        pet.happiness = min(0, pet.happiness + 10);
        pet.health = max(0, pet.health - 10)
    if random.random() < 0.1:
        messages.append(f"\n【Event】{pet.name} found a tasty snack at a food stall today! Mood and hunger both improved!")
        pet.happiness = min(0, pet.happiness + 10);
        pet.hunger = min(0, pet.hunger + 10)
    if random.random() < 0.005:
        messages.append(f"\n【Event】{pet.name} died today after accidentally ingesting pesticide.")
        pet.health = 0
        pet.alive = False
    return messages

def trigger_event_interactive(pet, current_day, app):
    if not pet.alive: return False
    event_happened = False
    if pet.happiness < 30 and random.random() < 0.6:
        app.log_message(f"\n【Sudden Event】Your {pet.name} seemed very depressed. Health slightly affected.")
        if messagebox.askyesno("Sudden Event", "Play with pet? (Yes)\nIgnore? (No)"):
            pet.happiness = min(100, pet.happiness + 30);
            pet.health = min(100, pet.health + 15)
            app.log_message("Mood and health improved!")
        else:
            pet.happiness = max(0, pet.happiness - 15);
            app.log_message("Mood greatly decreased.")
        event_happened = True
    elif pet.happiness > 70 and random.random() < 0.3:
        app.log_message(f"\n【Sudden Event】Your {pet.name} seemed quite happy and playful on its own.")
        if messagebox.askyesno("Sudden Event", "Play with pet? (Yes)\nIgnore? (No)"):
            pet.happiness = min(100, pet.happiness + 5); pet.health = min(100, pet.health + 5)
            app.log_message("Mood and health improved!")
        else:
            pet.happiness = max(0, pet.happiness - 30); app.log_message("Mood greatly decreased.")
        event_happened = True
    elif random.random() < 0.2:
        app.log_message(f"\n【Sudden Event】{pet.name} seems bored with the usual food and is curious about new things.")
        if messagebox.askyesno("Sudden Event", "Try some new food? (Yes)\nKeep original food? (No)"):
            if random.random() < 0.5:
                pet.hunger = min(100, pet.hunger + 5)
                app.log_message("Found a tasty morsel! Hunger slightly increased.")
            else:
                pet.happiness = max(0, pet.happiness - 5)
                app.log_message("New food is not tasty. Happiness slightly increased.")
        else:
            pet.happiness = max(0, pet.happiness - 30); pet.hunger = max(0, pet.hunger - 20)
            app.log_message("No eating!!! Mood greatly decreased.")
        event_happened = True
    return event_happened

def weekend_option_event(pet, app): # Unchanged
    if not pet or not pet.alive: return
    rand = random.random()
    msg = "【Weekend Event】"
    if rand < 0.2:
        attr = random.choice(['hunger', 'happiness', 'health', 'stamina'])
        old_val = getattr(pet, attr); new_val = max(0, old_val - 5); setattr(pet, attr, new_val)
        msg += f"{attr.capitalize()} randomly decreased by 5 (from {old_val} to {new_val})."
    elif rand < 0.5:
        attr = random.choice(['hunger', 'happiness', 'health', 'stamina'])
        old_val = getattr(pet, attr)
        if attr == 'stamina': new_val = min(30, old_val + 5)
        else: new_val = min(100, old_val + 5)
        setattr(pet, attr, new_val)
        msg += f"{attr.capitalize()} randomly increased by 5 (from {old_val} to {new_val})."
    elif rand < 0.9:
        attr = random.choice(['hunger', 'happiness', 'health', 'stamina'])
        old_val = getattr(pet, attr)
        if attr == 'stamina': new_val = 30
        else: new_val = 100
        setattr(pet, attr, new_val)
        msg += f"{attr.capitalize()} was boosted to maximum ({new_val})!"
    else:
        pet.hunger = 100; pet.happiness = 100; pet.health = 100; pet.stamina = 30
        msg += "All stats boosted to maximum!"
    app.log_message(msg)

# --- GUI Application ---
class PetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual Pet Paradise ASCII")
        self.root.geometry("800x900") # Adjusted for ASCII art
        self.pet = None
        self.current_day = 1
        self.current_week = 1
        self.last_interaction_time = get_now()
        self.rested_today = False
        self.pet_icons = {} # To store PhotoImage objects

        self.pet_ascii_art_data = load_ascii_art() # Load ASCII art

        # --- Style Definitions (similar to previous beautification) ---
        self.style = ttk.Style()
        try: self.style.theme_use('clam')
        except tk.TclError: self.style.theme_use(self.style.theme_names()[0])

        self.clr_bg_root = "#E0E0FF"
        self.clr_bg_frame = "#F0F0FF"
        self.clr_bg_labelframe_content = "#FFFFFF"
        self.clr_text_main = "#202040"
        self.clr_text_header = "#3030A0"
        self.clr_text_subheader = "#4040B0"
        self.clr_button_bg = "#7070E0"
        self.clr_button_fg = "#FFFFFF"
        self.clr_button_active_bg = "#5050C0"
        self.clr_border = "#C0C0E0"
        self.clr_log_bg = "#F8F8FF"
        self.clr_log_fg = "#303050"
        self.clr_ascii_bg = "#FAFAFA" # Background for ASCII art
        self.clr_ascii_fg = "#101030" # Text color for ASCII art

        self.root.configure(bg=self.clr_bg_root)
        self.font_main = ("Verdana", 14)
        self.font_header = ("Verdana", 20, "bold")
        self.font_subheader = ("Verdana", 16, "bold")
        self.font_button = ("Verdana", 12) # Slightly smaller for icon + text
        self.font_log = ("Consolas", 14)
        self.font_ascii = ("Courier New", 12) # Monospaced for ASCII art

        self.style.configure("TFrame", background=self.clr_bg_frame)
        self.style.configure("Header.TLabel", font=self.font_header, padding=(0,10,0,10), background=self.clr_bg_root, foreground=self.clr_text_header)
        self.style.configure("TLabel", font=self.font_main, padding=3, background=self.clr_bg_labelframe_content, foreground=self.clr_text_main)
        self.style.configure("Dialog.TLabel", font=self.font_main, padding=3, background=self.clr_bg_frame, foreground=self.clr_text_main)
        self.style.configure("StatusKey.TLabel", font=self.font_main, weight="bold", padding=(0,2,5,2), background=self.clr_bg_labelframe_content, foreground=self.clr_text_subheader)
        self.style.configure("TLabelframe", background=self.clr_bg_labelframe_content, padding=10, relief="groove", bordercolor=self.clr_border, borderwidth=1)
        self.style.configure("TLabelframe.Label", font=self.font_subheader, foreground=self.clr_text_subheader, background=self.clr_bg_frame, padding=(5,2))
        self.style.configure("TButton", font=self.font_button, padding=(8, 5), relief="raised", background=self.clr_button_bg, foreground=self.clr_button_fg, borderwidth=1, bordercolor=self.clr_button_active_bg)
        self.style.map("TButton", background=[('active', self.clr_button_active_bg), ('disabled', '#CDCDCD')], foreground=[('disabled', '#888888')], relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        self.style.configure("TRadiobutton", font=self.font_main, padding=2, background=self.clr_bg_frame, foreground=self.clr_text_main)
        self.style.map("TRadiobutton", background=[('active', self.clr_bg_root)], indicatorbackground=[('selected', self.clr_button_bg)])
        self.style.configure("TMenubutton", font=self.font_main, padding=(5,3), background=self.clr_button_bg, foreground=self.clr_button_fg)

        self._load_icons() # Load icons

        # --- Main Frames ---
        self.top_frame_container = ttk.Frame(root, style="TFrame") # Container for info and appearance
        self.top_frame_container.pack(fill=tk.X, pady=(10,5), padx=15)

        self.info_frame = ttk.Frame(self.top_frame_container, padding=(10,10,10,0))
        self.info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.appearance_frame = ttk.LabelFrame(self.top_frame_container, text="Pet", padding=5)
        self.appearance_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10,0), expand=True)

        self.status_frame = ttk.LabelFrame(root, text="Pet Stats", padding=15)
        self.status_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        self.actions_frame = ttk.LabelFrame(root, text="Actions", padding=15)
        self.actions_frame.pack(fill=tk.X, padx=15, pady=5)

        self.message_frame = ttk.LabelFrame(root, text="Log", padding=10)
        self.message_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5,15))

        # --- Info Area ---
        self.day_week_label = ttk.Label(self.info_frame, text="", style="Header.TLabel")
        self.day_week_label.pack(pady=5, anchor=tk.W)

        # --- Appearance Area (ASCII Art) ---
        self.pet_ascii_label = tk.Label(self.appearance_frame, text="", font=self.font_ascii,
                                        justify=tk.LEFT, anchor=tk.CENTER,
                                        bg=self.clr_ascii_bg, fg=self.clr_ascii_fg,
                                        padx=10, pady=10) # Use tk.Label for more control with bg/fg for ASCII
        self.pet_ascii_label.pack(pady=5, padx=5, expand=True, fill=tk.BOTH)


        # --- Status Display ---
        self.status_vars = {}
        stats = ["Name", "Species", "Gender", "Age", "Hunger", "Happiness", "Health", "Stamina", "Neutered", "Alive"]
        for i, stat_name in enumerate(stats):
            ttk.Label(self.status_frame, text=f"{stat_name}:", style="StatusKey.TLabel").grid(row=i, column=0, sticky="w", pady=3, padx=(0,10))
            self.status_vars[stat_name] = tk.StringVar()
            ttk.Label(self.status_frame, textvariable=self.status_vars[stat_name]).grid(row=i, column=1, sticky="w", padx=5, pady=3)
        self.status_frame.grid_columnconfigure(1, weight=1)

        # --- Action Buttons ---
        # (text, command, icon_key)
        btn_config = [
            (" Feed", self.feed_pet, "feed"), (" Play", self.play_with_pet, "play"),
            (" Clean", self.clean_pet, "clean"), (" Rest", self.rest_pet, "rest"),
            (" Next Day", self.next_day, "next_day")
        ]
        for i, (text, cmd, icon_key) in enumerate(btn_config):
            icon_image = self.pet_icons.get(icon_key)
            # If you want only icon: text="", image=icon_image
            # If icon and text: text=text, image=icon_image, compound=tk.LEFT
            b = ttk.Button(self.actions_frame, text=text if not icon_image else text,
                           image=icon_image if PIL_AVAILABLE else None,
                           compound=tk.LEFT if icon_image else tk.NONE,
                           command=cmd)
            b.grid(row=i // 2, column=i % 2, padx=8, pady=8, sticky="ew")

        self.actions_frame.grid_columnconfigure(0, weight=1)
        self.actions_frame.grid_columnconfigure(1, weight=1)

        # --- Message Log ---
        self.message_log = scrolledtext.ScrolledText(self.message_frame, height=8, wrap=tk.WORD, state=tk.DISABLED, font=self.font_log, bg=self.clr_log_bg, fg=self.clr_log_fg, relief="solid", bd=1, padx=8, pady=8, insertbackground=self.clr_text_main)
        self.message_log.pack(fill=tk.BOTH, expand=True, pady=(5,0))

        # --- Menu ---
        menubar = tk.Menu(self.root, font=self.font_main); filemenu = tk.Menu(menubar, tearoff=0, font=self.font_main)
        filemenu.add_command(label="New Pet", command=self.start_new_game_prompt); filemenu.add_command(label="Clear Save Data", command=self.clear_save_data_prompt)
        filemenu.add_separator(); filemenu.add_command(label="Exit", command=self.quit_game)
        menubar.add_cascade(label="Game", menu=filemenu); self.root.config(menu=menubar)
        self.root.protocol("WM_DELETE_WINDOW", self.quit_game)
        self.load_game()
        self.update_pet_ascii_art("idle") # Initial ASCII art

    def _load_icons(self):
        if not PIL_AVAILABLE: return
        icon_files = {
            "feed": "icons/feed.png", "play": "icons/play.png",
            "clean": "icons/clean.png", "rest": "icons/rest.png",
        }
        for key, path in icon_files.items():
            try:
                # Ensure icons directory exists relative to script
                script_dir = os.path.dirname(os.path.abspath(__file__))
                icon_path = os.path.join(script_dir, path)

                if not os.path.exists(icon_path):
                    print(f"Icon not found: {icon_path}")
                    self.pet_icons[key] = None
                    continue

                img = Image.open(icon_path).resize((20, 20), Image.Resampling.LANCZOS) # Resize icons
                self.pet_icons[key] = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Error loading icon {key} ({path}): {e}")
                self.pet_icons[key] = None

    def update_pet_ascii_art(self, pose_key="idle"):
        if not hasattr(self, 'pet_ascii_label') or not self.pet_ascii_label.winfo_exists():
            return

        art_string = "Pet art not available."
        if self.pet and self.pet.alive:
            species_art = self.pet_ascii_art_data.get(self.pet.species, self.pet_ascii_art_data.get("_default_", {}))
            pose_art_list = species_art.get(pose_key, species_art.get("idle", ["Pose not found."]))
            art_string = "\n".join(pose_art_list)
        elif self.pet and not self.pet.alive:
            species_art = self.pet_ascii_art_data.get(self.pet.species, self.pet_ascii_art_data.get("_default_", {}))
            pose_art_list = species_art.get("sad", species_art.get("idle", [f"{self.pet.name} has passed."])) # Or a specific 'passed' pose
            art_string = "\n".join(pose_art_list)
        else: # No pet
            default_art = self.pet_ascii_art_data.get("_default_", {}).get("idle", ["No pet."])
            art_string = "\n".join(default_art)

        self.pet_ascii_label.config(text=art_string)


    def log_message(self, msg):
        if not hasattr(self, 'message_log') or not self.message_log.winfo_exists(): return
        self.message_log.config(state=tk.NORMAL)
        self.message_log.insert(tk.END, msg + "\n")
        self.message_log.see(tk.END)
        self.message_log.config(state=tk.DISABLED)
        print(msg)

    def update_display(self):
        if not hasattr(self, 'root') or not self.root.winfo_exists(): return
        if self.pet:
            self.day_week_label.config(text=f"Week {self.current_week}, Day {self.current_day}")
            self.status_vars["Name"].set(self.pet.name)
            self.status_vars["Species"].set(self.pet.species)
            self.status_vars["Gender"].set(self.pet.gender)
            self.status_vars["Age"].set(f"{self.pet.age} days")
            self.status_vars["Hunger"].set(f"{self.pet.hunger}/100")
            self.status_vars["Happiness"].set(f"{self.pet.happiness}/100")
            self.status_vars["Health"].set(f"{self.pet.health}/100")
            self.status_vars["Stamina"].set(f"{self.pet.stamina}/30")
            self.status_vars["Neutered"].set("Yes" if self.pet.neutered else "No")
            self.status_vars["Alive"].set("Healthy" if self.pet.alive else "Deceased")

            is_alive = self.pet.alive
            rest_btn_state = tk.DISABLED if self.rested_today or not is_alive else tk.NORMAL
            other_btn_state = tk.NORMAL if is_alive else tk.DISABLED

            for child in self.actions_frame.winfo_children():
                if isinstance(child, ttk.Button):
                    btn_text = child.cget("text").strip().lower()
                    if "rest" in btn_text: child.config(state=rest_btn_state)
                    else: child.config(state=other_btn_state)
        else:
            self.day_week_label.config(text="Welcome to Virtual Pet Paradise")
            for key in self.status_vars: self.status_vars[key].set("N/A")
            for child in self.actions_frame.winfo_children():
                if isinstance(child, ttk.Button): child.config(state=tk.DISABLED)
            self.update_pet_ascii_art("idle") # Show default for no pet
        self.root.update_idletasks() # Ensure UI updates promptly

    def save_game_state(self):
        if self.pet: save_pet_data(self.pet, self.current_day, self.current_week, self.last_interaction_time)

    def load_game(self):
        self.pet, self.current_day, self.current_week, self.last_interaction_time = load_pet_data()
        if self.pet:
            self.log_message(f"Welcome back! Loading pet {self.pet.name}.")
            self.pet, self.current_day, self.current_week, self.last_interaction_time = \
                advance_days_on_load(self.pet, self.last_interaction_time, self.current_day, self.current_week, self)
            self.rested_today = False
            if not self.pet.alive: self.handle_pet_death(manual_next_day=False)
            else:
                self.update_pet_ascii_art("idle")
                if self.current_day >= 5: # Example: weekend on day 5, 6, or 7
                    self.log_message(f"It's day {self.current_day}, checking for weekend event...")
                    weekend_option_event(self.pet, self)
        else:
            self.log_message("No saved pet found, please create a new pet.")
            self.choose_new_pet_dialog() # This will also call update_display and save
        self.update_display() # Ensure display is updated after loading or new pet dialog

    def choose_new_pet_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Create New Pet"); dialog.geometry("600x400"); dialog.transient(self.root)
        dialog.grab_set(); dialog.configure(bg=self.clr_bg_frame)
        content_frame = ttk.Frame(dialog, padding=15, style="TFrame"); content_frame.pack(expand=True, fill=tk.BOTH)
        ttk.Label(content_frame, text="Name your pet:", style="Dialog.TLabel").pack(pady=(0,5))
        name_entry = ttk.Entry(content_frame, font=self.font_main); name_entry.pack(pady=5, fill=tk.X); name_entry.focus_set()
        ttk.Label(content_frame, text="Choose species:", style="Dialog.TLabel").pack(pady=(10,5))
        species_var = tk.StringVar(value="Dog"); species_options = ["Dog", "Cat", "Bird"]
        species_menu = ttk.OptionMenu(content_frame, species_var, species_options[0], *species_options, style="TMenubutton")
        species_menu.pack(pady=5, fill=tk.X)
        ttk.Label(content_frame, text="Choose gender:", style="Dialog.TLabel").pack(pady=(10,5))
        gender_frame = ttk.Frame(content_frame, style="TFrame"); gender_frame.pack(pady=5)
        gender_var = tk.StringVar(value="Male")
        ttk.Radiobutton(gender_frame, text="Male", variable=gender_var, value="Male").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(gender_frame, text="Female", variable=gender_var, value="Female").pack(side=tk.LEFT, padx=10)

        def on_submit():
            name = name_entry.get().strip()
            if not name: messagebox.showerror("Error", "Pet name cannot be empty!", parent=dialog); return
            if len(name) > 15: messagebox.showerror("Error", "Pet name too long (max 15 char)!", parent=dialog); return
            self.pet = Pet(name, species_var.get(), gender_var.get())
            self.current_day = 1; self.current_week = 1
            self.last_interaction_time = get_now(); self.rested_today = False
            self.log_message(f"You adopted a new {self.pet.species} named {self.pet.name}!")
            self.update_pet_ascii_art("idle")
            dialog.destroy()
            self.update_display() # This will update ASCII art too
            self.save_game_state()
        submit_button = ttk.Button(content_frame, text="Create Pet", command=on_submit); submit_button.pack(pady=(15,5))
        self.root.wait_window(dialog)

    def _perform_action(self, action_func, *args, pose_after_action="idle"):
        if not self.pet or not self.pet.alive:
            self.log_message("Pet is not present or has passed away, cannot perform action.")
            return

        message_or_tuple = action_func(*args)
        log_msg = ""
        action_succeeded = True
        is_stamina_failure = False
        if isinstance(message_or_tuple, tuple):
            log_msg, new_rested_status = message_or_tuple
            self.rested_today = new_rested_status
            if "Already rested" in log_msg or \
                    (self.pet and f"{self.pet.name} is no longer here" in log_msg):  # 确保检查宠物名字以更精确
                action_succeeded = False
        else:
            log_msg = message_or_tuple
            if "Not enough stamina" in log_msg:
                is_stamina_failure = True
                action_succeeded = False
            elif (self.pet and f"{self.pet.name} is no longer here" in log_msg):  # 确保检查宠物名字以更精确
                action_succeeded = False

        self.log_message(log_msg)  # 记录日志消息

        if is_stamina_failure:
            self.update_pet_ascii_art("idle")
        elif not action_succeeded:
            pass
        else:
            self.update_pet_ascii_art(pose_after_action)
        self.update_display()
        self.save_game_state()
        self.check_pet_status()
    def feed_pet(self): self._perform_action(self.pet.feed, pose_after_action="feeding")
    def play_with_pet(self): self._perform_action(self.pet.play, pose_after_action="playing") # Play makes them happy
    def clean_pet(self): self._perform_action(self.pet.clean, pose_after_action="cleaning") # Or a "clean" pose
    def rest_pet(self): self._perform_action(self.pet.rest, self.rested_today, pose_after_action="resting")


    def next_day(self):
        if not self.pet or not self.pet.alive:
            self.log_message("Cannot proceed to the next day, no healthy pet available."); return
        self.log_message(f"--- {self.pet.name} enters a new day ---")
        self.pet.stamina = 20; self.rested_today = False
        for msg in self.pet.grow(): self.log_message(msg)
        if not self.pet.alive: self.handle_pet_death(); return
        self.update_pet_ascii_art("idle")
        trigger_event_interactive(self.pet, self.current_day, self)
        if random.random() < 0.1:
            self.pet.stamina = min(30, self.pet.stamina + 10)
            self.log_message(f"【Lucky Event】{self.pet.name} is energetic today, stamina +10!")
        self.current_day += 1
        if self.current_day > DAYS_PER_WEEK:
            self.current_week += 1; self.current_day = 1
            self.log_message(f"\nA new week has begun! It is now Week {self.current_week}.")
        self.last_interaction_time = get_now()
        if self.current_day >= 5: weekend_option_event(self.pet, self)
        if self.current_day == 6 and not self.pet.neutered and self.pet.age >= (DAYS_PER_WEEK + 6):
            self.prompt_neutering()
        self.update_display(); self.save_game_state(); self.check_pet_status()

    def prompt_neutering(self): # Unchanged logic, but added parent to messagebox
        if self.pet and self.pet.alive and not self.pet.neutered:
            self.log_message("\n【Special Tip】Pet is old enough for neutering.")
            self.log_message("Neutering prevents estrus events.")
            if messagebox.askyesno("Neutering Choice", "Neuter pet?", parent=self.root):
                self.pet.neutered = True; self.log_message("Pet successfully neutered.")
            else: self.log_message("Chose not to neuter.")
            self.save_game_state(); self.update_display()

    def check_pet_status(self):
        if self.pet and not self.pet.alive:
            self.handle_pet_death(); return True
        return False

    def handle_pet_death(self, manual_next_day=True): # Added parent to messagebox
        if manual_next_day: self.log_message(f"\nYour pet {self.pet.name} has passed away.")
        self.update_display() # This will show deceased status and update ASCII
        if messagebox.askyesno("Game Over", f"{self.pet.name} passed away.\nAdopt a new pet?", parent=self.root):
            self.start_new_game_logic()
        else: self.log_message("Thanks for playing! Start new game or exit from menu.")

    def start_new_game_prompt(self): # Added parent to messagebox
        if self.pet and self.pet.alive:
            if not messagebox.askyesno("New Game", "Current pet active. Start new game & lose progress?", parent=self.root): return
        self.start_new_game_logic()

    def start_new_game_logic(self):
        self.pet = None
        if os.path.exists(PET_FILE):
            try: os.remove(PET_FILE); self.log_message("Old save data cleared.")
            except OSError as e: self.log_message(f"Could not clear old save: {e}")
        self.choose_new_pet_dialog()

    def clear_save_data_prompt(self): # Added parent to all messageboxes
        if messagebox.askyesno("Clear Save Data", "Clear ALL save data? Cannot be undone.", parent=self.root):
            if os.path.exists(PET_FILE):
                try:
                    os.remove(PET_FILE); self.log_message("Save file cleared.")
                    self.pet = None; self.current_day = 1; self.current_week = 1
                    self.last_interaction_time = get_now(); self.rested_today = False
                    self.update_display()
                    messagebox.showinfo("Save Cleared", "Save data cleared. Start new game from menu.", parent=self.root)
                except OSError as e: messagebox.showerror("Error", f"Could not clear save: {e}", parent=self.root)
            else: messagebox.showinfo("Notice", "No save file found.", parent=self.root)

    def quit_game(self): # Added parent to all messageboxes
        should_destroy = False
        if self.pet and self.pet.alive:
            if messagebox.askokcancel("Exit", "Exit game? Progress will be saved.", parent=self.root):
                self.save_game_state(); should_destroy = True
        elif self.pet and not self.pet.alive:
            if messagebox.askokcancel("Exit", "Pet passed away. Exit game?", parent=self.root):
                should_destroy = True
        else:
            if messagebox.askokcancel("Exit", "Exit game?", parent=self.root):
                should_destroy = True
        if should_destroy: self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PetApp(root)
    root.mainloop()