import urllib.request
import zipfile

import os
import platform

import shutil


py_install_dir = "python_install"


pip_url = "https://bootstrap.pypa.io/get-pip.py"
pip_py_file = "get-pip.py"

print(" -- PIP INSTALL -- ")
#r = requests.get(pip_url, allow_redirects=True)
r = urllib.request.urlopen(pip_url)
open(py_install_dir + "\\" + pip_py_file, 'wb').write(r.read())#.content


# Import file just created
import importlib  
get_pip = importlib.import_module("get-pip")

try:
    # Install pip
    get_pip.main()
except:
    print("Er -- ")


# Remove zip file

py_zip_dir = "python_install\\python37.zip"
py_zip_dir_1 = "python_install\\python37_.zip"


with zipfile.ZipFile(py_zip_dir, 'r') as zip_ref:
    zip_ref.extractall(py_zip_dir_1)
# --

os.chmod(py_zip_dir, 0o777)
os.remove(py_zip_dir)


os.rename(py_zip_dir_1, py_zip_dir)







# Move requisite files over

shutil.copy("python37._pth", py_install_dir)

shutil.copy("python39._pth", py_install_dir)

shutil.copy("sitecustomize.py", py_install_dir)

print("PROCESS COMPLETED")






# --