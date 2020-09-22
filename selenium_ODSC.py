import time
import re

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from IPython.display import clear_output
import subprocess


class connect:
    
    def __init__(self, url, option=None):
                
        with open ('ODSC_credentials.txt', "r") as myfile:
            creds = myfile.read().splitlines()
        
        self.username = creds
        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference("browser.privatebrowsing.autostart", True)

        options = Options()
        if isinstance(option, str):
            options.add_argument(option)

        self.driver = webdriver.Firefox(firefox_profile=firefox_profile,
                                        executable_path='/home/johndoe/jetX/geckodriver',
                                        options=options)
        self.driver.get(url)

    def login2menu(self):
        
        login = self.driver.find_elements_by_xpath(
            "//div[contains(@class, 'two-btns')]/a[@class='img-container']"
        )
        login = [el for el in login if el.text == 'Login']
        login[0].click()

        user = self.driver.find_element_by_name("LoginEmail")
        user.send_keys(self.username)

        login = self.driver.find_element_by_xpath(
                    "//button[contains(@class, 'btn btn-darkgrey')]"
                )
        login.click()

        self.remove_obscure()

        lobby = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'ext-content-area lobby-3d')]/div[@class='ext-content']")))
        lobby.click()

        self.remove_obscure()

        menu = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'entry-view')]/a[@onclick='webinarsInner(406);']")))
        menu.click()

        sub_menu = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'col-sm-12 borderbox')]/ul[@class='nav nav-tabs']/li[@id='webinar-group-2945']")))
        sub_menu.click()

    def remove_obscure(self):
        try:
            obscure = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH,"//div[@class='modal fade vjf-modal in']"+
                                                                                                                                             "//div[@class='modal-dialog']//div[@class='modal-content']"+
                                                                                                                                             "//div[@class='modal-header']//button[@class='close']")))
            self.driver.execute_script("arguments[0].click();", obscure)
            time.sleep(3)
        except:
            pass

    def get_replays(self):
        
        self.plays = self.driver.find_elements_by_xpath(
            "//a[contains(@class, 'track-btn-click btn btn-default play-webinar')]"
        )
        self.files = list()
        self.links = list()
        for idx,play in enumerate(self.plays):
            self.files.append(play.get_attribute('data-title'))
            self.links.append(play.get_attribute('data-url').replace('?autoplay=1',''))
            if idx+1<=5:
                print(f"{idx}. {play.get_attribute('data-title')} - {play.get_attribute('data-url').replace('?autoplay=1','')} \n")
                
    def download2drive(self,file_dl):
        
        format_ = 'bestvideo+bestaudio'
        error_code_404 = 'ERROR: Unable to download webpage'
        error_code_noplaylist = 'This playlist does not exist'

        if subprocess.call("test -e '{}'".format(file_dl), shell=True) == 1:
            subprocess.call("touch '{}'".format(file_dl), shell=True)
        track_dl = [line.strip() for line in open(f"./{file_dl}").readlines()]

        for file,link in zip(self.files,self.links):

            if link in track_dl:
                continue

            print(f'Processing: {file}  -  {link}')

            path = f"~/sharedrives/ODSC_Event/Material/{file}/".replace(' ','_').replace('&','and').replace('(','').replace(')','')
            
            bashCommand_dl = f'youtube-dl -f {format_} {link}'
            bashCommand_mkdir = f'mkdir {path}'
            bashCommand_mv = f'mv *.mp4 {path}'
            
            _,error = self.commander(bashCommand_dl)
            
            if error_code_404.encode() in error or error_code_noplaylist.encode() in error:
                print('Unable to download file - Skipping this link \n')
                continue
            else:
                _,_ = self.commander(bashCommand_mkdir)
                _,_ = self.commander(bashCommand_mv)
                print(f'Copied downloaded file into {path} \n')

                file = open(file_dl,"a")
                file.write(f'\n{link}')
                file.close()
            
            clear_output()
            
    def commander(self, command):
        
        print(f'Running Command: {command}')
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()

        return output, error
            
    def close(self):
        
        self.driver.close()
