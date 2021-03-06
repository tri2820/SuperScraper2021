import requests
import zipfile

poppler_url = "https://github.com/oschwartz10612/poppler-windows/releases/download/v21.03.0/Release-21.03.0.zip"
poppler_zip_dir = "poppler.zip"
poppler_dir = "poppler"


chromeDriver_url = "https://chromedriver.storage.googleapis.com/94.0.4606.61/chromedriver_win32.zip"
chromeDriver_zip_dir = "chromedriver_win32.zip"
chromeDriver_dir = "chrome_driver"



# Detect OS
import os
import platform

system_name = platform.system()

print(f" System detected as {system_name}")

if system_name == "Darwin":
    chromeDriver_url = "https://chromedriver.storage.googleapis.com/94.0.4606.61/chromedriver_mac64.zip"
    chromeDriver_zip_dir = "chromedriver_mac64.zip"




print(" -- POPPLER INSTALL -- ")
r = requests.get(poppler_url, allow_redirects=True)
open(poppler_zip_dir, 'wb').write(r.content)

with zipfile.ZipFile(poppler_zip_dir, 'r') as zip_ref:
    zip_ref.extractall(poppler_dir)
# --


print(" -- CHROME DRIVER INSTALL -- ")
r = requests.get(chromeDriver_url, allow_redirects=True)
open(chromeDriver_zip_dir, 'wb').write(r.content)

with zipfile.ZipFile(chromeDriver_zip_dir, 'r') as zip_ref:
    zip_ref.extractall(chromeDriver_dir)
# --


print(" -- NLTK DRIVER INSTALL -- ")
import nltk
nltk.download('stopwords', download_dir='./nltk_data')
nltk.download('punkt', download_dir='./nltk_data')




"""
print("-- Test --")
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

CHROME_DRIVER_PATH = "chrome_driver/chromedriver.exe"

options = Options()
options.headless = False
options.add_argument("--log-level=3")
options.add_argument("--disable-logging")
options.add_argument("--disable-gpu")
options.add_argument("start-maximized")
chrome_options=options
driver = webdriver.Chrome(executable_path = CHROME_DRIVER_PATH, options=options)


driver.get("https://www.google.com/")
"""













# --