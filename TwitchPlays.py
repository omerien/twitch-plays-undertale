# Written by DougDoug (DougDoug on Youtube, DougDougW on Twitch)

# Hello!
# This file contains the main logic to process Twitch chat and convert it to game commands.
# All sections that you need to update are labeled with a "TODO" comment.
# The source code primarily comes from:
    # Wituz's "Twitch Plays" tutorial: http://www.wituz.com/make-your-own-twitch-plays-stream.html
    # PythonProgramming's "Python Plays GTA V" tutorial: https://pythonprogramming.net/direct-input-game-python-plays-gta-v/

# There are 2 other files needed to run this code:
    # TwitchPlays_AccountInfo.py is where you put your Twitch username and OAuth token. This is to keep your account details separated from the main source code.
    # TwitchPlays_Connection.py is the code that actually connects to Twitch. You should not modify this file.

# Disclaimer: 
    # This code is NOT optimized or well-organized. I am not a Python programmer.
    # I created a simple version that works quickly, and I'm sharing it for educational purposes.

###############################################
# Import and define our functions / key codes to send key commands

# General imports
import time
import subprocess
import ctypes
import random
import string

# Twitch imports
import TwitchPlays_Connection
from TwitchPlays_AccountInfo import TWITCH_USERNAME, TWITCH_OAUTH_TOKEN

# Controller imports
import pyautogui
import pynput
from pynput.mouse import Button, Controller

SendInput = ctypes.windll.user32.SendInput

# KEY PRESS NOTES
# The standard "Twitch Plays" tutorial key commands do NOT work in DirectX games (they only work in general windows applications)
# Instead, we use DirectX key codes and input functions below.
# This DirectX code is partially sourced from: https://stackoverflow.com/questions/53643273/how-to-keep-pynput-and-ctypes-from-clashing

# Presses and permanently holds down a keyboard key
def PressKeyPynput(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = pynput._util.win32.INPUT_union()
    ii_.ki = pynput._util.win32.KEYBDINPUT(0, hexKeyCode, 0x0008, 0, ctypes.cast(ctypes.pointer(extra), ctypes.c_void_p))
    x = pynput._util.win32.INPUT(ctypes.c_ulong(1), ii_)
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

# Releases a keyboard key if it is currently pressed down
def ReleaseKeyPynput(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = pynput._util.win32.INPUT_union()
    ii_.ki = pynput._util.win32.KEYBDINPUT(0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.cast(ctypes.pointer(extra), ctypes.c_void_p))
    x = pynput._util.win32.INPUT(ctypes.c_ulong(1), ii_)
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

# Helper function. Holds down a key for the specified number of seconds, then releases it.
def PressAndHoldKey(hexKeyCode, seconds):
    PressKeyPynput(hexKeyCode)
    time.sleep(seconds)
    ReleaseKeyPynput(hexKeyCode)

# Mouse Controller, using pynput
    # pynput.mouse functions are found at: https://pypi.org/project/pynput/
    # NOTE: pyautogui's click() function permanently holds down in DirectX, so I used pynput instead for mouse instead.
mouse = Controller()

###############################################
# DIRECTX KEY CODES
# These codes identify each key on the keyboard.
# Note that DirectX's key codes (or "scan codes") are NOT the same as Windows virtual hex key codes. 
#   DirectX codes are found at: https://docs.microsoft.com/en-us/previous-versions/visualstudio/visual-studio-6.0/aa299374(v=vs.60)
Q = 0x10
W = 0x11
E = 0x12
R = 0x13
T = 0x14
Y = 0x15
U = 0x16
I = 0x17
O = 0x18
P = 0x19
A = 0x1E
S = 0x1F
D = 0x20
F = 0x21
G = 0x22
H = 0x23
J = 0x24
K = 0x25
L = 0x26
Z = 0x2C
X = 0x2D
C = 0x2E
V = 0x2F
B = 0x30
N = 0x31
M = 0x32
ESC = 0x01
ONE = 0x02
TWO = 0x03
THREE = 0x04
FOUR = 0x05
FIVE = 0x06
SIX = 0x07
SEVEN = 0x08
EIGHT = 0x09
NINE = 0x0A
ZERO = 0x0B
MINUS = 0x0C
EQUALS = 0x0D
BACKSPACE = 0x0E
SEMICOLON = 0x27
TAB = 0x0F
CAPS = 0x3A
ENTER = 0x1C
LEFT_CONTROL = 0x1D
LEFT_ALT = 0x38
LEFT_SHIFT = 0x2A
SPACE = 0x39
DELETE = 0x53
COMMA = 0x33
PERIOD = 0x34
BACKSLASH = 0x35
NUMPAD_0 = 0x52
NUMPAD_1 = 0x4F
NUMPAD_2 = 0x50
NUMPAD_3 = 0x51
NUMPAD_4 = 0x4B
NUMPAD_5 = 0x4C
NUMPAD_6 = 0x4D
NUMPAD_7 = 0x47
NUMPAD_8 = 0x48
NUMPAD_9 = 0x49
NUMPAD_PLUS = 0x4E
NUMPAD_MINUS = 0x4A
LEFT_ARROW = 0xCB
RIGHT_ARROW = 0xCD
UP_ARROW = 0xC8
DOWN_ARROW = 0xD0
LEFT_MOUSE = 0x100
RIGHT_MOUSE = 0x101
MIDDLE_MOUSE = 0x102
MOUSE3 = 0x103
MOUSE4 = 0x104
MOUSE5 = 0x105
MOUSE6 = 0x106
MOUSE7 = 0x107
MOUSE_WHEEL_UP = 0x108
MOUSE_WHEEL_DOWN = 0x109
Ffour = 0x3E


########################################################

# An optional countdown before the code actually starts running, so you have time to load up the game before messages are processed.
# TODO: Set the "countdown" variable to whatever countdown length you want.
countdown = 1 #The number of seconds before the code starts running
while countdown > 0:
    print(countdown)
    countdown -= 1
    time.sleep(1)

# Connects to your twitch chat, using your username and OAuth token.
# TODO: make sure that your Twitch username and OAuth token are added to the "TwitchPlays_AccountInfo.py" file
t = TwitchPlays_Connection.Twitch();
t.twitch_connect(TWITCH_USERNAME, TWITCH_OAUTH_TOKEN);

##########################################################

while True:
    # Check for new chat messages
    new_messages = t.twitch_recieve_messages();
    if not new_messages:
        #No new messages. 
        continue
    else:
        try:  
            for message in new_messages:
                # We got a new message! Get the message and the username.
                msg = message['message'].lower()
                username = message['username'].lower()
                
                # TODO:
                # Now that you have a chat message, this is where you add your game logic.
                # Use the "PressKeyPynput(KEYCODE)" function to press and hold down a keyboard key.
                # Use the "ReleaseKeyPynput(KEYCODE)" function to release a specific keyboard key.
                # Use the "PressAndHoldKey(KEYCODE, SECONDS)" function press down a key for X seconds, then release it.
                # Use "mouse.press(Button.left)" or "mouse.release(Button.left)" to press/release the mouse. Can use Button.right for right click.

                # I've added some example videogame logic code below:

                ###################################
                # Example GTA V Code 
                ###################################

                # If the chat message is "left", then hold down the A key for 2 seconds
                #if msg == "left": 
                    #PressAndHoldKey(A, 2)

                # If the chat message is "right", then hold down the D key for 2 seconds
                #if msg == "right": 
                    #PressAndHoldKey(D, 2)

                # If message is "drive", then permanently hold down the W key
                #if msg == "drive": 
                    #ReleaseKeyPynput(S) #release brake key first
                    #PressKeyPynput(W) #start permanently driving

                # If message is "reverse", then permanently hold down the S key
                #if msg == "reverse": 
                    #ReleaseKeyPynput(W) #release drive key first
                    #PressKeyPynput(S) #start permanently reversing

                # Release both the "drive" and "reverse" keys
                #if msg == "stop": 
                    #ReleaseKeyPynput(W)
                    #ReleaseKeyPynput(S)

                # Press the spacebar for 0.7 seconds
                #if msg == "brake": 
                    #PressAndHoldKey(SPACE, 0.7)
                if msg == "windows key":
                    PressKeyPynput(WINDOWS)
                    ReleaseKeyPynput(WINDOWS)


                if msg == "left":
                    pyautogui.move(-100,0)

                if msg == "light left":
                    pyautogui.move(-25,0)

                if msg == "right":
                    pyautogui.move(100,0)

                if msg == "light right":
                    pyautogui.move(25,0)

                if msg == "up":
                    pyautogui.move(0, -100)

                if msg == "light up":
                    pyautogui.move(0, -25)

                if msg == "down":
                    pyautogui.move(0, 100)

                if msg == "light down":
                    pyautogui.move(0, 25)

                if msg == "rightclick": 
                    mouse.press(Button.right)
                    time.sleep(0.1)
                    mouse.release(Button.right)

                # Presses the left mouse button down for 1 second, then releases it
                if msg == "click": 
                    mouse.press(Button.left)
                    time.sleep(0.1)
                    mouse.release(Button.left)

                if msg == "doubleclick": 
                    mouse.press(Button.left)
                    time.sleep(0.1)
                    mouse.release(Button.left)
                    mouse.press(Button.left)
                    time.sleep(0.1)
                    mouse.release(Button.left)

                if msg == "tab":
                    PressKeyPynput(TAB)
                    ReleaseKeyPynput(TAB)

                if msg == "enter":
                    PressKeyPynput(ENTER)
                    ReleaseKeyPynput(ENTER)

                if msg == "space":
                    PressKeyPynput(SPACE)
                    ReleaseKeyPynput(SPACE)

                if msg == "where?":
                    PressKeyPynput(LEFT_CONTROL)
                    ReleaseKeyPynput(LEFT_CONTROL)



                ###################################
                # Example Miscellaneous Code 
                ###################################
                
                # Clicks and drags the mouse upwards, using the Pyautogui commands.
                # NOTE: unfortunately, Pyautogui does not work in DirectX games like GTA V. It will work in all other environments (e.g. on your desktop)
                # If anyone finds a reliable way to move the mouse in DirectX games, please let me know!
                if msg == "drag mouse up":
                    pyautogui.drag(0, -50, 0.25, button='left')

                # Clicks and drags the mouse downwards, using the Pyautogui commands
                if msg == "drag mouse down":
                    pyautogui.drag(0, 50, 0.25, button='left')

                if msg == "drag mouse right":
                    pyautogui.drag(50, 0, 0.25, button='left')

                if msg == "drag mouse left":
                    pyautogui.drag(-50, 0, 0.25, button='left')

                if msg == "backspace":
                    PressKeyPynput(BACKSPACE)
                    time.sleep(0.1)
                    ReleaseKeyPynput(BACKSPACE)

                if msg == "arrow up":
                    PressKeyPynput(UP_ARROW)
                    time.sleep(1)
                    ReleaseKeyPynput(UP_ARROW)

                if msg == "arrow down":
                    PressKeyPynput(DOWN_ARROW)
                    time.sleep(1)
                    ReleaseKeyPynput(DOWN_ARROW)

                if msg == "arrow left":
                    PressKeyPynput(LEFT_ARROW)
                    time.sleep(1)
                    ReleaseKeyPynput(LEFT_ARROW)

                if msg == "arrow right":
                    PressKeyPynput(RIGHT_ARROW)
                    time.sleep(1)
                    ReleaseKeyPynput(RIGHT_ARROW)

                if msg == "quit":
                    PressKeyPynput(LEFT_ALT)
                    PressAndHoldKey(Ffour, 0.1)
                    ReleaseKeyPynput(LEFT_ALT)

                if msg == "its stuck":
                    mouse.position = (500, 500)


                if username == "controlmypc":
                    if msg == "starting soon":
                        PressKeyPynput(LEFT_ALT)
                        PressAndHoldKey(S, 0.1)
                        ReleaseKeyPynput(LEFT_ALT)

                    if msg == "main":
                        PressKeyPynput(LEFT_ALT)
                        PressAndHoldKey(C, 0.1)
                        ReleaseKeyPynput(LEFT_ALT)

                    if msg == "stop the stream!":
                        PressKeyPynput(LEFT_ALT)
                        PressAndHoldKey(Q, 0.1)
                        ReleaseKeyPynput(LEFT_ALT)

                    if msg == "maintenance":
                        PressKeyPynput(LEFT_ALT)
                        PressAndHoldKey(M, 0.1)
                        ReleaseKeyPynput(LEFT_ALT)


                # An example of pressing 2 keys at once.
                # First holds down the LEFT_CONTROL key, then presses the A key for 0.1 seconds, then releases the LEFT_CONTROL key.
                if msg == "select all":
                    PressKeyPynput(LEFT_CONTROL)
                    PressAndHoldKey(A, 0.1)
                    ReleaseKeyPynput(LEFT_CONTROL)
                
                # Can use pyautogui.typewrite() to type messages from chat into the keyboard.
                # Here, if a chat message says "type ...", it will type out their text.
                if msg.startswith("type "): 
                    try:
                        typeMsg = msg[5:] # Ignore the "type " portion of the message
                        pyautogui.typewrite(typeMsg)
                    except:
                        # There was some issue typing the msg. Print it out, and move on.
                        print("Typing this particular message didn't work: " + msg)

                ####################################
                ####################################

        except:
            # There was some error trying to process this chat message. Simply move on to the next message.
            print('Encountered an exception while reading chat.')

