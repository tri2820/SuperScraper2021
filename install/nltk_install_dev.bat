@echo on

mkdir nltk_data

echo /wait Creating nltk_data

call %UserProfile%\Anaconda3\Scripts\activate.bat

call conda deactivate

call conda activate ScrapperTest

echo /wait Activating

call python nltk_install.py

echo /wait Downloading nltk data



