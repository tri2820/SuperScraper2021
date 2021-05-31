@echo on

curl.exe --output Miniconda3-latest-Windows-x86_64.exe --url https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe

echo /wait Downloading

start /wait "" Miniconda3-latest-Windows-x86_64.exe /InstallationType=JustMe /RegisterPython=0 /S /D=%UserProfile%\Miniconda3

call %UserProfile%\Miniconda3\Scripts\activate.bat

cd ..

call conda deactivate

call conda create --name ScrapperTest --file requirements.txt --channel default --channel conda-forge --channel anaconda -y

call conda activate ScrapperTest

pause



