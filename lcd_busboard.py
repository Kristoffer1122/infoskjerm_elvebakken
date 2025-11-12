#!/usr/bin/env python3
import requests
from datetime import datetime, timezone
import time
from RPLCD import CharLCD
import RPi.GPIO as GPIO

# --------------------------
# LCD Setup (16x2)
# --------------------------
GPIO.setwarnings(False)
lcd = CharLCD(
    numbering_mode=GPIO.BCM,
    cols=16,
    rows=2,
    pin_rs=26,
    pin_e=19,
    pins_data=[13, 6, 5, 11]
)

# --------------------------
# Norwegian letters support
# --------------------------
lcd.create_char(0, [0b00110,0b00001,0b01111,0b10001,0b11111,0b10001,0b10011,0b01101])  # æ
lcd.create_char(1, [0b01110,0b10001,0b10011,0b10101,0b11001,0b10001,0b10001,0b01110])  # ø
lcd.create_char(2, [0b00100,0b01010,0b00100,0b01110,0b10001,0b11111,0b10001,0b10001])  # å

def convert_norwegian_chars(text):
    mapping = {
        "æ": chr(0),
        "ø": chr(1),
        "å": chr(2),
        "Æ": chr(0),
        "Ø": chr(1),
        "Å": chr(2)
    }
    for k, v in mapping.items():
        text = text.replace(k, v)
    return text

# --------------------------
# Entur API setup
# --------------------------
URL = "https://api.entur.io/journey-planner/v3/graphql"
HEADERS = {
    "Content-Type": "application/json",
    "ET-Client-Name": "Infoboard-app"
}

QUERY = """
{
  stopPlace(id: "NSR:StopPlace:6435") {
    id
    name
    estimatedCalls(timeRange: 72100, numberOfDepartures: 10) {
      realtime
      aimedArrivalTime
      expectedArrivalTime
      destinationDisplay {
        frontText
      }
      serviceJourney {
        journeyPattern {
          line {
            id
            transportMode
          }
        }
      }
    }
  }
}
"""

# --------------------------
# Helper functions
# --------------------------
def fetch_departures():
    try:
        response = requests.post(URL, headers=HEADERS, json={"query": QUERY})
        response.raise_for_status()
        data = response.json()
        return data["data"]["stopPlace"]["estimatedCalls"]
    except Exception as e:
        print("Fetch error:", e)
        return []

def format_departure(call):
    expected = datetime.fromisoformat(call["expectedArrivalTime"].replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    diff_minutes = int((expected - now).total_seconds() / 60)
    time_str = "nå" if diff_minutes <= 0 else f"{diff_minutes} min"

    line_id = call["serviceJourney"]["journeyPattern"]["line"]["id"].split(":")[-1]
    destination = call["destinationDisplay"]["frontText"]
    return convert_norwegian_chars(f"{line_id} {destination} {time_str}")

def scroll_text(text, width=16):
    if len(text) <= width:
        while True:
            yield text.ljust(width)
    else:
        scroll_text_str = text + " " * 4
        while True:
            for i in range(len(scroll_text_str) - width + 1):
                yield scroll_text_str[i:i+width]

def get_next_two_screens(departures):
    """
    Return 2 screens:
    Screen 1: Next 2 departures for Ekeberg hageby / Tåsen etc
    Screen 2: Next 2 departures for Kjelsås stasjon / Kværnerbyen
    """
    # Map each screen to destinations
    screen1_targets = ["Tåsen", "Ekeberg hageby"]
    screen2_targets = ["Kjelsås stasjon", "Kværnerbyen"]

    screen1 = [d for d in departures if d["destinationDisplay"]["frontText"] in screen1_targets][:2]
    screen2 = [d for d in departures if d["destinationDisplay"]["frontText"] in screen2_targets][:2]

    return screen1, screen2

def show_screen(departures, display_time=8, scroll_delay=0.5):
    if not departures:
        lcd.clear()
        lcd.write_string("Ingen data")
        time.sleep(display_time)
        return

    lines = [format_departure(d) for d in departures]
    scroll_gens = [scroll_text(line) for line in lines]

    cycles = int(display_time / scroll_delay)
    for _ in range(cycles):
        for row, gen in enumerate(scroll_gens):
            lcd.cursor_pos = (row, 0)
            lcd.write_string(next(gen))
        time.sleep(scroll_delay)

# --------------------------
# Main Loop
# --------------------------
try:
    while True:
        departures = fetch_departures()
        screen1, screen2 = get_next_two_screens(departures)

        # Show screen 1
        show_screen(screen1, display_time=8, scroll_delay=0.5)

        # Show screen 2
        show_screen(screen2, display_time=8, scroll_delay=0.5)

except KeyboardInterrupt:
    lcd.clear()
    lcd.close(clear=True)
    GPIO.cleanup()
    print("Exiting")

