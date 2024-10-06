import time
from pynput import keyboard,mouse
from pynput.keyboard import Key

class Bot:
    def __init__(self,startKey ='1', stopKey = '2'):
        self.running = False
        self.keyboardController = keyboard.Controller()
        self.mouseController = mouse.Controller()
    def start(self):
        self.running = True
        print("running")

    def stop(self):
        self.running = False

    def moveUp(self):
        self.press(Key.up)     

    def moveDown(self):
        print("moving down")
        self.press(Key.down)
        
    def moveRight(self):
        print("moving right")
        self.press(Key.right)
        
    def moveLeft(self):
        self.press(Key.left)
        
    def press(self,button):
        self.keyboardController.press(button)

    def release(self,button):
        self.keyboardController.release(button)

    def leftClick(self, x_range, y_range):
        self.mouseController.position = (x_range, y_range)
        time.sleep(0.1)
        self.mouseController.click(mouse.Button.left)
        time.sleep(0.1)
        


  
