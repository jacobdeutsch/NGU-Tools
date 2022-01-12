# NGU Cooking Automator
# AutoCook will automatically run the cooking minigame.  With 7 ingredients it runs in about 90 seconds.
# Efficiency is high but not guaranteed to be 100% since the OCR is not perfect and fails for certain values.
# Adjust the user input for numIngs for the number of ingredients you currently have.


# Requires PyAutoGUI, Pillow, OpenCV, numpy, scipy re, and PyTesseract plus the executables https://tesseract-ocr.github.io/tessdoc/Downloads (made with 64bit 5.0.0.20211201 from UB Mannheim)
# Note, the locations for buttons and screenshots assume that the game is in the default location, on a 1920x1080 screen with a game resolution of 960x600.
# Numbering for ingredients is left column 0->3 and then right column 4->7
# Depending on the number of ingredients you have adjust the line instantiating numIngs

import pyautogui, cv2, pytesseract, re
import numpy as np
from PIL import ImageGrab
from scipy.signal import argrelextrema

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Only User Input HERE! 8th
numIngs = 8     # set to the number of ingredients you have between 6 and 8.  I do not check or validate this input...

# step 0, set plus and minus coords
plusx = [1048, 1048, 1048, 1048, 1328, 1328, 1328, 1328]
plusy = [354, 444, 534, 624, 354, 444, 534, 624]
minusx = [1048, 1048, 1048, 1048, 1328, 1328, 1328, 1328]
minusy = [378, 468, 559, 648, 378, 468, 559, 648]

# step 1, define functions
def zeroingredient(ingredientNum):  # zeroes ingredient passed to it (0 through 7)
    pyautogui.click(minusx[ingredientNum], minusy[ingredientNum], 20, 0.020)  # click the minus button for the ingredient 20 times with a 20 ms pause between clicks

def setingredient(ingredientNum, amount):   # set ingredient to a certain amount.  assumes ingredient starts at 0
    pyautogui.click(plusx[ingredientNum], plusy[ingredientNum], amount, 0.020)  # click the plus button for the ingredient amount times with a 20 ms pause between clicks

def getmealeff():   # gets meal efficiency
    cap = ImageGrab.grab(bbox =(1190, 707, 1260, 730))  # capture meal efficiency and set bounding box around meal efficiency
    tesstr = pytesseract.image_to_string(cv2.cvtColor(np.array(cap), cv2.COLOR_BGR2GRAY), lang = 'eng')     # run OCR
    effRegex = re.compile(r'[0-9.]+')   # create regex to find all digits and decimal points
    if re.findall(effRegex, tesstr) == []:
        return -1       # if OCR fails, return -1
    else:
        return(float(re.findall(effRegex, tesstr)[0]))      # return value from regex



# step 2, set all cooking supplies to 0
for i in range(0,numIngs):    # 8th change 7 to 8
    zeroingredient(i)

# step 3, run through each ingredient and record meal efficiencies
efficiencies = np.zeros((numIngs, 21))    # 8th change 7 to 8, this array contains the efficiencies, efficiencies[ingredient#,amount of ingredient]

currentEff = getmealeff()
for ingNum in range(0, efficiencies.shape[0]):   # set the 0 efficiency for all ingredients
    efficiencies[ingNum][0] = currentEff

for ingNum in range(0, efficiencies.shape[0]):   # now set the efficiency for all ingredients for all ingredient amounts
    for amount in range(1, 21):
        pyautogui.click(plusx[ingNum], plusy[ingNum])
        efficiencies[ingNum][amount] = getmealeff()
    zeroingredient(ingNum)

 # step 4, find ingredient pairs
ingPairs = np.full((4, 2), -1)     # create pairs 2D list.  ingPairs[pair number 0-3][ingNum]

for ingNum in range(0, efficiencies.shape[0]):
    if np.any(np.isin(ingPairs, ingNum)):       # check if the ingNum is already in a pair and skip if true
        continue
    for ingNum2 in range(0, efficiencies.shape[0]):
        if ingNum2 == ingNum:       # check if ingNum and ingNum2 are the same and skip if they are.  Dont want to compare an ingredient to itself
            continue
        if np.array_equal(efficiencies[ingNum], efficiencies[ingNum2]) == True:     # if ingNum and ingNum2 have the same efficiencies
            for i in range(0, len(ingPairs)):
                if ingPairs[i][0] == -1:    # find the first unused pair
                    ingPairs[i][0], ingPairs[i][1] = ingNum, ingNum2    #set the pairs
                    break


 # step 5, find local max
if ingPairs[0][0] != -1:
    pairAMax = argrelextrema(efficiencies[ingPairs[0][0]], np.greater)[0]
if ingPairs[1][0] != -1:
    pairBMax = argrelextrema(efficiencies[ingPairs[1][0]], np.greater)[0]
if ingPairs[2][0] != -1:
    pairCMax = argrelextrema(efficiencies[ingPairs[2][0]], np.greater)[0]
if ingPairs[3][0] != -1:
    pairDMax = argrelextrema(efficiencies[ingPairs[3][0]], np.greater)[0]


 # step 6, run ingredient pairs to find paired max
maxEffA = [-1, -1, -1]   # max efficiency placeholder [Amount Ing 0, Amount Ing 1, eff]
if ingPairs[0][0] != -1:    # for pair A
    for max in pairAMax:
        setingredient(ingPairs[0][0], max)
        for amount in range(0, 21):
            eff = getmealeff()
            if eff > maxEffA[2]:
                maxEffA[0], maxEffA[1], maxEffA[2] = max, amount, eff
            pyautogui.click(plusx[ingPairs[0][1]], plusy[ingPairs[0][1]])
        zeroingredient(ingPairs[0][0])
        zeroingredient(ingPairs[0][1])

maxEffB = [-1, -1, -1]   # max efficiency placeholder [Amount Ing 0, Amount Ing 1, eff]
if ingPairs[1][0] != -1:    # for pair B
    for max in pairBMax:
        setingredient(ingPairs[1][0], max)
        for amount in range(0, 21):
            eff = getmealeff()
            if eff > maxEffB[2]:
                maxEffB[0], maxEffB[1], maxEffB[2] = max, amount, eff
            pyautogui.click(plusx[ingPairs[1][1]], plusy[ingPairs[1][1]])
        zeroingredient(ingPairs[1][0])
        zeroingredient(ingPairs[1][1])

maxEffC = [-1, -1, -1]   # max efficiency placeholder [Amount Ing 0, Amount Ing 1, eff]
if ingPairs[2][0] != -1:    # for pair C
    for max in pairCMax:
        setingredient(ingPairs[2][0], max)
        for amount in range(0, 21):
            eff = getmealeff()
            if eff > maxEffC[2]:
                maxEffC[0], maxEffC[1], maxEffC[2] = max, amount, eff
            pyautogui.click(plusx[ingPairs[2][1]], plusy[ingPairs[2][1]])
        zeroingredient(ingPairs[2][0])
        zeroingredient(ingPairs[2][1])

maxEffD = [-1, -1, -1]   # max efficiency placeholder [Amount Ing 0, Amount Ing 1, eff]
if ingPairs[3][0] != -1:    # for pair D
    for max in pairDMax:
        setingredient(ingPairs[3][0], max)
        for amount in range(0, 21):
            eff = getmealeff()
            if eff > maxEffD[2]:
                maxEffD[0], maxEffD[1], maxEffD[2] = max, amount, eff
            pyautogui.click(plusx[ingPairs[3][1]], plusy[ingPairs[3][1]])
        zeroingredient(ingPairs[3][0])
        zeroingredient(ingPairs[3][1])

# step 7, find the max of any unpaired ingredients
unpairedIngredients = list(range(numIngs))     # 8th add a 7 to this list, list all ingredients
for i in range(0, 4):       # iterate through ingPairs and remove all the paired values from unpairedIngredients
    for j in range(0, 2):
        if ingPairs[i][j] != -1:
            unpairedIngredients.remove(ingPairs[i][j])      

unpairedMax = {}
for i in unpairedIngredients:       # go through each unpaired ingredient and find the absolute maximum and record the max's index in unpairedMax
    unpairedMax[i] = np.argmax(efficiencies[i])     # sets key to ingNum and value to maximums index

 # step 8, set ingredients to correct amounts

# start by setting pairs
if ingPairs[0][0] != -1:
    setingredient(ingPairs[0][0], maxEffA[0])
    setingredient(ingPairs[0][1], maxEffA[1])

if ingPairs[1][0] != -1:
    setingredient(ingPairs[1][0], maxEffB[0])
    setingredient(ingPairs[1][1], maxEffB[1])

if ingPairs[2][0] != -1:
    setingredient(ingPairs[2][0], maxEffC[0])
    setingredient(ingPairs[2][1], maxEffC[1])

if ingPairs[3][0] != -1:
    setingredient(ingPairs[3][0], maxEffD[0])
    setingredient(ingPairs[3][1], maxEffD[1])

for key in unpairedMax:
    setingredient(key, unpairedMax[key])