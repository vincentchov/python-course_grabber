import json
import pathlib
from selenium import webdriver
from secrets import username, password
from downloader import Course
from downloader import Video
from downloader import clean_filename
from downloader import download_all_videos
from downloader import download_from_json
from downloader import video_links_to_file
from downloader import video_links_from_file
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def init_chrome_driver():
    """ Use Selenium to grab the direct links lecture videos """
    caps = DesiredCapabilities.CHROME
    caps['loggingPrefs'] = {'performance': 'ALL'}
    driver = webdriver.Chrome(desired_capabilities=caps)

    return driver


def get_video_links(driver, course_page_url, login_page):
    driver.get(login_page_url)
    username_form = driver.find_element_by_id("username")
    password_form = driver.find_element_by_id("password")

    username_form.send_keys(username)
    password_form.send_keys(password)

    driver.find_element_by_id("account-login").submit()

    # Once logged-in, go to the course page
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "courses"))
        )
    finally:
        # Visit the course page and pair up each lecture title with
        # their links
        driver.get(course_page_url)
        rows = driver.find_elements_by_class_name("lecture-link")
        lectures = [Video(row.text, row.get_property('href')) for row in rows]

    videos = []

    for lecture in lectures:
        # Visit each lecture and pair up the lecture title with the video's
        # direct link
        lecture_title = lecture.title
        lecture_link = lecture.url
        driver.get(lecture_link)
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "scrubber"))
            )
        finally:
            logs = driver.get_log('performance')

            for obj in logs:
                if "http://player.vimeo.com/external/" in obj['message']:
                    print("{}".format(lecture_name))
                    url_json = json.loads(obj['message'])['message']
                    direct_link = url_json['params']['request']['url']
                    videos.append(Video(lecture_title, direct_link))
                    break

    driver.close()
    print("Done grabbing the video links!")
    return videos


if __name__ == "__main__":
    login_page_url = "http://training.talkpython.fm/account/login"
    course_page_url = (
        "https://training.talkpython.fm/courses/details/" +
        "python-for-entrepreneurs-build-and-launch-your-online-business"
    )
    driver = init_chrome_driver()
    links = get_video_links(driver, course_page_url, login_page)
    download_all_videos(links)
