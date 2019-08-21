#This is the program to run in the command prompt with the following command :
# "python /path/to/JukeBot/JukeBot.py"

import time
import subprocess
import os
import random

import vlc
import RPi.GPIO 


def setup():
    """ This function initialise the GPIO pins for the program in order to run properly """
    # Setup all the global variables
    global pin_led 
    global pin_button_off 
    global pin_button_language 
    global pin_bling_bling
    
    global actual_song_directory
    global french_song_directory
    global english_song_directory

    global french_song_list
    global english_song_list

    # This is the list of directory where all the .mp3 files are located
    french_song_directory = "//path//to//directory"            ### ENTER YOUR DIRECTORY HERE ### WITH DOUBLE SLASHES "//" INSTEAD OF SINGLE ONES
    english_song_directory = "//path//to//directory"           ### ENTER YOUR DIRECTORY HERE ### WITH DOUBLE SLASHES "//" INSTEAD OF SINGLE ONES
    actual_song_directory = english_song_directory          # The default song directory is the english one... sorry law 101

    # This is the lists for .mp3 files in the french or english directory: [[NOT RED], [ALREADY RED]] -- They will be initialised or refreshed each time the order_files_list() function is called
    french_song_list = [[],[]]
    english_song_list = [[],[]]

    # Setup the GPIO pins
    pin_led = 11
    pin_button_off = 12
    pin_button_language = 13
    pin_bling_bling = 16
    
    input_pins = [pin_led]
    output_pins = [pin_bling_bling, pin_button_off, pin_button_language]

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(input_pins, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
    GPIO.setup(output_pins, GPIO.OUT)


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

def choose_language(self):
    """ This function determines the directory of .mp3 files to read from (english or french). It runs as a threaded callback"""
    global french_song_directory
    global english_song_directory
    global actual_song_directory

    if GPIO.input(pin_button_language):
        actual_song_directory = english_song_directory
    else:
        actual_song_directory = french_song_directory

def read_random_mp3(song_list):
    """ This function reads the .mp3 file given as an argument from the chosen directory (actual_song_directory)"""
    
    global actual_song_directory

    # Select a random track from the song list passed as an argument (english or french)
    track = random.choice(song_list[0])
    
    # Play that track
    path = actual_song_directory + track
    p = vlc.MediaPlayer(path)
    p.play()

    # Move the played track from the unred to the red list
    song_list[1].append(track)
    song_list[0].remove(track)

def order_files_list(path, song_list):
    """ Refresh the list of .mp3 files that have been red, not red and possibly added """

    # Initialize the song list OR add new .mp3 files to the list that might have been put in the repository
    for r,d,f in os.walk(path):
        for file in f:
            if ".mp3" in file and file not in song_list[0] and file not in song_list[1]:
                song_list[0].append(file)

    # Remove any .mp3 files from the unred list that has already been red
    for track in song_list[1]:
        if track in song_list[0]:
            song_list[0].remove(track)

    # If all songs have been red, then all the "red" songs come back to the unred list
    if not bool(song_list[0]):
        song_list[0] = song_list[1]
        song_list[1].clear()

def bling_bling(self):
    """ This is the main function run as a threaded callback when money enter the coin recepter """
    
    # The led in the eyes turn on
    GPIO.output(pin_led, 1)

    global english_song_list
    global french_song_list

    # Run the "order_files_list()" function in order to refresh the list of .mp3 files that have been red, not red and possibly added
    # Then, play a random .mp3 file
    if actual_song_directory == english_song_directory:
        order_files_list(actual_song_directory, english_song_list)
        read_random_mp3(english_song_list)
    else:
        order_files_list(actual_song_directory, french_song_list)
        read_random_mp3(french_song_list)
    
    # The led in the eyes of the robot turn off at the end of the song play
    GPIO.output(pin_led, 0)
    

if __name__ == "__main__":          # THIS IS WHERE THE MAIN ACTIONS OF THIS SCRIPT HAPPENS
    try:
        setup()

        GPIO.add_event_detect(pin_button_off, GPIO.RISING, callback = close_RPi, bouncetime = 1000)
        GPIO.add_event_detect(pin_button_language, GPIO.RISING, callback = choose_language)
        GPIO.add_event_detect(pin_bling_bling, GPIO.RISING, callback = bling_bling, bouncetime = 200)

        while True:
            time.sleep(60)
        
    except KeyboardInterrupt:
        GPIO.cleanup()              # If you want to terminate the program from the command prompt, use "Ctrl c"
