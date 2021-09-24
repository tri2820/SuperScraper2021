@echo on

call download_py.bat

echo -- Downloaded Python --

call python_install\python python_install.py

echo -- Installed Pip --

call python_install\Scripts\pip install -r requirements.txt -q -q

echo -- Installed Requirements --

call python_install\python python_files_install.py

echo -- Installed Data Files --

rem pause









