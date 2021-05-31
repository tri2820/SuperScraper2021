@echo on

call %UserProfile%\Miniconda3\Scripts\activate.bat



call conda deactivate

call conda activate ScrapperTest


call python refreshbutton.py

