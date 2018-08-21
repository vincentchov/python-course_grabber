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
from downloader import video_links_to_file
from secrets import egghead_secrets
from bs4 import BeautifulSoup
from collections import namedtuple
from selenium import webdriver
from logger import logger


username = egghead_secrets["username"]
password = egghead_secrets["password"]


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


def login(driver, login_page_url):
    driver.get(login_page_url)

    username_form = driver.find_element_by_id("user_email")
    password_form = driver.find_element_by_id("user_password")

    username_form.send_keys(username)
    password_form.send_keys(password)

    driver.find_element_by_name("commit").submit()


def get_course_video_pages(driver, course_url):
    driver.get(course_url)
    soup = BeautifulSoup(driver.page_source, "lxml")
    name = soup.find("span", class_="f1-ns").text

    # Get links to pages where the videos are
    links = [
        Video(link.text, course_url + link["href"])
        for link
        in soup.findAll("a", class_ = "w-100")
        if link and link["href"].startswith("/lesson") and link.find("h2")
    ]

    course = Course(name, course_url, links)

    return course


def get_direct_links(driver, course):
    direct_links = []

    for page in course.videos:
        driver.get(page.url)
        driver.find_element_by_css_selector("div.db-1").click()
        direct_link = Video(page.name, driver.current_url)

    return Course(course.name, course.url, direct_links)


def download(course):
    course_with_direct_links = get_direct_links(course)
    direct_links = course_with_direct_links.videos
    filename = clean_filename(course_with_direct_links.name)
    download_all_videos(direct_links, filename)


if __name__ == "__main__":
    login_page_url = "https://egghead.io/users/sign_in"
    course_url = (
        "https://egghead.io/courses/json-web-token-jwt"
        "-authentication-with-node-js-and-auth0"
    )
    driver = init_driver()
    login(driver, login_page_url)
    course = get_course_video_pages(driver, course_url)
    video_links_to_file(course.videos,
                        "{}.json".format(clean_filename(course.name)))
    # download(course)
