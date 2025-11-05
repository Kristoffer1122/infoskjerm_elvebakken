#!/usr/bin/env python3
from RPLCD.gpio import CharLCD
from RPi import GPIO
import time

print("Initializing LCD...")

try:
    # Initialize LCD
    lcd = CharLCD(
        pin_rs=17,
        pin_e=27,
        pins_data=[22, 23, 24, 25],
        numbering_mode=GPIO.BCM,
        cols=16,
        rows=2,
        dotsize=8,
        charmap='A02',
        auto_linebreaks=True
    )
    
    print("LCD initialized successfully!")
    
    # Clear display
    lcd.clear()
    time.sleep(0.5)
    
    # Write Hello World
    lcd.write_string('Hello World!')
    print("Written: Hello World!")
    
    # Move to second line
    lcd.cursor_pos = (1, 0)
    lcd.write_string('LCD Test OK!')
    print("Written: LCD Test OK!")
    
    print("If you see text on LCD, it works!")
    print("Press Ctrl+C to exit")
    
    # Keep running
    while True:
        time.sleep(1)

except Exception as e:
    print(f"Error: {e}")
    
except KeyboardInterrupt:
    print("\nExiting...")

finally:
    try:
        lcd.clear()
    except:
        pass
    GPIO.cleanup()
    print("Cleanup done")
