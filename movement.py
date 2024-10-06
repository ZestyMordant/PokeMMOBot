import time
import threading
import random
import pytesseract
import cv2
from PIL import ImageGrab
import numpy as np
from pynput.keyboard import Key
from projectP import Bot
import tkinter as tk
from tkinter import ttk
import pygetwindow as gw
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
run = False
inSafari = False
fishing = False
started = False
ballCount = 5
walkTimePerTile = 0.26666666666666667
runTimePerTile = 0.184
breakChance = 0.01
timeRunning = 0


#################################################################################################################################################################
#startBot
#Changes some Boolean values and checks the mode to see what the bot should do
#Switches the focus to the pokemmo window
#Starts a thread to control the Bots movements and controls
#
#
#################################################################################################################################################################
def startBot():
    global run, paused, mode, started, timeRunning
    mode = mode_var.get()
    run = True
    paused = False
    print("Bot started in mode:", mode)
    switchFocusToGame()
    if not started:
        started = True
        threading.Thread(target=main, daemon=True).start() #start the thread to control the Bots movements/controls

#################################################################################################################################################################
#stopBot
#Closes out the Gui and stop the program
#
#
#################################################################################################################################################################
def stopBot():
    global run
    run = False
    print("Bot stopped, exiting program")
    root.destroy()
    
#################################################################################################################################################################
#pauseBot
#Changes the paused variable to True which pauses the bot, the most appropriate/effective spot to pause the bot is inbetween casts
#
#
#################################################################################################################################################################
def pauseBot():
    global paused
    paused = True
    if paused:
        print("Bot paused")
#################################################################################################################################################################
#switchFocusToGame
#This function switches the focus from the gui to the pokemmo window
#
#
#################################################################################################################################################################    

def switchFocusToGame():
    window_title = "PokеMMO"  
    try:
        game_window = gw.getWindowsWithTitle(window_title)[0]
        game_window.activate()
    except IndexError:
        print(f"No window with title '{window_title}' found.")
#################################################################################################################################################################
#main
#The main function initializes the bot object and is responsible for the bot to enter the safari zone and which mode the bot will use
#Current version only allows the user to fish for Magikarp
#
################################################################################################################################################################# 

def main():
    global run,timeRunning
    print("Bot is running in mode:", mode)
    timeRunning = time.time() #Start timer for breaks
    time.sleep(0.5) #Allow for the script to change focus to pokemmo 
    while(run):
        if not paused:
            
            bot = Bot()
            if mode == 'Magikarp Farming':
                while(1):
                    if run: 
                        if  inSafari:        
                            magikarpFishing(bot)
                            time.sleep(.3)
                        else:
                            print("entering safari")
                            enterSafari(bot)
                            number = getRandomFloat(1,2) 
                            time.sleep(number)
                            moveToWater(bot)
                    else:
                        #stopBallCountThread(bot) #stops the ball count thread 
                        
                        time.sleep(0.1)
            else:
                magikarpFishing(bot)#At water already
                
#################################################################################################################################################################
#magikarpFishing
#This function uses Tesseract OCR to determine whether or not a fish is on the hook and depending on the result will either cast the rod again or enter combat
#
#
################################################################################################################################################################# 
def magikarpFishing(bot):

    while (not paused):
        print("Fishing")
        randomBreak()
        bot.press('2') #cast rod
        number = getRandomFloat(0.1,0.2)
        time.sleep(number)
        bot.release('2')
        timebetweenFishing = getRandomFloat(5,6) #wait for combat or not even a nibble
        time.sleep(timebetweenFishing)
        region = (552,137,779,168) #PokeMMO
        text = readScreen(region)
        message = "Landed a Pokémon"
        if message in text:
            print(text)
            bot.press('x') #press a
            number = getRandomFloat(0.1,0.2)
            time.sleep(number)
            bot.release('x')
            print("going into combat")
            number = getRandomFloat(5,7) #delay for the setup of combat scene
            time.sleep(number)
            catchMagikarp(bot)
        else:
            bot.press('x')
            number = getRandomFloat(0.1,0.2)
            bot.release('x')
            print("no fish")
            timebetweenFishing = getRandomFloat(1,3) #wait for combat or not even a nibble
            time.sleep(timebetweenFishing)
            
    
#################################################################################################################################################################
#catchMagikarp
#This function uses Tesseract OCR to determine whether or not the Magikarp is caught and will either throw the ball again or head into processing the pokemon and 
# catching the next one
#
################################################################################################################################################################# 
def catchMagikarp(bot):
    while not paused:
        global ballCount
        region = (375,688,420,701) #Ball
        message = "BALL"
        text = readScreen(region)
        alist = ['M', 'a', 'g', 'i','k','a','r','p']
        region2 = (330, 150, 408, 172) #Magikarp
        text2 = readScreen(region2)
        if message in text: #if they are in combat and haven't thrown a ball
            bot.press('x')
            
            number = getRandomFloat(0.1,0.2)
            time.sleep(number)
            bot.release('x')
            ballCount -= 1
            print("Ball count {}".format(ballCount))
            number = getRandomFloat(8,10)
            time.sleep(number)
            
            if ballCount == 0:
                print("Ball count is 0 leaving safari")
                checkBallCount(bot)
                
                #stopEvent.clear()
                #threading.Thread(target=checkBallCount, daemon=True, args= (bot, stopEvent)).start()
        elif not any(char in text2 for char in alist): #sometimes has troubles reading magikarp because of the background shifting around so lets make it easier for it
            #User is not in combat
            print(text2)
            print("Leaving Combat")
            number = getRandomFloat(3,4)
            time.sleep(number)
            text3 = readScreen(region= (1028,384,1154,405)) #PokemonSummary 
            if("Pokémon Summary" in text3):
                print("caught a Magikarp")
                processCatch(bot)
            else:
                print("The Magikarp got away")
            return
        
#################################################################################################################################################################
#processCatch
#This function clicks on the IV button of the pokemon entry as well as closing out the window of that entry
#There is also a chance for a misclick to try and evade detection
#
################################################################################################################################################################# 
def processCatch(bot):
    #click on IV's
    if not paused:
        print("processing")
        if random.random() < 0.7: #70% chance to check IVs
            ivX = getRandomInteger(787,795)
            ivY = getRandomInteger(385,400)
            randomMisclick(bot,ivX,ivY)
            number = getRandomFloat(3,5)
            time.sleep(0.1)
            bot.leftClick(ivX,ivY)   
            number = getRandomFloat(2,4)
            time.sleep(number)
        number = getRandomFloat(1,3)
        time.sleep(number)
        #exit out window
        Xnumber = getRandomInteger(1191,1197) #X dimension
        Ynumber = getRandomInteger(394,397) #Y dimension 
        randomMisclick(bot,Xnumber,Ynumber)
        time.sleep(0.1)
        bot.leftClick(Xnumber,Ynumber)
        timebetweenCasts = getRandomFloat(1,6)  
        time.sleep(timebetweenCasts)
        return
    else:
        return

#################################################################################################################################################################
#readScreen
#This Function uses three other functions to read a certain region of the screen that Tesseract OCR uses to determine what the game is telling the user 
#In order to use string comparisons
#
################################################################################################################################################################# 
def readScreen(region):
    image = captureScreen(region)
    preprocessed_image = preprocessImage(image)
    text = readTextFromImage(preprocessed_image) 
    return text
    
#################################################################################################################################################################
#captureScreen
#This Function captures an region of the screen and converts it to greyscale 
#
#
################################################################################################################################################################# 
def captureScreen(region=None):
    screenshot = ImageGrab.grab(bbox=region)  # Capture the screen
    screenshot_np = np.array(screenshot)  # Convert to numpy array
    gray_screenshot = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)  # Convert to grayscale, this converts the images RGB to shades of grey
    return gray_screenshot

#################################################################################################################################################################
#preprocessImage
#This Function resizes the image and uses Binary thresholding to enhance the accuracy for Tesseract OCR
#
#
################################################################################################################################################################# 
def preprocessImage(image):
    # Resize the image to double its size for better OCR accuracy
    image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    # Apply binary thresholding , this turns the grey scale image into a binary image where each pixel is either black or white depending on the threshold
    _, binary_image = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Apply median blurring to remove noise
    blurred_image = cv2.medianBlur(binary_image, 3)
    
    return blurred_image

#################################################################################################################################################################
#readTextFromImage
#This Function takes the processed image and returns a string that is used for string comparisons
#
#
################################################################################################################################################################# 
def readTextFromImage(image):
    config = '--psm 6 --oem 3'  # PSM 6 is for a uniform block of text, OEM 3 is the default OCR Engine Mode
    
    text = pytesseract.image_to_string(image, config=config, lang='eng')
    return text

#################################################################################################################################################################
#enterSafari
#This function is used to click through the safari clerks dialogue to enter the safari zone
#
#
################################################################################################################################################################# 
def enterSafari(bot):
    global inSafari
    counter = 0
    bot.press(Key.up)
    time.sleep(0.2)
    bot.release(Key.up)
    while counter != 10:
        print("X counter: {}" .format(counter))
        bot.press('x')
        bot.release('x')
        number = getRandomFloat(1,2)
        time.sleep(number)
        counter += 1
    inSafari = True

#################################################################################################################################################################
#moveToWater
#This function takes an approximate time to cross a tile and uses that to navigate a body of water
#
#
################################################################################################################################################################# 
def moveToWater(bot):
    timeUp = walkTimePerTile * 8
    timeRight = walkTimePerTile * 6
    timeUp2 = walkTimePerTile * 2
    bot.press(Key.up)
    time.sleep(timeUp)
    bot.release(Key.up)

    bot.press(Key.right)
    time.sleep(timeRight)
    bot.release(Key.right)

    bot.press(Key.up)
    time.sleep(timeUp2)
    bot.release(Key.up)
        
#################################################################################################################################################################
#getRandomFloat
#This function uses the random module to get a random float between ranges given to give delays to the bots actions
#
#
################################################################################################################################################################# 
def getRandomFloat(lower,upper):
    number = random.uniform(lower,upper)
    return number

#################################################################################################################################################################
#getRandomInteger
#This function uses the random module to get a random Integer to give the bots left mouse clicks a range for variation
#
#
################################################################################################################################################################# 
def getRandomInteger(lower,upper):
    number = random.randint(lower,upper)
    return number

#################################################################################################################################################################
#randomMisclick
#This function attempts to make the bot misclick within a random range when dealing with the pokemon entry when a magikarp has been caught to avoid detection
#
#
################################################################################################################################################################# 
def randomMisclick(bot,X,Y):
    if random.random() < 0.2: #20% chance for a random misclick
        print("Misclicked !")
        deviation = getRandomInteger(6,10)
        if random.random() < 0.5: #50% to add or subtract deviation from position
            X = X + deviation
            bot.leftClick(X,Y)
            CorrectionTiming = getRandomFloat(1,1.5)
            time.sleep(CorrectionTiming)
        else:
            X = X - deviation
            bot.leftClick(X,Y)
            CorrectionTiming = getRandomFloat(1,1.5)
            time.sleep(CorrectionTiming)
    else:
        return
    return

#################################################################################################################################################################
#randomBreak
#This function takes the start time of the program and progressively increases the chance for a "break" to make the bot seem more human
#After a break has occured the chance for a break is reset
#
################################################################################################################################################################# 
def randomBreak():
    global breakChance,run,timeRunning,ballCount
    CurrentTime = time.time()
    elapsedTime = CurrentTime - timeRunning
    
    if((elapsedTime) > 300): #slowly increase breakChance
        print("elapsed time {}".format(elapsedTime))
        print("current time {}".format(CurrentTime))
        print("timerunning time {}".format(timeRunning))
        timeRunning = CurrentTime
        print("updated timerunning time {}".format(timeRunning))
        breakChance += 0.02
        print("5 minutes have passed increasing break chance")
        
    if((random.random() < breakChance) and (ballCount > 5)):
        run = False
        breakTime = getRandomFloat(2,6)
        print("taking a {} minute break".format(breakTime))
        breakTime = breakTime * 60 #times 60 for minutes
        time.sleep(breakTime)
        print("Breaks over")
        CurrentTime = time.time() #need to set Current Time to time running 
        timeRunning = CurrentTime
        breakChance = 0.05 #set chance back to five percent
    

    
#################################################################################################################################################################
#checkBallCount
#This function uses a thread that starts up after the ball count is equal to 2 in order to pause the main bot loop so that it can handle the dialogue that kicks
#the user out of the safari zone
#
################################################################################################################################################################# 
def checkBallCount(bot):
    global paused,ballCount
    
    try:
        if ballCount == 0:
            #print("paused out of balls")
            paused = True #stop the main loop
            if checkCombat():
                exitCombat(bot)
            time.sleep(2)
            exitSafari(bot)
            number = getRandomFloat(3,6)
            time.sleep(number)
            print("Exiting safari zone, Press 'e' again to resume after exiting...")
    except:
        pass

#################################################################################################################################################################
#checkCombat
#This function uses a thread that starts up after the ball count is equal to 0 and checks if the user is still in battle, if they are it returns true otherwise false
#
#
################################################################################################################################################################# 
def checkCombat():
    print("0 balls left checking for combat")
    region = (330, 150, 408, 172)
    text = readScreen(region)
    message = "Magikarp"
    if message in text:
        return True
    else:
        return False
#################################################################################################################################################################
#exitCombat
#This function clicks on the run button in combat within a range 
#
#
#################################################################################################################################################################
def exitCombat(bot):
    print("exiting combat")
    runX = getRandomInteger(510,707)
    runY = getRandomInteger(735,775)
    dialogueDelay = getRandomFloat(3,4)
    time.sleep(dialogueDelay)
    bot.leftClick(runX,runY)
    time.sleep(2)
    return

#################################################################################################################################################################
#exitSafari
#This function clicks through the dialogue to exit the safari zone 
#
#
#################################################################################################################################################################
def exitSafari(bot):
    global inSafari
    print("exiting Safari")
    counter = 0
    region = (552,137,779,168)
    text = readScreen(region)
    message = "PA: Ding-dong!"
    print(text)
    if message in text:
        while counter < 3:
            number = getRandomFloat(0.5,0.8)
            bot.press('x')
            time.sleep(number)
            bot.release('x')
            counter += 1
        inSafari = False
        return
    else:
        return



    
#Setting up the GUI
root = tk.Tk()
root.title("Bot Controller")
root.geometry("300x200")

# Create a dropdown menu for mode selection
mode_var = tk.StringVar()
mode_label = tk.Label(root, text="Select Mode:")
mode_label.pack()

mode_menu = ttk.Combobox(root, textvariable=mode_var)
mode_menu['values'] = ('Magikarp Farming', 'Magikarp Farming but at water', 'Mode 3')
mode_menu.current(0)
mode_menu.pack()

# Create buttons to start, stop, and pause the bot
start_button = tk.Button(root, text="Start", command=startBot)
start_button.pack()

pause_button = tk.Button(root, text="Pause", command=pauseBot)
pause_button.pack()

stop_button = tk.Button(root, text="Stop", command=stopBot)
stop_button.pack()

# Run the GUI loop
root.mainloop()
