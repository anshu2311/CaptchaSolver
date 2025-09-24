# config.py
import os
import time
import random
import cv2
import pytesseract
import numpy as np
from PIL import Image, ImageFilter
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Get the current directory (where your main script is)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Set up paths
TESSERACT_PATH = os.path.join(BASE_DIR, "tesseract", "tesseract.exe")
CHROMEDRIVER_PATH = os.path.join(BASE_DIR, "chromedriver-win64", "chromedriver.exe")

# Configure pytesseract
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
