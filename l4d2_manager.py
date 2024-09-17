import os
import tkinter as tk
import shutil
import re
import requests
import concurrent.futures
from tkinter import messagebox, filedialog, simpledialog
from html.parser import HTMLParser
from PIL import Image, ImageTk
import threading

# Path to the game folder and gameinfo.txt
GAME_FOLDER = os.getcwd()
LEFT4DEAD2_EXE = os.path.join(GAME_FOLDER, 'left4dead2.exe')
USERMODS_PATH = os.path.join(GAME_FOLDER, 'usermods')
WORKSHOP_PATH = os.path.join(GAME_FOLDER, 'left4dead2', 'addons', 'workshop')
GAMEINFO_PATH = os.path.join(GAME_FOLDER, 'left4dead2', 'gameinfo.txt')

# Function to check game folder and create usermods folder if necessary
def check_setup():
    if not os.path.isfile(LEFT4DEAD2_EXE):
        messagebox.showerror("Setup Error", "left4dead2.exe not found, please move the Tool to the same directory.")
        exit()

    if not os.path.exists(USERMODS_PATH):
        os.makedirs(USERMODS_PATH)

    if not os.path.exists(WORKSHOP_PATH):
        os.makedirs(WORKSHOP_PATH)  # Ensure workshop folder exists

check_setup()

def scan_for_mods():
    usermods_path = os.path.join(GAME_FOLDER, 'usermods')

    if not os.path.exists(usermods_path):
        messagebox.showerror("Error", f"usermods folder not found in {GAME_FOLDER}")
        return [], []

    enabled_mods = []
    disabled_mods = []

    all_mods = [
        folder_name for folder_name in os.listdir(usermods_path)
        if os.path.isdir(os.path.join(usermods_path, folder_name))
    ]

    if os.path.exists(GAMEINFO_PATH):
        with open(GAMEINFO_PATH, 'r') as file:
            gameinfo_content = file.readlines()

        enabled_mod_names = set()

        for line in gameinfo_content:
            line = line.strip()
            if line.startswith('Game\t\t\t\tusermods\\'):
                enabled_mod_name = line.split('usermods\\')[-1]
                if enabled_mod_name in all_mods:
                    enabled_mods.append(enabled_mod_name)
                    enabled_mod_names.add(enabled_mod_name)

        for mod in all_mods:
            mod_path = os.path.join(usermods_path, mod)
            if mod not in enabled_mod_names:
                if os.path.exists(os.path.join(mod_path, 'pak01_dir.vpk')):
                    disabled_mods.append(mod)

    else:
        disabled_mods = [
            mod for mod in all_mods 
            if os.path.exists(os.path.join(usermods_path, mod, 'pak01_dir.vpk'))
        ]

    return enabled_mods, disabled_mods

def update_mod_lists():
    enabled_mods, disabled_mods = scan_for_mods()
    enabled_listbox.delete(0, tk.END)
    disabled_listbox.delete(0, tk.END)

    for mod in enabled_mods:
        enabled_listbox.insert(tk.END, mod)

    for mod in disabled_mods:
        disabled_listbox.insert(tk.END, mod)

def disable_mods():
    selected_mods = enabled_listbox.curselection()
    if selected_mods:
        for index in selected_mods[::-1]:
            mod = enabled_listbox.get(index)
            enabled_listbox.delete(index)
            disabled_listbox.insert(tk.END, mod)

def enable_mods():
    selected_mods = disabled_listbox.curselection()
    if selected_mods:
        for index in selected_mods[::-1]:
            mod = disabled_listbox.get(index)
            disabled_listbox.delete(index)
            enabled_listbox.insert(tk.END, mod)

def apply_changes():
    usermods_path = os.path.join(GAME_FOLDER, 'usermods')

    if not os.path.exists(GAMEINFO_PATH):
        messagebox.showerror("Error", "gameinfo.txt not found in the left4dead2 folder.")
        return

    with open(GAMEINFO_PATH, 'r') as file:
        gameinfo_content = file.readlines()

    new_content = []
    
    for line in gameinfo_content:
        if not line.strip().startswith('Game\t\t\t\tusermods\\'):
            new_content.append(line)

    search_path_index = None
    for i, line in enumerate(new_content):
        if 'SearchPaths' in line:
            search_path_index = i + 2
            break

    if search_path_index is not None:
        enabled_mods = [enabled_listbox.get(i) for i in range(enabled_listbox.size())]
        temp_mod_entries = [f'\t\t\t\tGame\t\t\t\tusermods\\{mod}\n' for mod in enabled_mods]
        new_content[search_path_index:search_path_index] = temp_mod_entries

    with open(GAMEINFO_PATH, 'w') as file:
        file.writelines(new_content)

    messagebox.showinfo("Success", "Mod changes applied successfully!")
    update_mod_lists()

def refresh_mods():
    update_mod_lists()

def move_mod_up():
    selected_indices = enabled_listbox.curselection()
    if selected_indices:
        # Convert selection to a list and sort it in ascending order
        sorted_indices = sorted(selected_indices)
        # Store the original items to be moved
        items_to_move = [enabled_listbox.get(index) for index in sorted_indices]
        
        for index in sorted_indices:
            if index > 0:  # Normal move up
                mod = enabled_listbox.get(index)
                enabled_listbox.delete(index)
                enabled_listbox.insert(index - 1, mod)

        # Reselect the moved items
        for mod in items_to_move:
            new_index = enabled_listbox.get(0, tk.END).index(mod)
            enabled_listbox.select_set(new_index)

def move_mod_up():
    selected_indices = enabled_listbox.curselection()
    if selected_indices:
        # Convert selection to a list and sort it in ascending order
        sorted_indices = sorted(selected_indices)
        
        # Check if the first selected index is at the top
        if sorted_indices[0] == 0:
            return  # Prevent moving up if the first selected item is at the top

        # Store the original items to be moved
        items_to_move = [enabled_listbox.get(index) for index in sorted_indices]
        
        for index in sorted_indices:
            if index > 0:  # Normal move up
                mod = enabled_listbox.get(index)
                enabled_listbox.delete(index)
                enabled_listbox.insert(index - 1, mod)

        # Reselect the moved items
        for mod in items_to_move:
            new_index = enabled_listbox.get(0, tk.END).index(mod)
            enabled_listbox.select_set(new_index)

def move_mod_down():
    selected_indices = enabled_listbox.curselection()
    if selected_indices:
        # Convert selection to a list and sort it in descending order
        sorted_indices = sorted(selected_indices, reverse=True)
        
        # Check if the first selected index is at the bottom
        if sorted_indices[0] == enabled_listbox.size() - 1:
            return  # Prevent moving down if the first selected item is at the bottom

        # Store the original items to be moved
        items_to_move = [enabled_listbox.get(index) for index in sorted_indices]

        for index in sorted_indices:
            if index < enabled_listbox.size() - 1:  # Normal move down
                mod = enabled_listbox.get(index)
                enabled_listbox.delete(index)
                enabled_listbox.insert(index + 1, mod)

        # Reselect the moved items
        for mod in items_to_move:
            new_index = enabled_listbox.get(0, tk.END).index(mod)
            enabled_listbox.select_set(new_index)

# Function to delete selected mods
def delete_selected_mods():
    selected_enabled_mods = enabled_listbox.curselection()
    selected_disabled_mods = disabled_listbox.curselection()

    mods_to_delete = []
    if selected_enabled_mods:
        mods_to_delete += [enabled_listbox.get(i) for i in selected_enabled_mods]
    if selected_disabled_mods:
        mods_to_delete += [disabled_listbox.get(i) for i in selected_disabled_mods]

    if not mods_to_delete:
        messagebox.showwarning("Selection Error", "No mods selected for deletion.")
        return

    for mod in mods_to_delete:
        # Delete the mod folder (including non-empty ones)
        mod_path = os.path.join(USERMODS_PATH, mod)
        if os.path.exists(mod_path):
            try:
                shutil.rmtree(mod_path)  # This deletes the directory and all its contents
            except OSError as e:
                messagebox.showerror("Error", f"Failed to delete mod folder: {mod}. Error: {e}")
                continue

    # Update gameinfo.txt to remove the deleted mods
    with open(GAMEINFO_PATH, 'r') as file:
        gameinfo_content = file.readlines()

    new_content = []
    for line in gameinfo_content:
        if not any(mod in line for mod in mods_to_delete if line.strip().startswith('Game\t\t\t\tusermods\\')):
            new_content.append(line)

    with open(GAMEINFO_PATH, 'w') as file:
        file.writelines(new_content)

    update_mod_lists()
    messagebox.showinfo("Success", "Selected mods deleted successfully!")

# Dictionary to hold the mapping of mod names to their VPK filenames
mod_mapping = {}

# Function to add a new mod
def add_mod():
    # Open a file dialog to select a .vpk file
    vpk_file_path = filedialog.askopenfilename(title="Select a VPK file", filetypes=[("VPK Files", "*.vpk")])
    
    if not vpk_file_path:  # User cancelled the file dialog
        return

    while True:  # Loop until a valid folder name is provided or the user cancels
        # Ask for a folder name
        folder_name = simpledialog.askstring("Input", "Enter a name for the mod folder:")
        
        if folder_name is None:  # User cancelled the input dialog
            return
        
        # Check if the folder name contains only allowed characters (letters, digits, underscores, dashes)
        if re.match(r'^[\w-]+$', folder_name) and all(char not in folder_name for char in 'äöü'):
            break  # Valid folder name, exit the loop
        else:
            messagebox.showerror("Input Error", "Name contains invalid characters or spaces.")

    # Create the destination path
    destination_folder = os.path.join(USERMODS_PATH, folder_name)
    
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Define the new path for the VPK file
    new_vpk_file_path = os.path.join(destination_folder, 'pak01_dir.vpk')

    # Move and rename the selected VPK file
    try:
        shutil.copy(vpk_file_path, new_vpk_file_path)
        messagebox.showinfo("Success", f"Mod added successfully in {destination_folder} as pak01_dir.vpk")
        update_mod_lists()  # Refresh the mod list
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add mod: {e}")

# HTML parser for fetching mod names from workshop
class ModNameParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title_div = False
        self.mod_name = ""

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            for attr in attrs:
                if attr == ('class', 'workshopItemTitle'):
                    self.in_title_div = True

    def handle_endtag(self, tag):
        if tag == 'div' and self.in_title_div:
            self.in_title_div = False

    def handle_data(self, data):
        if self.in_title_div:
            self.mod_name = data.strip()

# Function to fetch workshop mods
def fetch_workshop_mods():
    if not os.path.exists(WORKSHOP_PATH):
        messagebox.showerror("Error", "Workshop folder not found.")
        return

    def fetch_mod_info(vpk_file):
        workshop_id = os.path.splitext(vpk_file)[0]
        url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                parser = ModNameParser()
                parser.feed(response.text)
                return parser.mod_name
            else:
                return None
        except Exception as e:
            print(f"Error fetching mod info for {vpk_file}: {e}")
            return None

    def fetch_mods():
        # Clear the listbox for workshop mods
        workshop_listbox.delete(0, tk.END)

        # List all VPK files in the workshop directory
        vpk_files = [f for f in os.listdir(WORKSHOP_PATH) if f.endswith('.vpk')]
        if not vpk_files:
            messagebox.showinfo("Info", "No mods found in the workshop folder.")
            return
        
        # Use ThreadPoolExecutor to fetch mod info concurrently
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(fetch_mod_info, vpk_files))

        for vpk_file, mod_name in zip(vpk_files, results):
            if mod_name:
                mod_name_filtered = re.sub(r'[^a-zA-Z0-9-_]', '', mod_name.replace(' ', '_'))
                workshop_listbox.insert(tk.END, mod_name_filtered)  # Only insert the name
                # Store the original VPK filename in the mapping
                mod_mapping[mod_name_filtered] = vpk_file
            else:
                messagebox.showwarning("Warning", f"Mod title not found for {vpk_file}.")

        messagebox.showinfo("Done", "Finished fetching workshop mods!")

    # Run the fetching in a separate thread
    threading.Thread(target=fetch_mods).start()

# Function to add selected workshop mods
def add_workshop_mod():
    selected_mods = workshop_listbox.curselection()

    added_count = 0  # Counter for successfully added mods

    for index in selected_mods:
        mod_name = workshop_listbox.get(index)
        # Get the original VPK filename from the mapping
        vpk_file_name = mod_mapping.get(mod_name)

        if vpk_file_name:
            destination_folder = os.path.join(USERMODS_PATH, mod_name)

            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)

            # Define the new path for the VPK file
            vpk_file_path = os.path.join(WORKSHOP_PATH, vpk_file_name)
            new_vpk_file_path = os.path.join(destination_folder, 'pak01_dir.vpk')

            try:
                shutil.copy(vpk_file_path, new_vpk_file_path)
                added_count += 1  # Increment the counter for each successful addition
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add workshop mod '{mod_name}': {e}")

    update_mod_lists()  # Refresh the mod list

# Function to rename a selected mod
def rename_mod():
    selected_enabled_mods = enabled_listbox.curselection()
    selected_disabled_mods = disabled_listbox.curselection()

    # Check if exactly one mod is selected
    if len(selected_enabled_mods) + len(selected_disabled_mods) != 1:
        messagebox.showwarning("Selection Error", "Please select exactly one mod to rename.")
        return

    # Determine which list the selected mod is in
    if selected_enabled_mods:
        current_listbox = enabled_listbox
    else:
        current_listbox = disabled_listbox

    # Get the current mod name
    current_mod_name = current_listbox.get(current_listbox.curselection())

    # Prompt for a new mod name
    while True:
        new_mod_name = simpledialog.askstring("Rename Mod", "Enter a new name for the mod:")
        
        if new_mod_name is None:  # User cancelled the input dialog
            return
        
        # Check if the new name is valid
        if re.match(r'^[\w-]+$', new_mod_name) and all(char not in new_mod_name for char in 'äöü'):
            break  # Valid name, exit the loop
        else:
            messagebox.showerror("Input Error", "Name contains invalid characters or spaces.")

    # Rename the mod folder
    old_mod_path = os.path.join(USERMODS_PATH, current_mod_name)
    new_mod_path = os.path.join(USERMODS_PATH, new_mod_name)

    try:
        os.rename(old_mod_path, new_mod_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to rename mod: {e}")
        return

    # Update gameinfo.txt if the mod is enabled
    if current_mod_name in enabled_listbox.get(0, tk.END):
        with open(GAMEINFO_PATH, 'r') as file:
            gameinfo_content = file.readlines()

        new_content = []
        for line in gameinfo_content:
            if line.strip().startswith(f'Game\t\t\t\tusermods\\{current_mod_name}'):
                line = line.replace(current_mod_name, new_mod_name)
            new_content.append(line)

        with open(GAMEINFO_PATH, 'w') as file:
            file.writelines(new_content)

    messagebox.showinfo("Success", f"Mod renamed successfully to '{new_mod_name}'!")
    update_mod_lists()  # Refresh the mod list

# Get the directory of the script or executable
dir_path = os.path.dirname(os.path.realpath(__file__))

# Construct the path to the icon file
icon_path = os.path.join(dir_path, 'icon.png')

# Create the main application window
root = tk.Tk()
root.title("L4D2 Mod Manager")
ico = Image.open(icon_path)
photo = ImageTk.PhotoImage(ico)
root.wm_iconphoto(False, photo)
root.geometry("730x350")
root.resizable(False, False)

# Label for Version
tk.Label(root, text="v0.0.1").place(x=690, y=330)

# Label for Enabled Mods
tk.Label(root, text="Enabled Mods").place(x=20, y=10)

# Listbox for Enabled Mods (supports multiple selection)
enabled_listbox = tk.Listbox(root, height=15, width=30, selectmode=tk.MULTIPLE, highlightthickness=0, bd=2, relief=tk.RIDGE)
enabled_listbox.place(x=20, y=40)

# Label for Disabled Mods
tk.Label(root, text="Disabled Mods").place(x=300, y=10)

# Listbox for Disabled Mods (supports multiple selection)
disabled_listbox = tk.Listbox(root, height=15, width=30, selectmode=tk.MULTIPLE, highlightthickness=0, bd=2, relief=tk.RIDGE)
disabled_listbox.place(x=300, y=40)

# Label for Workshop Mods
tk.Label(root, text="Workshop Mods").place(x=520, y=10)

# Listbox for Workshop Mods
workshop_listbox = tk.Listbox(root, height=15, width=30, selectmode=tk.MULTIPLE, highlightthickness=0, bd=2, relief=tk.RIDGE)
workshop_listbox.place(x=520, y=40)

# Button to fetch workshop mods
fetch_button = tk.Button(root, text="Fetch Mods", command=fetch_workshop_mods)
fetch_button.place(x=631, y=300)

# Button to add selected workshop mod
add_workshop_button = tk.Button(root, text="←", command=add_workshop_mod)
add_workshop_button.place(x=492, y=140)

# Button to move selected mods from Enabled to Disabled
disable_button = tk.Button(root, text="→", command=disable_mods)
disable_button.place(x=240, y=100)

# Button to move selected mods from Disabled to Enabled
enable_button = tk.Button(root, text="←", command=enable_mods)
enable_button.place(x=240, y=180)

# Button to apply the changes (modifying gameinfo.txt)
apply_button = tk.Button(root, text="Apply", command=apply_changes)
apply_button.place(x=221, y=300)

# Button to refresh the mod list
refresh_button = tk.Button(root, text="Refresh", command=refresh_mods)
refresh_button.place(x=20, y=300)

# Button to move selected mod up
up_button = tk.Button(root, text="↑", command=move_mod_up)
up_button.place(x=205, y=40)

# Button to move selected mod down
down_button = tk.Button(root, text="↓", command=move_mod_down)
down_button.place(x=205, y=258)

# Button to delete selected mods
delete_button = tk.Button(root, text="Delete", command=delete_selected_mods)
delete_button.place(x=75, y=300)

# Button to add a new mod
add_mod_button = tk.Button(root, text="Add", command=add_mod)
add_mod_button.place(x=124, y=300)  # Adjust the position as needed

# Button to rename selected mod
rename_button = tk.Button(root, text="Rename", command=rename_mod)
rename_button.place(x=162, y=300)

# Initial mod scan (on startup)
update_mod_lists()

# Start the GUI loop
root.mainloop()