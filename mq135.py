import RPi.GPIO as GPIO
import time
import Adafruit_DHT
import spidev
import serial
#import mysql.connector
import folium
import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime

# Set up SPI interface
spi = spidev.SpiDev()
spi.open(0, 0)  # Open SPI bus 0, device 0
spi.max_speed_hz = 1000000  # Set SPI clock speed to 1 MHz

# Define the ADC channel to read from
channel = 0  # CH0 on MCP3008

# Define the MQ-135 sensor resistance and voltage conversion parameters
RL_VALUE = 10.0  # Replace with the resistance value of your MQ-135 sensor
RO_CLEAN_AIR_FACTOR = 9.83  # Replace with the Ro value of your MQ-135 sensor
VREF = 3.3  # Set the reference voltage for the ADC

# Define the air quality levels based on the sensor resistance
AIR_QUALITY_LEVELS = {
    "Excellent": (0, 50),
    "Good": (50, 100),
    "Moderate": (100, 150),
    "Poor": (150, 200),
    "Very Poor": (200, 300),
    "Hazardous": (300, 500),
}

def read_mcp3008(channel):
    # Read the ADC value from the specified channel
    adc_value = spi.xfer2([1, (8 + channel) << 4, 0])
    # Convert the ADC value to a voltage
    voltage = ((adc_value[1] & 3) << 8) + adc_value[2]
    voltage = (voltage * VREF) / float(1023)
    return voltage

def get_gas_concentration():
# Read the sensor value from the MCP3008 ADC
    sensor_value = read_mcp3008(channel)
    # Calculate the sensor resistance in kohms
    sensor_resistance = ((RL_VALUE * (VREF - sensor_value)) / sensor_value)
    # Calculate the air quality index (AQI)
    ratio = (sensor_resistance / RO_CLEAN_AIR_FACTOR)
    
    if ratio < 0.01:
        aqi = 0
    elif ratio < 0.02:
        aqi = 50
    elif ratio < 0.03:
        aqi = 100
    elif ratio < 0.04:
        aqi = 150
    elif ratio < 0.05:
        aqi = 200
    elif ratio < 0.06:
        aqi = 300
    else:
        aqi = 500
    
    # Calculate the gas concentration in PPM
    concentration = 10.0 ** ((aqi / 100) - 0.01)
    return aqi, concentration
while True:

    aqi, concentration = get_gas_concentration()
    for level, (lower, upper) in AIR_QUALITY_LEVELS.items():
        if lower <= aqi < upper:
           print(f"Air quality level: {level}")
        break
    print(f"Air quality index (AQI): {aqi}")
    print(f"Gas concentration (PPM): {concentration:.2f}")

