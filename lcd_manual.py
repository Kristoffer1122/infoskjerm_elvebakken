#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

# Pin definitions
RS = 17
E = 27
D4 = 22
D5 = 23
D6 = 24
D7 = 25

# Setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(RS, GPIO.OUT)
GPIO.setup(E, GPIO.OUT)
GPIO.setup(D4, GPIO.OUT)
GPIO.setup(D5, GPIO.OUT)
GPIO.setup(D6, GPIO.OUT)
GPIO.setup(D7, GPIO.OUT)

def lcd_toggle_enable():
    time.sleep(0.0005)
    GPIO.output(E, True)
    time.sleep(0.0005)
    GPIO.output(E, False)
    time.sleep(0.0005)

def lcd_byte(bits, mode):
    # Mode: True for character, False for command
    GPIO.output(RS, mode)
    
    # High bits
    GPIO.output(D4, False)
    GPIO.output(D5, False)
    GPIO.output(D6, False)
    GPIO.output(D7, False)
    if bits & 0x10 == 0x10:
        GPIO.output(D4, True)
    if bits & 0x20 == 0x20:
        GPIO.output(D5, True)
    if bits & 0x40 == 0x40:
        GPIO.output(D6, True)
    if bits & 0x80 == 0x80:
        GPIO.output(D7, True)
    
    lcd_toggle_enable()
    
    # Low bits
    GPIO.output(D4, False)
    GPIO.output(D5, False)
    GPIO.output(D6, False)
    GPIO.output(D7, False)
    if bits & 0x01 == 0x01:
        GPIO.output(D4, True)
    if bits & 0x02 == 0x02:
        GPIO.output(D5, True)
    if bits & 0x04 == 0x04:
        GPIO.output(D6, True)
    if bits & 0x08 == 0x08:
        GPIO.output(D7, True)
    
    lcd_toggle_enable()

def lcd_init():
    print("Initializing LCD...")
    lcd_byte(0x33, False)  # Initialize
    lcd_byte(0x32, False)  # Set to 4-bit mode
    lcd_byte(0x28, False)  # 2 line, 5x8 matrix
    lcd_byte(0x0C, False)  # Display on, cursor off
    lcd_byte(0x06, False)  # Increment cursor
    lcd_byte(0x01, False)  # Clear display
    time.sleep(0.005)
    print("LCD initialized!")

def lcd_string(message, line):
    # Line 1 = 0x80, Line 2 = 0xC0
    lcd_byte(line, False)
    for char in message:
        lcd_byte(ord(char), True)

try:
    lcd_init()
    
    lcd_string("Hello World!    ", 0x80)
    lcd_string("LCD Works!      ", 0xC0)
    
    print("Text written to LCD!")
    print("Press Ctrl+C to exit")
    
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    lcd_byte(0x01, False)  # Clear display
    GPIO.cleanup()
    print("Cleanup done")
