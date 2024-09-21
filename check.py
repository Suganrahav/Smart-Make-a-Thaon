import csv
import math
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

# Haversine formula to calculate the distance between two coordinates
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return R * c  # Distance in kilometers

# Function to parse coordinates from the string format "(lat, lon)"
def parse_coordinates(coordinate_str):
    match = re.match(r"\(([^,]+), ([^,]+)\)", coordinate_str)
    if match:
        lat = float(match.group(1))
        lon = float(match.group(2))
        return lat, lon
    return None

# Function to read driver coordinates from coordinates.csv
def read_driver_coordinates_from_csv(filename):
    coordinates = []
    try:
        with open(filename, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:
                    driver_id = row[0].strip()
                    coordinate_str = row[1].strip('"').strip()
                    parsed_coordinates = parse_coordinates(coordinate_str)
                    if parsed_coordinates:
                        lat, lon = parsed_coordinates
                        coordinates.append((driver_id, lat, lon))
                        print(f"Driver ID: {driver_id}, Coordinates: {lat}, {lon}")
                    else:
                        print(f"Failed to parse coordinates: {row[1]}")
    except FileNotFoundError:
        print(f"{filename} not found.")
    return coordinates

# Function to read signal coordinates from signal_coor.csv
def read_signal_coordinates_from_csv(filename):
    coordinates = []
    try:
        with open(filename, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:
                    lat = float(row[0].strip())
                    lon = float(row[1].strip())
                    coordinates.append((lat, lon))
                    print(f"Signal Post Coordinates: {lat}, {lon}")
    except FileNotFoundError:
        print(f"{filename} not found.")
    return coordinates

# Write output to CSV file
def write_to_csv(signal_lat, signal_lon):
    with open('output.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([(signal_lat, signal_lon), 'high'])

# Check if any coordinate in driver_coordinates is within 1.5 km of any coordinate in signal_coor.csv
def check_distance():
    driver_coordinates = read_driver_coordinates_from_csv('coordinates.csv')
    signal_coordinates = read_signal_coordinates_from_csv('signal_coor.csv')

    if not driver_coordinates or not signal_coordinates:
        print("No coordinates found to compare.")
        return

    for driver_id, driver_lat, driver_lon in driver_coordinates:
        found_near_signal = False
        for signal_lat, signal_lon in signal_coordinates:
            distance = haversine(driver_lat, driver_lon, signal_lat, signal_lon)
            if distance < 1.5:
                print(f"Driver {driver_id}: high, Signal Coordinates: ({signal_lat}, {signal_lon})")
                write_to_csv(signal_lat, signal_lon)  # Write to CSV file
                found_near_signal = True
                break  # Stop checking further signals once a "high" is found

        if not found_near_signal:
            print(f"Driver {driver_id} is not close to any signal.")

# Watchdog event handler to monitor changes in coordinates.csv
class CSVChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith("coordinates.csv"):
            print("\ncoordinates.csv updated. Re-running check_distance()...\n")
            check_distance()

if __name__ == "__main__":
    # Initialize Watchdog observer to monitor changes in the directory
    event_handler = CSVChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=False)  # Monitor current directory

    observer.start()

    try:
        print("Monitoring coordinates.csv for changes...\n")
        check_distance()  # Run the function initially
        while True:
            time.sleep(1)  # Keep the script running
    except KeyboardInterrupt:
        observer.stop()  # Stop observer on interrupt
        print("Stopped monitoring.")
    
    observer.join()
