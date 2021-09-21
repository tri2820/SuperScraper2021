#import dateparser
import datetime
import re
import io
import os

import random


import PyPDF2
import pandas as pd
#import camelot

from pdf2image import convert_from_path, convert_from_bytes



import requests


from PIL import Image


class PdfImageExtractor():

    pdfs_path = 'pdfs/'
    images_path = 'images/pdf-page-images'

    def get_PDF_files(self):
        print('--- Getting PDF Rel Paths ---')

        rel_paths = []
        file_names = []
        
        # If directory does not exist create it
        os.makedirs(self.pdfs_path, exist_ok=True)
        
        # Get files
        for dirpath, dirnames, filenames in os.walk(self.pdfs_path):
            rel_paths = [dirpath + x for x in filenames]
            file_names = filenames
            #print(rel_paths)
        # --
        return rel_paths, file_names
    # --

    def extract_images(self):
        rel_paths, file_names = self.get_PDF_files()
        # If directory does not exist create it
        os.makedirs(self.images_path, exist_ok=True)
        # Put images in folder
        for rel_path, file_name in zip(rel_paths, file_names):
            images = convert_from_path(rel_path, output_folder = self.images_path, fmt = 'jpeg', output_file = file_name.split('.pdf')[0])
        # --
    # --

    def train_test_file_split(self, images_path, xml_path, train_path, test_path, ratio):
        img_paths = []
        img_names = []
        
        # If directorys does not exist create it
        os.makedirs(images_path, exist_ok=True)
        os.makedirs(xml_path, exist_ok=True)
        os.makedirs(train_path, exist_ok=True)
        os.makedirs(test_path, exist_ok=True)
        
        # Images
        for dirpath, dirnames, filenames in os.walk(images_path):
            img_paths = [dirpath + '\\' + x for x in filenames]
            img_names = filenames
        # --
        xml_paths = []
        xml_names = []
        # Labels
        for dirpath, dirnames, filenames in os.walk(xml_path):
            xml_paths = [dirpath + '\\' + x for x in filenames]
            xml_names = filenames
        # --

        img_values = {x.split('.jpg')[0] : [x,y] for x, y in zip(img_names, img_paths)}
        xml_values = {x.split('.xml')[0] : [x,y] for x, y in zip(xml_names, xml_paths)}

        test_number = (len(xml_values) * ratio) // 1

        random_values = random.sample(xml_values.keys(),int(test_number))

        print(f'\nTest Number: {test_number} \n')
        print(f'\nTest List: {random_values} \n')

        for xml_name in xml_values:
            if xml_name in img_values:
                img = Image.open(img_values[xml_name][1])
                xml_content = open(xml_values[xml_name][1]).read()

                # Test path
                if xml_name in random_values:
                    img.save(test_path + '\\' + img_values[xml_name][0], 'JPEG')
                    xml_save = open(test_path + '\\' + xml_values[xml_name][0], 'w')
                    xml_save.write(xml_content)
                    xml_save.close()
                else:# Train path
                    img.save(train_path + '\\' + img_values[xml_name][0], 'JPEG')
                    xml_save = open(train_path + '\\' + xml_values[xml_name][0], 'w')
                    xml_save.write(xml_content)
                    xml_save.close()
                # --
            # --
        # --
    # --
# --
















































# --
