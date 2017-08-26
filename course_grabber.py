import json
from selenium import webdriver
from secrets import username, password
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def get_video_links():
    caps = DesiredCapabilities.CHROME
    caps['loggingPrefs'] = {'performance': 'ALL'}
    driver = webdriver.Chrome(desired_capabilities=caps)
    
    login_page_url = "http://training.talkpython.fm/account/login"
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
        course_page_url = (
            "https://training.talkpython.fm/courses/details/" + 
            "python-for-entrepreneurs-build-and-launch-your-online-business"
        )
        driver.get(course_page_url)
        rows = driver.find_elements_by_class_name("lecture-link")
        lectures = [(row.text, row.get_property('href')) for row in rows]
    
    videos = []
    
    for lecture in lectures:
        # Visit each lecture and pair up the lecture title with the video's
        # direct link
        lecture_title = lecture[0]
        lecture_link = lecture[1]
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
                    videos.append((lecture_title, direct_link))
                    break

    driver.close()
    print("Done grabbing the video links!")
    return videos


def video_links_to_file(filename):
    """ Outputs all the lecture titles and direct links to a JSON file. """
    video_links = get_video_links()
    with open(filename, 'w') as json_data:
        json_data.write(json.dumps(video_links, indent=4, sort_keys=True))


def video_links_from_file(filename):
    """ Reads the JSON file that's already been populated. """
    with open(filename) as json_data:
        video_links = json.load(json_data)
    return video_links


