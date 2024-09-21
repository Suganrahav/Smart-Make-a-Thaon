import csv
import geocoder
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, RoundedRectangle

# Set window size for better visualization (Optional)
Window.size = (400, 600)

# Function to check if the driver ID exists in emergency.csv
def check_driver_id(driver_id):
    try:
        with open('emergency.csv', mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row and driver_id == row[1]:  # Check if driver_id matches the ID in the 2nd column
                    return True
    except FileNotFoundError:
        print("emergency.csv not found.")
    return False

# Function to append coordinates to coordinates.csv
def update_coordinates_in_csv(driver_id, live_coordinates):
    data = []
    try:
        with open('coordinates.csv', mode='r') as file:
            reader = csv.reader(file)
            data = list(reader)
    except FileNotFoundError:
        pass  # If file does not exist, we'll create it later

    # Update or add the driver's coordinates
    updated = False
    with open('coordinates.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        for row in data:
            if row and row[0] == driver_id:
                writer.writerow([driver_id, live_coordinates])  # Update coordinates for existing driver
                updated = True
            else:
                writer.writerow(row)
        if not updated:
            writer.writerow([driver_id, live_coordinates])  # Add new entry for new driver

# Function to write emergency form data to a CSV file
def write_emergency_to_csv(emergency_level, driver_id):
    with open('emergency.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([emergency_level, driver_id])

# Function to get real GPS coordinates
def get_live_coordinates():
    g = geocoder.ip('me')  # Get location based on IP (suitable for demo purposes)
    lat, lon = g.latlng
    if lat is None or lon is None:
        return "Location not available"
    
    return lat, lon

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        layout = FloatLayout(size=Window.size)

        # Create Driver Login Button
        driver_button = Button(text="Driver Login", size_hint=(0.8, None), height=50, pos_hint={'center_x': 0.5, 'center_y': 0.6})
        driver_button.bind(on_press=self.go_to_driver_login)
        layout.add_widget(driver_button)

        # Create Hospital Login Button
        hospital_button = Button(text="Hospital Login", size_hint=(0.8, None), height=50, pos_hint={'center_x': 0.5, 'center_y': 0.5})
        hospital_button.bind(on_press=self.go_to_hospital_login)
        layout.add_widget(hospital_button)

        self.add_widget(layout)

    def go_to_driver_login(self, instance):
        self.manager.current = 'driver'

    def go_to_hospital_login(self, instance):
        self.manager.current = 'hospital'

class DriverLoginScreen(Screen):
    def __init__(self, **kwargs):
        super(DriverLoginScreen, self).__init__(**kwargs)
        layout = FloatLayout(size=Window.size)

        # Label
        label = Label(text="Driver Login Page", font_size=24, size_hint=(0.8, None), height=50, pos_hint={'center_x': 0.5, 'center_y': 0.8})
        layout.add_widget(label)

        # Driver ID Input
        self.driver_id_input = TextInput(hint_text='Enter Driver ID', multiline=False, size_hint=(0.8, None), height=40, pos_hint={'center_x': 0.5, 'center_y': 0.65})
        layout.add_widget(self.driver_id_input)

        # Connect to TraffXpert Button
        self.connect_button = Button(text="Connect to TraffXpert", size_hint=(0.8, None), height=50, pos_hint={'center_x': 0.5, 'center_y': 0.55})
        self.connect_button.bind(on_press=self.check_driver_and_connect)
        layout.add_widget(self.connect_button)

        # Back Button
        back_button = Button(text="Back", size_hint=(0.8, None), height=50, pos_hint={'center_x': 0.5, 'center_y': 0.4})
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def check_driver_and_connect(self, instance):
        driver_id = self.driver_id_input.text  # Get entered Driver ID

        if check_driver_id(driver_id):
            self.start_tracking(driver_id)  # Proceed if valid driver ID
        else:
            self.show_invalid_popup()  # Show error if invalid

    def start_tracking(self, driver_id):
        Clock.schedule_interval(lambda dt: self.update_location(driver_id), 1)
        print("Driver ID valid. Tracking started...")

    def update_location(self, driver_id):
        live_coordinates = get_live_coordinates()  # Get real GPS coordinates
        print(f"Updating coordinates for {driver_id}: {live_coordinates}")
        update_coordinates_in_csv(driver_id, live_coordinates)  # Save coordinates to CSV

    def show_invalid_popup(self):
        popup = Popup(title='Error',
                      content=Label(text='Invalid Driver ID!', color=(1, 0, 0, 1)),
                      size_hint=(0.6, 0.4))
        popup.open()

    def go_back(self, instance):
        self.manager.current = 'main'

class HospitalLoginScreen(Screen):
    def __init__(self, **kwargs):
        super(HospitalLoginScreen, self).__init__(**kwargs)
        layout = FloatLayout(size=Window.size)

        # Label
        label = Label(text="Hospital Login Page", font_size=24, size_hint=(0.8, None), height=50, pos_hint={'center_x': 0.5, 'center_y': 0.8})
        layout.add_widget(label)

        # Subscribe Button
        subscribe_button = Button(text="Subscribe", size_hint=(0.8, None), height=50, pos_hint={'center_x': 0.5, 'center_y': 0.6})
        subscribe_button.bind(on_press=self.open_subscribe_form)  # Bind the button to the function
        layout.add_widget(subscribe_button)

        # Emergency Button
        emergency_button = Button(text="Emergency", size_hint=(0.8, None), height=50, pos_hint={'center_x': 0.5, 'center_y': 0.5})
        emergency_button.bind(on_press=self.open_emergency_form)
        layout.add_widget(emergency_button)

        # Back Button
        back_button = Button(text="Back", size_hint=(0.8, None), height=50, pos_hint={'center_x': 0.5, 'center_y': 0.4})
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def open_subscribe_form(self, instance):
        form_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.new_driver_id_input = TextInput(hint_text='New Driver ID', multiline=False, size_hint=(1, None), height=40)
        form_layout.add_widget(self.new_driver_id_input)

        submit_button = Button(text='Subscribe', size_hint=(1, None), height=50)
        submit_button.bind(on_press=self.submit_new_driver)
        form_layout.add_widget(submit_button)

        self.popup = Popup(title='Subscribe New Driver', content=form_layout, size_hint=(0.7, 0.7))
        self.popup.open()

    def submit_new_driver(self, instance):
        new_driver_id = self.new_driver_id_input.text.strip()
        if not new_driver_id:
            error_popup = Popup(title="Error",
                                content=Label(text="Please enter a valid Driver ID."),
                                size_hint=(0.6, 0.4))
            error_popup.open()
            return

        # Assuming a default emergency level of 'Low' for new subscriptions
        emergency_level = 'Low'
        write_emergency_to_csv(emergency_level, new_driver_id)
        self.popup.dismiss()

        confirmation_popup = Popup(title='Success',
                                   content=Label(text=f'Driver {new_driver_id} subscribed successfully!'),
                                   size_hint=(0.6, 0.4))
        confirmation_popup.open()

    def open_emergency_form(self, instance):
        form_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.emergency_spinner = Spinner(
            text='Select Priority',
            values=('High', 'Medium', 'Low'),
            size_hint=(1, None),
            height=44
        )
        form_layout.add_widget(self.emergency_spinner)

        self.driver_id_input = TextInput(hint_text='Driver Unique ID', multiline=False, size_hint=(1, None), height=40)
        form_layout.add_widget(self.driver_id_input)

        submit_button = Button(text='Submit', size_hint=(1, None), height=50)
        submit_button.bind(on_press=self.submit_emergency_form)
        form_layout.add_widget(submit_button)

        self.popup = Popup(title='Emergency Form', content=form_layout, size_hint=(0.7, 0.7))
        self.popup.open()

    def submit_emergency_form(self, instance):
        emergency_level = self.emergency_spinner.text
        driver_id = self.driver_id_input.text

        write_emergency_to_csv(emergency_level, driver_id)

        self.popup.dismiss()

    def go_back(self, instance):
        self.manager.current = 'main'

class LoginApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(DriverLoginScreen(name='driver'))
        sm.add_widget(HospitalLoginScreen(name='hospital'))
        return sm

if __name__ == '__main__':
    LoginApp().run()
