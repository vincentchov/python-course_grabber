import os
import sys
import requests
import json
import platform
from downloader import Course
from downloader import Video
from downloader import clean_filename
from downloader import download_all_videos
from downloader import download_from_json
from bs4 import BeautifulSoup
from collections import namedtuple
from selenium import webdriver
from logger import logger


def init_driver():
    if 'microsoft' in platform.platform().lower():
        # You're running in Windows Subsystem for Linux,
        # so use xvfb and pyvirtualdisplay to simulate headless mode
        import pyvirtualdisplay
        display = pyvirtualdisplay.Display(visible=0, size=(1920, 1080))
        display.start()
    else:
        # Otherwise just run headless mode
        os.environ['MOZ_HEADLESS'] = '1'

    return webdriver.Firefox()


if __name__ == "__main__":
    driver = init_driver()
