from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import json

with open('config.json') as config_file:
    config = json.load(config_file)
pth = config['driver_path']
driver_service = Service(executable_path=pth)
driver = webdriver.Chrome(service=driver_service)
actions = ActionChains(driver)

# First get the list of possible words
driver.get("https://raw.githubusercontent.com/lorenbrichter/Words/master/Words/en.txt")
dd = driver.find_element(by=By.XPATH, value="/html/body/pre")
dta = dd.text
manifest = (dta.split('\n'))

# Only include them if they have five letters
manifest = [ word for word in manifest if len(word) == 5 ]
originalManifest = manifest.copy()

# Updates the manifest using the process of elimination
def updateList(wd, pos, letter, letter_state):
    global manifest
    if(letter_state == 'flip-back wp-cell-absent'):          
            #if else needed because like in the word 'sissy' the first 's' will show
            #as present and the second 's' will show as absent
            #we still want to keep the words with s in them, not delete them because the second
            #'s was absent
        manifest = [word for word in manifest if not word[pos] == letter ]     
        if wd.count(letter) == 1:
            manifest = [word for word in manifest if not letter in word]
    elif(letter_state == 'flip-back wp-cell-present'):
        manifest = [ word for word in manifest if not letter == word[pos] ]
        manifest = [ word for word in manifest if letter in word ]
    elif(letter_state == 'flip-back wp-cell-correct'):
        manifest = [ word for word in manifest if letter == word[pos] ]

# aka https://wordplay.com/
driver.get("https://wordplay.com/")
time.sleep(1)

def playGame():
    time.sleep(5)
    global manifest 
    manifest = originalManifest.copy()
    try_word = "stare"
    for letter in try_word:
        actions.send_keys(letter)
        actions.perform()
        time.sleep(1/4)
    entertime = driver.find_element(by=By.TAG_NAME, value="body")
    entertime.send_keys(Keys.RETURN)
    time.sleep(5)
    for row in range(1,7):       
        ended_or_not = driver.find_element(by = By.XPATH, value = '/html/body/div/div/div[1]/div[1]/div/div[2]/div/div/div[1]').text

        # If the number of tries is over (not likely because the bot works really well) or we have guessed the correct word
        if(ended_or_not[0] != 'Q'):
            break    
        for let in range(1,6):           
            letter = (driver.find_element(by=By.XPATH, value="/html/body/div/div/div[1]/div[1]/div/div[1]/div[2]/div/div/div[%s]/div[%s]/div/div[1]/div" %(str(row), str(let))).text).lower()
            letter_state = driver.find_element(by=By.XPATH, value="/html/body/div/div/div[1]/div[1]/div/div[1]/div[2]/div/div/div[%s]/div[%s]/div/div[2]"%(str(row), str(let))).get_attribute("className")
            updateList(try_word, let-1, letter, letter_state)
        
        # If for some reason the manifest is empty (usually happens if the dictionary has become outdated)
        # we will just try "story"
        if(len(manifest) == 0):
            try_word = "story"
        else:
            try_word = manifest[0]
        for letter in try_word:
            actions.send_keys(letter)
            actions.perform()
            time.sleep(1/4)
        entertime = driver.find_element(by=By.TAG_NAME, value="body")
        entertime.send_keys(Keys.RETURN)
        time.sleep(5)
    entertime.send_keys(Keys.RETURN)
    playGame()

playGame()
