from RPLCD.gpio import CharLCD
from RPi import GPIO
import requests
import time
from datetime import datetime

# Initialize LCD
lcd = CharLCD(
    pin_rs=17,
    pin_e=27,
    pins_data=[22, 23, 24, 25],
    numbering_mode=GPIO.BCM,
    cols=16,
    rows=2
)

query = """
{
  stopPlace(id: "NSR:StopPlace:6435") {
    id
    name
    estimatedCalls(timeRange: 72100, numberOfDepartures: 10) {
      realtime
      aimedArrivalTime
      expectedArrivalTime
      destinationDisplay { frontText }
      quay { id }
      serviceJourney {
        journeyPattern {
          line { id name transportMode }
        }
      }
    }
  }
}
"""

url = "https://api.entur.io/journey-planner/v3/graphql"

def get_bus_data():
    try:
        response = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
                "ET-Client-Name": "elvebakken-infoskjerm"
            },
            json={"query": query}
        )
        
        data = response.json()
        bus_lines = []
        
        for call in data['data']['stopPlace']['estimatedCalls']:
            # Parse arrival time
            arrival_time = datetime.fromisoformat(call['expectedArrivalTime'].replace('Z', '+00:00'))
            time_str = arrival_time.strftime('%H:%M')
            
            bus_lines.append({
                'line': call['serviceJourney']['journeyPattern']['line']['name'],
                'destination': call['destinationDisplay']['frontText'],
                'time': time_str,
                'realtime': call['realtime']
            })
        
        return bus_lines
    
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def display_bus_info():
    try:
        while True:
            buses = get_bus_data()
            
            if buses:
                for bus in buses[:3]:  # Show first 3 buses
                    lcd.clear()
                    
                    # First row: Line number and destination (truncated to 16 chars)
                    line1 = f"{bus['line']} {bus['destination']}"[:16]
                    lcd.write_string(line1)
                    
                    # Second row: Time and realtime indicator
                    lcd.cursor_pos = (1, 0)
                    realtime_indicator = "RT" if bus['realtime'] else "  "
                    line2 = f"{bus['time']} {realtime_indicator}"
                    lcd.write_string(line2)
                    
                    time.sleep(5)  # Show each bus for 5 seconds
            else:
                lcd.clear()
                lcd.write_string('No departures')
                lcd.cursor_pos = (1, 0)
                lcd.write_string('available')
                time.sleep(10)
            
            # Wait before refreshing data
            time.sleep(30)
    
    except KeyboardInterrupt:
        pass
    finally:
        lcd.clear()
        GPIO.cleanup()

if __name__ == "__main__":
    lcd.clear()
    lcd.write_string('Loading...')
    time.sleep(2)
    display_bus_info()
