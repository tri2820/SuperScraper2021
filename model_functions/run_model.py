

import os
import io

import PyPDF2
import pandas as pd

from pdf2image import convert_from_path, convert_from_bytes

import requests

from PIL import Image

import camelot

# Big boi varaibles

setup_install = False

CUSTOM_MODEL_NAME = 'pdf_table_model_ssd_mobilenet_v2_640x640'
PRETRAINED_MODEL_NAME = 'ssd_mobilenet_v2_fpnlite_640x640_coco17_tpu-8'
PRETRAINED_MODEL_URL = 'http://download.tensorflow.org/models/object_detection/tf2/20200711/ssd_mobilenet_v2_fpnlite_640x640_coco17_tpu-8.tar.gz'

TF_RECORD_SCRIPT_NAME = 'generate_tfrecord.py'
LABEL_MAP_NAME = 'label_map.pbtxt'




#def detect_tables():

    #camelot.read_pdf(filepath=pdf_file, flavor="stream", table_areas=interesting_areas)

# --




























# --
