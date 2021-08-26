@echo on

call %UserProfile%\Anaconda3\Scripts\activate.bat

call conda deactivate

echo /wait Waiting for conda

call conda create --name ScrapperTest -y

echo /wait Recreating Env

call conda activate ScrapperTest

echo /wait Activating
