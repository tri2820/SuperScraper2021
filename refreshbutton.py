# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 13:06:45 2021

@author: tanav
"""

import tkinter as tk
import os
from Extractor.extractor import extract

from scraper_run import SpiderHandler

from Maintenance.Maintenance import clear_docs, delete_docs

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

r.geometry("500x500")
r.mainloop()
