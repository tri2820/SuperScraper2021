@echo on

curl.exe --output Anaconda3-latest-Windows-x86_64.exe --url https://repo.anaconda.com/archive/Anaconda3-2021.05-Windows-x86_64.exe

echo /wait Downloading

start /wait "" Anaconda3-latest-Windows-x86_64.exe /InstallationType=JustMe /RegisterPython=0 /S /D=%UserProfile%\Anaconda3

call %UserProfile%\Anaconda3\Scripts\activate.bat

cd ..

call conda deactivate

call conda create --name ScrapperTest -y

call conda activate ScrapperTest

call conda install pip -y

echo /wait Installing pip

call pip install -r requirements.txt

pause



