# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 13:06:45 2021

@author: tanav
"""

import tkinter as tk
import os
from Extractor.extractor import extract

from scraper_run import SpiderHandler, run_scraper_traversal

from Maintenance.Maintenance import clear_docs, delete_docs

#from Scraper.get_fund_managers import run_test

#from Scraper import pdf_extraction

#from Scraper import  get_fund_managers

from Scraper.get_fund_managers import run_test

import matplotlib

import camelot

#from Scraper import settings

#from Scraper import pdf_extraction

#from Scraper.pdf_extraction import StringTest, ExtractTableHandler, TableExtraction, TableDataExtractor

spider_handler = SpiderHandler()


r = tk.Tk()
r.title("Super Scraper")

def refresh():
    r.destroy()
    os.popen("refreshbutton.py")
button_1 = tk.Button(r, text = "Refresh", command = refresh)
button_1.pack()

def exit():
    r.destroy()
button_2 = tk.Button(r, text = "Exit", command = exit)
button_2.pack()

#def extract():
    #os.popen("extractor.py")
button_3 = tk.Button(r, text = "Extract", command = extract)
button_3.pack()

button_4 = tk.Button(r, text = "Scrap", command = spider_handler.run_scraper)
button_4.pack()

button_5 = tk.Button(r, text = "Clear Database Docs", command = clear_docs)
button_5.pack()

button_6 = tk.Button(r, text = "Delete Database Docs", command = delete_docs)
button_6.pack()

button_7 = tk.Button(r, text = "Traverse test sites", command = run_scraper_traversal)
button_7.pack()

button_8 = tk.Button(r, text = "Extract pdf file data", command = run_test)
button_8.pack()

r.geometry("500x500")
r.mainloop()
