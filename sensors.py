import RPi.GPIO as GPIO
import time
import Adafruit_DHT
import spidev
import serial
#import mysql.connector
import folium
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from mq import *
import sys, time
from folium import plugins
from folium.plugins import HeatMap
import csv
import pandas as pd
from itertools import zip_longest

# Connect to the database
#mydb = mysql.connector.connect(
#  host="localhost",
#  user="joaoclaro",
#  password="joaoclaro",
#  database="sensordata"
#)

# Get a cursor object
#mycursor = mydb.cursor()

distance_interval = 10  # Interval for distance measurements in seconds
sensor_data_interval = 60  # Interval for sensor data collection in seconds
distance_timer = time.time()  # Timer for distance measurements
sensor_data_timer = time.time()  # Timer for sensor data collection

# Create empty lists for storing data
timestamps = []
temperatures = []
humidities = []
distances1 = []
distances2 = []
distances3 = []
lpg_values = []
smoke_values = [] 
co_values = []
gps_latitudes = []
gps_longitudes = []
gps_speeds = []
datetimes = []
timestamp_list = []
latitude_list = []
longitude_list = []
marker_locations = []
temperature_list = []
humidity_list = []
smoke_list = []
co_list = []
lpg_list = []
dist1_list = []
dist2_list = []
dist3_list = []

# Set GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Define GPIO pins for each sensor
TRIG1 = 12
ECHO1 = 6
TRIG2 = 13
ECHO2 = 26
TRIG3 = 25
ECHO3 = 24
DHT_PIN = 5
#LED_PIN1 = 15
#LED_PIN2 = 16 
# Set up GPIO pins as output (for trigger) or input (for echo)
GPIO.setup(TRIG1, GPIO.OUT)
GPIO.setup(ECHO1, GPIO.IN)
GPIO.setup(TRIG2, GPIO.OUT)
GPIO.setup(ECHO2, GPIO.IN)
GPIO.setup(TRIG3, GPIO.OUT)
GPIO.setup(ECHO3, GPIO.IN)
#GPIO.setup(LED_PIN1, GPIO.OUT)
#GPIO.setup(LED_PIN2, GPIO.OUT)

# Define safety distance in centimeters
#SAFETY_DISTANCE = 30

#Define warning distance in centimeters
#WARNING_DISTANCE = 50


# Open serial port
ser = serial.Serial('/dev/serial0', baudrate=9600, timeout=1)

# Enable GNSS module
ser.write(b'AT+CGNSPWR=1\r\n')
time.sleep(1)

def calculate_aqi(concentration):
    breakpoints = [0, 51, 101, 151, 201, 301, 401, 501]
    index = 0
    
    while index < len(breakpoints) - 1 and concentration > breakpoints[index + 1]:
        index += 1

    c_low = breakpoints[index]
    c_high = breakpoints[index + 1]
    i_low = index * 50
    i_high = (index + 1) * 50

    aqi = ((i_high - i_low) / (c_high - c_low)) * (concentration - c_low) + i_low
    return int(aqi)

def get_classification(aqi):
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    elif aqi <= 200:
        return "Unhealthy"
    elif aqi <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"


# Initialize DHT11 sensor
DHT_SENSOR = Adafruit_DHT.DHT11


# Function to measure distance using ultrasonic sensor
def measure_distance(trig_pin, echo_pin):
    # Send a 10us pulse to trigger pin to start measurement
    GPIO.output(trig_pin, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(trig_pin, GPIO.LOW)

    # Wait for echo pin to go high and start timing
    while GPIO.input(echo_pin) == GPIO.LOW:
        start_time = time.time()

    # Wait for echo pin to go low and stop timing
    while GPIO.input(echo_pin) == GPIO.HIGH:
        end_time = time.time()

    # Calculate distance using speed of sound and time taken
    duration = end_time - start_time
    distance = duration * 34300 / 2

    return distance

#Function to get GPS information
def get_coordinates(ser):

    # Request location information
    ser.write(b'AT+CGNSINF\r\n')
    time.sleep(1)

    # Read response from module
    response = ser.read_all().decode('utf-8')
        
    # Split the response string into an array of values
    values = response.split(',')

    if values[3] != '' or values[4] != '':
        #timestamp = float(values[1])
        timestamp2 = time.time
        latitude = float(values[3])
        longitude = float(values[4])
        speed = float(values[7])
            
        # Print the retrieved values
        print(f"Timestamp: {timestamp2}")
        print(f"Latitude: {latitude}")
        print(f"Longitude: {longitude}")
        print(f"Speed: {speed}")

        gps_latitudes.append(latitude)
        gps_longitudes.append(longitude)
        gps_speeds.append(speed)
            
    else:
        gps_latitudes.append("")
        gps_longitudes.append("")
        gps_speeds.append("")


try:
    counter = 0
    safety_count = 0
    warning_count = 0
    timestamp = datetime.now().strftime("%H:%M:%S")
    current_time = datetime.now().strftime("%H:%M:%S")
    print(current_time)
    timestamps.append(current_time)

    while True:

        # Request location information
        #ser.write(b'AT+CGNSINF\r\n')
        #time.sleep(1)

        # Read response from module
        #response = ser.read_all().decode('utf-8')
        
        # Split the response string into an array of values
        #values = response.split(',')

        if time.time() - distance_timer >= 10:
           # Get the current time
            #timestamp = datetime.now().strftime("%H:%M:%S")
            #current_time = datetime.now().strftime("%H:%M:%S")
            #print(current_time)
            #timestamps.append(current_time)

            #if values[3] != '' or values[4] != '':
                #timestamp = float(values[1])
                #timestamp2 = time.time
                #latitude = float(values[3])
                #longitude = float(values[4])
                #speed = float(values[7])
            
                # Print the retrieved values
                #print(f"Timestamp: {timestamp2}")
                #print(f"Latitude: {latitude}")
                #print(f"Longitude: {longitude}")
                #print(f"Speed: {speed}")

                #gps_latitudes.append(latitude)
                #gps_longitudes.append(longitude)
                #gps_speeds.append(speed)
            
            #else:
                #gps_latitudes.append("")
                #gps_longitudes.append("")
                #gps_speeds.append("")

                # Create a folium map object
                #my_map = folium.Map(location=[gps_latitudes[0], gps_longitudes[0]], zoom_start=12)

          
                # Add a marker for each coordinate on the map
                #for lat, lon in zip(gps_latitudes, gps_longitudes):
                    #folium.Marker(location=[lat, lon]).add_to(my_map)
            
        #Measure distances every 15 seconds
        #if counter % 3 == 0:
            # Measure distance from sensor 1
            dist1 = measure_distance(TRIG1, ECHO1)
            print("Distance from sensor 1: %.1f cm" % dist1)
            dist1 = round(dist1, 2)
            #distances1.append(dist1)

            # Measure distance from sensor 2
            dist2 = measure_distance(TRIG2, ECHO2)
            print("Distance from sensor 2: %.1f cm" % dist2)
            dist2 = round(dist2, 2)
            #distances2.append(dist2)


            # Measure distance from sensor 3
            dist3 = measure_distance(TRIG3, ECHO3)
            print("Distance from sensor 3: %.1f cm" % dist3)
            dist3 = round(dist3, 2)
            #distances3.append(dist3)

            #If any of the measured distances are smaller than the safety distance than save those distances and collect the corresponding coordinates
            if dist1 < 50 or dist2 < 50 or dist3 < 50:
                distances1.append(dist1)
                distances2.append(dist2)
                distances3.append(dist3)
                get_coordinates(ser)
                humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
                temperatures.append(temperature)
                current_time = datetime.now().strftime("%H:%M:%S")
                print(current_time)
                timestamps.append(current_time)


            
            distance_timer = time.time()
            

            #if distance_1 < SAFETY_DISTANCE or distance_2 < SAFETY_DISTANCE or distance_3 < SAFETY_DISTANCE:
               #consecutive_count += 1
            #else:
               #consecutive_count = 0

            # Turn on LED if three consecutive distances are smaller than safety distance
            #if consecutive_count == 3:
               #GPIO.output(LED_PIN1, GPIO.HIGH)
            #else:
               #GPIO.output(LED_PIN1, GPIO.LOW)
            
            #Collect GPS information, humidity, temperature and air quality levels every 60 seconds.
            if time.time() - sensor_data_timer >= 60: 

                #Collect GPS information
                get_coordinates(ser)

                current_time = datetime.now().strftime("%H:%M:%S")
                print(current_time)
                timestamps.append(current_time)


                # Measure humidity, temperature, air quality, and GPS every minute
                # Attempt to get a sensor reading
                humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)


                # If a valid reading was obtained, print it
                if humidity is not None and temperature is not None:    
                    print(f"Temperature: {temperature:.2f} °C")
                    print(f"Humidity: {humidity:.2f}%")
                    temperatures.append(temperature)
                    humidities.append(humidity)
                else:
                    print("Failed to retrieve data from DHT sensor")


                #Collect data from MQ-135 sensor
                mq = MQ();
                perc = mq.MQPercentage()
                sys.stdout.write("\r")
                sys.stdout.write("\033[K")
                sys.stdout.write("LPG: %g ppm, CO: %g ppm, Smoke: %g ppm\n" % (perc["GAS_LPG"], perc["CO"], perc["SMOKE"]))
                sys.stdout.flush()
                time.sleep(0.1)
                lpg_values.append(perc["GAS_LPG"])
                co_values.append(perc["CO"])
                smoke_values.append(perc["SMOKE"])


                # Calculate AQI based on the concentrations
                lpg_aqi = calculate_aqi(perc["GAS_LPG"])
                co_aqi = calculate_aqi(perc["CO"])
                smoke_aqi = calculate_aqi(perc["SMOKE"])
            
                print(f"LPG AQI: {lpg_aqi} - {get_classification(lpg_aqi)}")
                print(f"CO AQI: {co_aqi} - {get_classification(co_aqi)}")
                print(f"Smoke AQI: {smoke_aqi} - {get_classification(smoke_aqi)}")


        # Insert data into the database
        #sql = "INSERT INTO data (timestamp, temperature, humidity, distance1, distance2, distance3, aqi, concentration, gps_latitude, gps_longitude, gps_speed) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        #val = (timestamp, temperature, humidity, dist1, dist2, dist3, aqi, concentration, gps_latitude, gps_longitude, gps_speed)
        #mycursor.execute(sql, val)
        #mydb.commit()

        # Append data to respective lists
        #timestamps.append(timestamp)
        #temperatures.append(temperature)
        #humidities.append(humidity)
        #distances1.append(dist1)
        #distances2.append(dist2)
        #distances3.append(dist3)
        #lpg_values.append(perc["GAS_LPG"])
        #co_values.append(perc["CO"])
        #smoke_values.append(perc["SMOKE"])


        #gps_latitudes.append(gps_latitude)
        #gps_longitudes.append(gps_longitude)
        #gps_speeds.append(gps_speed)
        
        # Define the file path
        #file_path = timestamps[0] + ".csv"

        # Open the file in write mode
        #with open(file_path, mode='w', newline='') as file:
            # Create a CSV writer object
            #writer = csv.writer(file)

            #writer.writerow(["Timestamp","Latitude", "Longitude","Distance1", "Distance2", "Distance3", "Temperature","Humidity","Smoke Concentration", "LPG Concentration", "CO Concentration"])        # Combine the lists into a single list of rows
            #rows = zip(timestamps, gps_latitudes, gps_longitudes, distances1, distances2, distances3, temperatures, humidities, smoke_values, lpg_values, co_values)
            # Write the rows to the file
            #writer.writerows(rows)

          

        # Define the distances file path
        distances_file = timestamps[0] + "_distances" + ".csv"

        # Open the file in write mode
        with open(distances_file, mode='w', newline='') as file_distance:
            # Create a CSV writer object
            writer = csv.writer(file_distance)

            writer.writerow(["Timestamp","Latitude", "Longitude","Distance1", "Distance2", "Distance3", "Temperature"])
            rows = zip(timestamps, gps_latitudes, gps_longitudes, distances1, distances2, distances3, temperatures)
            #Write the rows to the file
            writer.writerows(rows)

        # Define the air quality file path
        environment_file = timestamps[0] + "_environmental" + ".csv"

        # Open the file in write mode
        with open(environment_file, mode='w', newline='') as file_environment:
            # Create a CSV writer object
            writer = csv.writer(file_environment)

            writer.writerow(["Timestamp","Latitude", "Longitude", "Temperature","Humidity","Smoke Concentration", "LPG Concentration", "CO Concentration"])        # Combine the lists into a single list of rows
            rows2 = zip(timestamps, gps_latitudes, gps_longitudes, temperatures, humidities, smoke_values, lpg_values, co_values)
            # Write the rows to the file
            writer.writerows(rows2)

        # Wait for 5 seconds before next iteration
        time.sleep(5)
        counter += 1


except KeyboardInterrupt:

    print('Program stopped') # User interrupted the program
  

    print(f"Timestamps: {timestamps}")
    print(f"Distances1: {distances1}")
    print(f"Distances2: {distances2}")
    print(f"Distances3: {distances3}")
    print(f"GPS Latitudes: {gps_latitudes}")
    print(f"GPS Longitudes: {gps_longitudes}")
    print(f"Temperatures: {temperatures}")

    # Define the distances file path
    distances_file = timestamps[0] + "_distances" + ".csv"

    # Open the file in write mode
    with open(distances_file, mode='w', newline='') as file_distance:
        # Create a CSV writer object
        writer = csv.writer(file_distance)

        writer.writerow(["Timestamp","Latitude", "Longitude","Distance1", "Distance2", "Distance3", "Temperature"])
        rows = zip(timestamps, gps_latitudes, gps_longitudes, distances1, distances2, distances3, temperatures)
        #Write the rows to the file
        writer.writerows(rows)

    # Define the air quality file path
    environment_file = timestamps[0] + "_environmental" + ".csv"

    # Open the file in write mode
    with open(environment_file, mode='w', newline='') as file_environment:
        # Create a CSV writer object
        writer = csv.writer(file_environment)

        writer.writerow(["Timestamp","Latitude", "Longitude", "Temperature","Humidity","Smoke Concentration", "LPG Concentration", "CO Concentration"])        # Combine the lists into a s>
        rows2 = zip(timestamps, gps_latitudes, gps_longitudes, temperatures, humidities, smoke_values, lpg_values, co_values)
        # Write the rows to the file
        writer.writerows(rows2)



    # Read the CSV file
    data = pd.read_csv(distances_file)

    # Filter out rows with missing coordinates and temperatures
    valid_data = data.dropna(subset=['Latitude', 'Longitude', 'Temperature'])

    # Check if there are valid coordinates and temperatures
    if len(valid_data) > 0:
        # Extract latitude, longitude, distance, and temperature columns
        latitudes = valid_data['Latitude']
        longitudes = valid_data['Longitude']
        distances1 = valid_data['Distance1']
        distances2 = valid_data['Distance2']
        distances3 = valid_data['Distance3']
        temperatures = valid_data['Temperature']

        # Create a map centered at the first valid latitude and longitude
        map_center = [latitudes.iloc[0], longitudes.iloc[0]]
        distance_map = folium.Map(location=map_center, zoom_start=12)

        # Create a heatmap layer based on the temperature values
        heat_data = list(zip(latitudes, longitudes, temperatures))
        HeatMap(heat_data, radius=15).add_to(distance_map)

        # Create a map with just the line
        path_map = folium.Map(location=[latitudes.iloc[0], longitudes.iloc[0]], zoom_start=12)
        path_coords = list(zip(latitudes, longitudes))
        folium.PolyLine(locations=path_coords, color='blue').add_to(path_map)
        path_map.save('path_map.html')


        # Iterate over the data and add markers with popups to the map
        for lat, lon, dist1, dist2, dist3, temp in zip(latitudes, longitudes, distances1, distances2, distances3, temperatures):
            if pd.notnull(lat) and pd.notnull(lon):
                popup_text = f"Distance 1: {dist1}<br>Distance 2: {dist2}<br>Distance 3: {dist3}<br>Temperature: {temp}"
                folium.Marker(location=[lat, lon], popup=popup_text).add_to(distance_map)

        # Save the map as an HTML file
        distance_map.save('map.html')

    else:
        print("No valid coordinates found in the file.")



    # Read the CSV file
    data2 = pd.read_csv(environment_file)

    # Filter out rows with missing coordinates
    valid_data2 = data2.dropna(subset=['Latitude', 'Longitude'])

    # Check if there are valid coordinates
    if len(valid_data2) > 0:
        # Extract latitude and longitude columns
        latitudes2 = valid_data2['Latitude']
        longitudes2 = valid_data2['Longitude']

        # Create a map centered at the first valid latitude and longitude
        map_center = [latitudes2.iloc[0], longitudes2.iloc[0]]
        marker_map = folium.Map(location=map_center, zoom_start=12)

        # Iterate over the data and add markers with popups to the map
        for lat, lon, timestamp, temperature, humidity, smoke, lpg, co in zip(valid_data2['Latitude'], valid_data2['Longitude'], valid_data2['Timestamp'], valid_data2['Temperature'], valid_data2['Humidity'], valid_data2['Smoke Concentration'], valid_data2['LPG Concentration'], valid_data2['CO Concentration']):
            if not pd.isnull(lat) and not pd.isnull(lon):
                popup_text = f"Timestamp: {timestamp}<br>Temperature: {temperature}<br>Humidity: {humidity}<br>Smoke: {smoke}<br>LPG: {lpg}<br>CO: {co}"
                folium.Marker(location=[lat, lon], popup=popup_text).add_to(marker_map)

        # Save the map as an HTML file
        marker_map.save('marker_map.html')

    else:
        print("No valid coordinates found in the file.")





  

 


    # Set figure size and DPI
    fig_width = 12
    fig_height = 6
    dpi = 300

    # Plot 1: Temperature
    plt.figure(1, figsize=(fig_width, fig_height))
    plt.scatter(timestamp_list, temperature_list, label='Temperature', marker='o')
    plt.xlabel('Timestamp')
    plt.ylabel('Value')
    plt.title('Temperature Data')
    plt.legend()
    plt.xticks(rotation=45)
    plt.savefig('temperature_file.png')
    plt.close()

    # Plot 2: Humidity
    plt.figure(2, figsize=(fig_width, fig_height))
    plt.scatter(timestamp_list, humidity_list, label='Humidity', marker='o')
    plt.xlabel('Timestamp')
    plt.ylabel('Humidity Value')
    plt.title('Humidity Data')
    plt.legend()
    plt.xticks(rotation=45)
    plt.savefig('humidity_file.png')
    plt.close()


    GPIO.cleanup()

finally:
    # Disable GNSS module
    ser.write(b'AT+CGNSPWR=0\r\n')
    time.sleep(1)

    # Close serial port
    ser.close()    

    #mydb.close()
    #cursor.close()
