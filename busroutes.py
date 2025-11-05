from RPLCD.gpio import CharLCD
from RPi import GPIO
import requests
import time
from datetime import datetime, timedelta

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
            
            bus_lines.append({
                'line': call['serviceJourney']['journeyPattern']['line']['name'],
                'destination': call['destinationDisplay']['frontText'],
                'arrival_time': arrival_time,
                'realtime': call['realtime']
            })
        
        return bus_lines
    
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def get_minutes_until(arrival_time):
    """Calculate minutes until arrival"""
    now = datetime.now(arrival_time.tzinfo)
    diff = arrival_time - now
    minutes = int(diff.total_seconds() / 60)
    return max(0, minutes)  # Don't show negative numbers

def display_bus_info():
    last_fetch = None
    buses = []
    
    try:
        while True:
            # Fetch new data every 30 seconds
            if last_fetch is None or (time.time() - last_fetch) > 30:
                buses = get_bus_data()
                last_fetch = time.time()
            
            if buses and len(buses) >= 1:
                # Get current time
                now = datetime.now()
                current_time = now.strftime('%H:%M')
                
                # Next bus
                next_bus = buses[0]
                minutes_until_next = get_minutes_until(next_bus['arrival_time'])
                
                # Line 1: Line number, current time, minutes until next bus
                line1 = f"{next_bus['line']} {current_time} {minutes_until_next}min"[:16]
                
                # Line 2: Time until second bus (if available)
                if len(buses) >= 2:
                    second_bus = buses[1]
                    minutes_until_second = get_minutes_until(second_bus['arrival_time'])
                    line2 = f"Next: {minutes_until_second}min"[:16]
                else:
                    line2 = "Next: N/A"
                
                lcd.clear()
                lcd.write_string(line1)
                lcd.cursor_pos = (1, 0)
                lcd.write_string(line2)
                
            else:
                lcd.clear()
                lcd.write_string('No departures')
                lcd.cursor_pos = (1, 0)
                lcd.write_string('available')
            
            # Update display every second to keep time current
            time.sleep(1)
    
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
