@echo on

cd ..

call %UserProfile%\Anaconda3\Scripts\activate.bat


call conda deactivate

echo /wait Waiting for conda

call conda create --name ScrapperTest -y

echo /wait Recreating Env

call conda activate ScrapperTest

call conda install pip -y

echo /wait Activating

call pip install -r requirements.txt

echo /wait Installing libs
