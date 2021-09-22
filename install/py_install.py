import requests
import zipfile

poppler_url = "https://github.com/oschwartz10612/poppler-windows/releases/download/v21.03.0/Release-21.03.0.zip"
poppler_zip_dir = "poppler.zip"
poppler_dir = "poppler"


chromeDriver_url = "https://chromedriver.storage.googleapis.com/92.0.4515.43/chromedriver_win32.zip"
chromeDriver_zip_dir = "chromedriver_win32.zip"
chromeDriver_dir = "chrome_driver"



# Detect OS
import os
import platform

system_name = platform.system()

print(f" System detected as {system_name}")

if system_name == "Darwin":
    chromeDriver_url = "https://chromedriver.storage.googleapis.com/92.0.4515.107/chromedriver_mac64.zip"
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

































# --