import adafruit_dht
from board import *

# GPIO4
SENSOR_PIN = D4

dht22 = adafruit_dht.DHT22(SENSOR_PIN, use_pulseio=False)

temperature = dht22.temperature
humidity = dht22.humidity

print(f"Humidity= {humidity:.2f}")
print(f"Temperature= {temperature:.2f}°C")
