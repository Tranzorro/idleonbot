import sys
import io
import subprocess
import pyautogui
import time
import json
import os
import pkg_resources
from pathlib import Path
from pynput import keyboard
import tkinter as tk
from threading import Thread, Event
from PIL import Image, ImageTk

#this is the main script. it's simple. find matching images on screen, click it. rinse repeat.

CONFIG_FILE = 'config.json'

#initialize tkinter root window
root = tk.Tk()
#icon name variable
global icon_name, search_label, icon_label, tolerance_slider, config, duration_entry
# Get the directory where the script is located
script_dir = Path(__file__).resolve().parent

# Construct the path to the imagerefs directory
image_directory = 'imagerefs'

#path to icons
icon_directory = 'icons'

# Default duration for mouse hold
mouse_hold_duration = 5

# Event to control the running state of the script
stop_event = Event()

# Load icon images using pkg_resources
icon_images = {
    name: ImageTk.PhotoImage(Image.open(pkg_resources.resource_stream(__name__, f"{icon_directory}/{name}icon.png")))
    for name in ['BoO', 'TGMR', 'FR', 'SF', 'SFC', 'FC', 'FG', 'SFP', 'FM', 'GC', 'FishR', 'BFP', 'FD', 'FB', 'FI', 'MF', 'LQ', 'SL', 'QR', 'JW', 'TF', 'shinyfish']
}

# List of owl button images in order of priority
owl = [pkg_resources.resource_filename(__name__, f'{image_directory}/BoO.png'),
       pkg_resources.resource_filename(__name__, f'{image_directory}/TGMR.png'),
       pkg_resources.resource_filename(__name__, f'{image_directory}/FR.png'),
       pkg_resources.resource_filename(__name__, f'{image_directory}/SF.png'),
       pkg_resources.resource_filename(__name__, f'{image_directory}/SFC.png'),
       pkg_resources.resource_filename(__name__, f'{image_directory}/FC.png'),
       pkg_resources.resource_filename(__name__, f'{image_directory}/FG.png'),
       pkg_resources.resource_filename(__name__, f'{image_directory}/SFP.png'),
       pkg_resources.resource_filename(__name__, f'{image_directory}/FM.png')]

# List of fish button images in order of priority
fish = [pkg_resources.resource_filename(__name__, f'{image_directory}/GC.png'),
        pkg_resources.resource_filename(__name__, f'{image_directory}/FishR.png'),
        pkg_resources.resource_filename(__name__, f'{image_directory}/BFP.png'),
        pkg_resources.resource_filename(__name__, f'{image_directory}/FD.png'),
        pkg_resources.resource_filename(__name__, f'{image_directory}/FB.png'),
        pkg_resources.resource_filename(__name__, f'{image_directory}/FI.png'),
        pkg_resources.resource_filename(__name__, f'{image_directory}/MF.png'),
        pkg_resources.resource_filename(__name__, f'{image_directory}/LQ.png'),
        pkg_resources.resource_filename(__name__, f'{image_directory}/SL.png'),
        pkg_resources.resource_filename(__name__, f'{image_directory}/QR.png'),
        pkg_resources.resource_filename(__name__, f'{image_directory}/JW.png'),
        pkg_resources.resource_filename(__name__, f'{image_directory}/TF.png'),
        pkg_resources.resource_filename(__name__, f'{image_directory}/shinyfish.png')]

#map button modes to their respective lists
button_modes = {
    'owl': owl,
    'fish': fish
    }

#set button type to search for
button_mode = 'owl'

# Theme colors
theme_colors = [
    {
        'mode': 'owl',
        'bg': '#481E1D',
        'fg': 'white',
        'bbg': '#9C5B3D',
        'bghl': '#5C1B00',
        'fghl': 'lightgray'
    },
    {
        'mode': 'fish',
        'bg': '#000C27',
        'fg': 'white',
        'bbg': '#4B8397',
        'bghl': '#0B4357',
        'fghl': 'lightgray'
    }
]

# RGB color of lit-up buttons
lit_up_color = (156, 91, 61) if button_mode == 'owl' else (51,204,128)

# Flag to control the running state of the script
running = False

# Variable to track the visibility of the output text window
output_visible = False

# Variable to track the current screen for multimonitor support without scanning all screens
current_screen = 1

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    return {'owl': 30, 'fish': 90}  # Default values for both modes

def save_config(config):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file)
# Tolerance for color matching
config =  load_config()
color_tolerance = config.get(button_mode, 30 if button_mode == 'owl' else 90)  # Default to 90 if not set

# Function to check if the target pixel color is present in the image
def is_color_within_tolerance(pixel_color, target_color, tolerance):
    return all(abs(pixel_color[i] - target_color[i]) <= tolerance for i in range(3))

# Function to locate and click buttons
def locate_and_click_buttons():
    global running, mouse_hold_duration
    while not stop_event.is_set() and running:
        # Get the screen dimensions based on the current screen
        screen_width, screen_height = pyautogui.size()
        if current_screen == 1:
            window_region = (0, 0, screen_width, screen_height)
        else:
            # Assuming screen 2 is to the left of screen 1
            window_region = (-screen_width, 0, 0, screen_height)

        # Iterate over owl button images in priority order
        for button_image in button_modes[button_mode]:
            # Check if the stop condition is met
            if stop_event.is_set() or not running:
                break  # Exit the for loop immediately
            try:
                #update icon_name variable for tkinter window
                icon_name = Path(button_image).stem

                # Update the Tkinter label with the new icon
                if icon_name in icon_images:
                    icon_label.config(image=icon_images[icon_name])
                    icon_label.image = icon_images[icon_name]  # Keep a reference to avoid garbage collection

                # Locate the button within the window region
                button_location = pyautogui.locateCenterOnScreen(button_image, region=window_region, confidence= 0.9)
                
                if button_location:
                    print(f"Found {button_image} at {button_location}") #debug
                    # Check the color of the pixel at the button's center
                    pixel_color = pyautogui.pixel(button_location.x, button_location.y)
                    print(f"pixel color of {button_location} is {pixel_color}")

                    if button_image == 'shinyfish':
                        # Simulate a 5-second mouse hold
                        pyautogui.click(button_location)
                        print(f"Clicked {button_image} at {button_location}")
                    if is_color_within_tolerance(pixel_color, lit_up_color, color_tolerance):
                        # Click the button if the color matches the lit-up color
                        # Simulate a 5-second mouse hold
                        pyautogui.mouseDown(button_location)
                        time.sleep(mouse_hold_duration)  # Hold the mouse button down for 5 seconds
                        pyautogui.mouseUp(button_location)
                        print(f"Clicked {button_image} at {button_location}")
                        break
                    #else: #use this else for testing. otherwise, keep it commented out.
                        #print(f"{button_image} is not lit up (color: {pixel_color}).")
            except Exception as e:
                print(f"could not find {button_image}: {e}")#this will print even when buttons are unclickable.
    # Re-enable the start button
    start_button.config(state=tk.NORMAL)
    running = False

# Function to start the script
def start_script():
    global running
    if not running:
        running = True
        print("Starting script.")
        # Disable the start button
        start_button.config(state=tk.DISABLED)
        # show the search label
        search_label.grid(row=1,column=0, padx=120, pady=10, sticky='w')
        icon_label.grid(row=1, column=0, padx=(240,0), pady=10, sticky='w')
        # Clear the stop event
        stop_event.clear()
        # Run the locate_and_click_buttons function in a separate thread
        Thread(target=locate_and_click_buttons).start()

# Function to stop the script
def stop_script():
    global running
    if running:
        print("Stopping script.")
        # Set the stop event to signal the thread to stop
        stop_event.set()
        # Wait for the thread to finish
        while running:
            root.update()  # Keep the GUI responsive
        # Re-enable the start button
        start_button.config(state=tk.NORMAL)
        #hide search label
        search_label.grid_forget()
        icon_label.grid_forget()
        running = False
    else:
        print("already stopped.")

#restart script

def restart_script():
    stop_script()
    time.sleep(0.5)
    start_script()

# Function to toggle between screens
def toggle_screen(toggle_button):
    global current_screen
    current_screen = 2 if current_screen == 1 else 1
    #update button text upon press.
    toggle_button.config(text=f"Screen: {current_screen}")
    print(f"Toggled to screen {current_screen}")

def toggle_search(toggle_button):
    global button_mode, icon_name, color_tolerance, tolerance_slider, config
    # Toggle the button mode
    button_mode = 'fish' if button_mode == 'owl' else 'owl'
    icon_name = 'TF' if button_mode == 'fish' else 'FG'

    # Load the tolerance for the new mode
    color_tolerance = config.get(button_mode, 30 if button_mode == 'owl' else 90)
    tolerance_slider.set(color_tolerance)

    # Update the icon label with the new icon
    if icon_name in icon_images:
        icon_label.config(image=icon_images[icon_name])
        icon_label.image = icon_images[icon_name]  # Keep a reference to avoid garbage collection

    # Update button text upon press
    toggle_button.config(text=f"Search: {button_mode}")
    print(f"Toggled to {button_mode}")
    icon_label.grid(row=1, column=0, padx=(240,0), pady=10, sticky='w')
    print(f"set color_tolerance to {color_tolerance}")
    set_theme()
    if running:
        icon_label.grid_forget()
        restart_script()

# Function to toggle the output text window
def toggle_output(toggle_button):
    global output_visible
    output_visible = not output_visible
    
    # Get the current position of the window
    current_x = root.winfo_x() - 2 # offset by pixel amount to avoid traveling window.
    current_y = root.winfo_y() - 36

    # Set a fixed position
    fixed_x = current_x
    fixed_y = current_y
    
    if output_visible:
        output_text.grid(row=3, column=0, columnspan=4, padx=50, pady=0, sticky='nsew')
        new_height = 340
        new_width = 500
    else:
        output_text.grid_forget()
        new_height = 150
        new_width = 500

    # Set the new size and fixed position
    root.geometry(f"{new_width}x{new_height}+{fixed_x}+{fixed_y}")

    toggle_button.config(text=f"debug: {'On' if output_visible else 'Off'}")

# Listener for keyboard events
def on_press(key):
    try:
        if key.char == 'a':
            start_script()
        elif key.char == 's':
            stop_script()
    except AttributeError:
        pass

# Redirect print statements to the Tkinter Text widget
class RedirectText(io.StringIO):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def write(self, s):
        self.text_widget.insert(tk.END, s)
        self.text_widget.see(tk.END)

# Function to set the theme based on the current mode
def set_theme():
    bg_color, fg_color, bbg_color, active_bg_color, active_fg_color = get_theme_colors(button_mode)
    root.configure(bg=bg_color)
    
    # Function to apply theme to a widget if applicable
    def apply_theme(widget):
        try:
            if isinstance(widget, tk.Button):
                widget.configure(bg=bbg_color, fg=fg_color, activebackground=active_bg_color, activeforeground=active_fg_color)
            else:
                widget.configure(bg=bg_color, fg=fg_color)
        except tk.TclError:
            pass  # Ignore widgets that don't support bg/fg configuration

    # Update all widgets with the new theme colors
    def update_widgets(container):
        for widget in container.winfo_children():
            apply_theme(widget)
            # If the widget is a container, update its children as well
            if isinstance(widget, (tk.Frame, tk.LabelFrame, tk.PanedWindow, tk.Toplevel)):
                widget.configure(bg=bg_color)  # Ensure frame itself is updated
                update_widgets(widget)

    # Start updating from the root window
    update_widgets(root)

def update_tolerance(val):
    global color_tolerance, config
    color_tolerance = int(val)
    print(f"accuracy of pixel color: {color_tolerance}")
    # Save the updated color_tolerance to the config file
    config[button_mode] = color_tolerance
    save_config(config)

def update_duration():
    global mouse_hold_duration
    try:
        # Get the duration from the entry widget and convert it to an integer
        mouse_hold_duration = int(duration_entry.get())
        print(f"Mouse hold duration set to: {mouse_hold_duration} seconds")
    except ValueError:
        print("Invalid input for duration. Please enter an integer.")

# Function to get theme colors based on the current mode
def get_theme_colors(mode):
    try:
        for theme in theme_colors:
            if theme['mode'] == mode:
                return theme['bg'], theme['fg'], theme['bbg'], theme['bghl'], theme['fghl']
        return 'lightgray', 'black', ' lightgray','darkgray', 'white'  # Default colors if mode not found
    except Exception as e:
        # Handle the exception and return default colors
        print(f"An error occurred: {e}")
        return 'lightgray', 'black', 'lightgray','darkgray', 'white'


# Create the Tkinter GUI
def create_gui():
    global start_button, icon_label, icon_name, search_label, tolerance_slider, duration_entry
    root.title("IdleOn Button Clicker")
    root.resizable(False, False)  # Make the window non-resizable
    root.geometry("500x150")
    # Frame for buttons
    button_frame = tk.Frame(root)
    button_frame.grid(row=0, column=0, columnspan=4, pady=5, sticky='w')  # Align to the left

    start_button = tk.Button(button_frame, text="Start (a)", command=start_script,highlightthickness=0 )
    start_button.grid(row=0, column=0, padx=20)
    stop_button = tk.Button(button_frame, text="Stop (s)", command=stop_script,highlightthickness=0 )
    stop_button.grid(row=0, column=1, padx=20)
    toggle_button = tk.Button(button_frame, text=f"Screen: {current_screen}", command=lambda: toggle_screen(toggle_button),highlightthickness=0 )
    toggle_button.grid(row=0, column=2, padx=20)
    search_toggle_button = tk.Button(button_frame, text=f"search: {button_mode}", command=lambda: toggle_search(search_toggle_button),highlightthickness=0 )
    search_toggle_button.grid(row=0, column=3, padx=20)

    # Frame for the output toggle button
    output_button_frame = tk.Frame(root)
    output_button_frame.grid(row=1, column=0, sticky='w', pady=5)
    output_toggle_button = tk.Button(output_button_frame, text="debug: Off", command=lambda: toggle_output(output_toggle_button),highlightthickness=0 )
    output_toggle_button.grid(row=1, column=0, padx=20, pady=15)

   # Label to display the current icon
    icon_label = tk.Label(root, width=100, height=50)
    icon_label.grid(row=1, column=0, padx=(240, 0), pady=10, sticky='w')  # Add icon_label to the grid initially
    icon_name = 'FG'
    if icon_name in icon_images:
        icon_label.config(image=icon_images[icon_name])
        icon_label.image = icon_images[icon_name]  # Keep a reference to avoid garbage collection

    # Label to display the "searching for..." text
    search_label = tk.Label(root, text="Searching for...", font=("Arial", 12))

    # Create a Scale widget (slider)
    tolerance_slider = tk.Scale(root,from_=1, to=100, orient='horizontal', label='accuracy', command=update_tolerance)

    # Set the initial position of the slider
    tolerance_slider.set(color_tolerance)

    # Pack the slider into the window
    tolerance_slider.grid(row=1, column=0, padx=(370,0), pady=0, sticky='w')

    # Create a validation command inline, this limits the int value to max of 2 digits.
    vcmd = (root.register(lambda P: P.isdigit() and len(P) <= 2 or P == ""), '%P')

    # Entry for mouse hold duration
    duration_label = tk.Label(root, text="Mouse wait/s:")
    duration_label.grid(row=2, column=0, padx=(170,0), pady=5, sticky='w')
    duration_entry = tk.Entry(root, width=2, validate='key', validatecommand=vcmd)
    duration_entry.grid(row=2, column=0, padx=(280,0), pady=5, sticky='w')
    duration_entry.insert(0, str(mouse_hold_duration))  # Set default value
    duration_entry.bind("<Return>", lambda event: update_duration())  # Update duration on Enter key press
    # Bind the <FocusOut> event to update the duration when the entry loses focus
    duration_entry.bind("<FocusOut>", lambda event: update_duration())
    # Bind a click event to the root window to set focus away from the entry only if clicking on the root window
    root.bind("<Button-1>", lambda event: root.focus_set() if event.widget == root else None)

    # Force an update to ensure proper layout
    root.update()

    # Start the keyboard listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    global output_text
    output_text = tk.Text(root, wrap='word', height=10, width=50)
    sys.stdout = RedirectText(output_text)

    set_theme()
    root.mainloop()

if __name__ == "__main__":
    create_gui()
