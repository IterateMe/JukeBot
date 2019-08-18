#This the program to run in the command prompt with the following command :
# "python /path/to/JukeBot/JukeBot.py"

import time
import subprocess

import RPi.GPIO 


def setup():
    """ This function initialise the GPIO pins for the program in order to run properly """
    global pin_led 
    global pin_button_off 
    global pin_button_language 
    global pin_bling_bling
    
    global actual_song_directory
    global french_song_directory
    global english_song_directory


    pin_led = 11
    pin_button_off = 12
    pin_button_language = 13
    pin_bling_bling = 16

    french_song_directory = "/path/to/directory"
    english_song_directory = "/path/to/directory"
    actual_song_directory = english_song_directory

    input_pins = [pin_led]
    output_pins = [pin_bling_bling, pin_button_off, pin_button_language]

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(input_pins, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
    GPIO.setup(output_pins, GPIO.OUT)


def led_on_off():
    """ When this function is called, if the led(s) are open, they are turned off and vice-versa """
    if GPIO.input(pin_led):
        GPIO.output(pin_led, 0)
    else:
        GPIO.output(pin_led, 1)

def led_blink(speed = 0.3, blinks = 10):
    """ This function make led(s) blink with default speed (in seconds) and default number of blinks """
    global pin_led
    count = blinks
    while count != 0:
        GPIO.output(pin_led, 1)
        time.sleep(speed)
        GPIO.output(pin_led, 0)
        time.sleep(speed)
        count -= 1


def close_RPi(self):
    """ This script closes the RPi if you keep pushing after the default 10 blinks of 0.3 seconds"""
    led_blink()
    if GPIO.input(pin_button_off):
        GPIO.cleanup()
        subprocess.call("sudo poweroff", shell=True)

def choose_language():
    global french_song_directory
    global english_song_directory
    global actual_song_directory

    if GPIO.input(pin_button_language):
        actual_song_directory = english_song_directory
    else:
        actual_song_directory = french_song_directory

def read_mp3(track):
    global actual_song_directory
    path = actual_song_directory + track
    p = vlc.MediaPlayer(path)
    p.play()

def bling_bling():
    read_mp3()

if __name__ == "__main__":          # THIS IS WHERE THE MAIN ACTIONS OF THIS SCRIPT HAPPENS
    try:
        setup()

        GPIO.add_event_detect(pin_button_off, GPIO.RISING, callback=close_RPi, bouncetime = 1000)
        GPIO.add_event_detect(pin_button_language, GPIO.RISING, callback=choose_language)
        GPIO.add_event_detect(pin_bling_bling, GPIO.RISING, callback=bling_bling, bouncetime = 200)
        
    except KeyboardInterrupt:
        GPIO.cleanup()              # If you want to terminate the program from the command prompt, use "Ctrl c"
