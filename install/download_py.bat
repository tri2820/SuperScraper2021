@echo on

echo y|rmdir /s python_install

mkdir python_install

cd python_install

curl.exe -L --output python_install.zip --url https://www.python.org/ftp/python/3.7.9/python-3.7.9-embed-amd64.zip

rem curl.exe -L --output python_install.zip --url https://www.python.org/ftp/python/3.9.6/python-3.9.6-embed-amd64.zip

rem curl.exe -L --output python_install.zip --url https://www.python.org/ftp/python/3.7.10/python-3.7.10-embed-amd64.zip

echo Downloading

tar -xf python_install.zip

cd ..