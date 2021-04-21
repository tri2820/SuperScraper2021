# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 13:06:45 2021

@author: tanav
"""

import tkinter as tk
import os
from Extractor.extractor import extract

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

r.geometry("500x500")
r.mainloop()
