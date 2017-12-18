import json
import pathlib
from urllib.request import urlretrieve
from selenium import webdriver
from secrets import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def get_video_links_mkennedy():
    """ Use Selenium to grab the direct links lecture videos """
    caps = DesiredCapabilities.CHROME
    caps['loggingPrefs'] = {'performance': 'ALL'}
    driver = webdriver.Chrome(desired_capabilities=caps)

    login_page_url = "http://training.talkpython.fm/account/login"
    driver.get(login_page_url)
    username_form = driver.find_element_by_id("username")
    password_form = driver.find_element_by_id("password")

    username_form.send_keys(mkennedy_username)
    password_form.send_keys(mkennedy_password)

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


def get_video_links_udemy():
    """ Use Selenium to grab the direct links lecture videos """
    caps = DesiredCapabilities.CHROME
    caps['loggingPrefs'] = {'performance': 'ALL'}
    driver = webdriver.Chrome(desired_capabilities=caps)
    login_page_url = "http://udemy.com"
    driver.get(login_page_url)
    driver.find_element_by_css_selector((
        "#udemy > div.c_header.c_header--v6.c_header--desktop.ud-angular-" +
        "loader.js-hellobar > div.c_header__inner > div.c_header__right >" +
        " div.dropdown.dropdown--login > require-auth > div > a"
    )).click()

    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "id_email"))
        )
    finally:
        username_form = driver.find_element_by_id("id_email")
        password_form = driver.find_element_by_id("id_password")

        username_form.send_keys(udemy_username)
        password_form.send_keys(udemy_password)

        driver.find_element_by_id("submit-id-submit").submit()

    # Once logged-in, go to the course page
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH,
                '//*[@id="udemy"]/div[2]/div[1]/div[4]/div[2]/div/div[1]/a'
            ))
        )
    finally:
        # Visit the course page and pair up each lecture title with
        # their links
        course_page_url = (
            "https://www.udemy.com/basic-dance-moves-for-guys/learn/v4/content"
        )
        driver.get(course_page_url)
        
    # Once you're on the course page, get all the lecture's names
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                '.curriculum-navigation__section'
            ))
        )
    finally:
        # Show all lectures and get them all
        sections = driver.find_elements_by_css_selector("[ng-click*=setOpenAll]")
        for section in sections:
            if "all sections" in section.text.lower():
                section.click()
        
        # Get the names and supposed links to each lecture
        rows = driver.find_elements_by_css_selector((
            ".lecture__item__link.fx-jsb"
        ))

    lectures = []
    
    lecture_names = [row.text.split("\n")[0] for row in rows]
    for current_lecture in lecture_names:
        # Refresh the links each time, visiting each video by lecture name
        # and recording their Udemy links
        driver.get(course_page_url)
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    '.curriculum-navigation__section'
                ))
            )
        finally:
            # Show all lectures and get them all
            sections = driver.find_elements_by_css_selector("[ng-click*=setOpenAll]")
            for section in sections:
                if "all sections" in section.text.lower():
                    section.click()
            
        link_names = (
            driver.find_elements_by_class_name("lecture__item__link__name")
        )
        link_pairs = [[x.get_attribute("textContent"), x] for x in link_names]

        title = current_lecture
        link_pair = [x for x in link_pairs if x[0] in title]
        link_pair[0][1].click()
        link = driver.current_url

        lectures.append([title, link])

    driver.close()
    print("Done grabbing the video links!")
    return lectures


def video_links_to_file(filename):
    """ Outputs all the lecture titles and direct links to a JSON file. """
    video_links = get_video_links()
    with open(filename, 'w') as json_data:
        json_data.write(json.dumps(video_links, indent=4, sort_keys=True))


def video_links_from_file(filename):
    """ Reads the JSON file that's already been populated. """
    if not pathlib.Path(filename).is_file():
        raise IOError("{} does not exist...".format(filename))
    else:
        with open(filename) as json_data:
            video_links = json.load(json_data)

        return video_links


def clean_filename(filename):
    """ Replaces illegal characters from filenames with underscores. """
    keep_chars = (' ', '.', '_', '-')
    chars = [c if c.isalnum() or c in keep_chars else '_' for c in filename]
    return "".join(chars).rstrip()


def download_all_videos(list_of_lectures, dest_folder):
    """ Takes the JSON and runs wget on all of the links. """
    pathlib.Path(dest_folder).mkdir(parents=True, exist_ok=True)
    length = len(list_of_lectures)
    i = 1
    for pair in list_of_lectures:
        filename = "{}.mp4".format(clean_filename(pair[0]))
        url = pair[1]
        print("({}/{}) Downloading '{}' as '{}'".format(i, length,
                                                        pair[0], filename))
        urlretrieve(url, "{}/{}".format(dest_folder, filename))
        i += 1

    print("Done!")


def download_udemy_videos(list_of_lectures, dest_folder):
    """ Takes the JSON and runs wget on all of the links. """
    caps = DesiredCapabilities.CHROME
    caps['loggingPrefs'] = {'performance': 'ALL'}
    driver = webdriver.Chrome(desired_capabilities=caps)
    login_page_url = "http://udemy.com"
    driver.get(login_page_url)
    driver.find_element_by_css_selector((
        "#udemy > div.c_header.c_header--v6.c_header--desktop.ud-angular-" +
        "loader.js-hellobar > div.c_header__inner > div.c_header__right >" +
        " div.dropdown.dropdown--login > require-auth > div > a"
    )).click()

    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "id_email"))
        )
    finally:
        username_form = driver.find_element_by_id("id_email")
        password_form = driver.find_element_by_id("id_password")

        username_form.send_keys(udemy_username)
        password_form.send_keys(udemy_password)

        driver.find_element_by_id("submit-id-submit").submit()

    # Once logged-in, go to the course page
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH,
                '//*[@id="udemy"]/div[2]/div[1]/div[4]/div[2]/div/div[1]/a'
            ))
        )
    finally:
        # Visit the course page and pair up each lecture title with
        # their links
        course_page_url = (
            "https://www.udemy.com/basic-dance-moves-for-guys/learn/v4/content"
        )
        driver.get(course_page_url)

    pathlib.Path(dest_folder).mkdir(parents=True, exist_ok=True)
    length = len(list_of_lectures)
    i = 1
    for pair in list_of_lectures:
        driver.get(pair[1])
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "vjs-play-progress"))
            )
        finally:
            logs = driver.get_log('performance')

            for obj in logs:
                if "https://udemy-assets-on-demand2.udemy.com" in obj['message']:
                    print("{}".format(lecture_name))
                    url_json = json.loads(obj['message'])['message']
                    direct_link = url_json['params']['request']['url']
                    break

            filename = "{}.mp4".format(clean_filename(pair[0]))
            url = direct_link
            print("({}/{}) Downloading '{}' as '{}'".format(i, length,
                                                            pair[0], filename))
            urlretrieve(url, "{}/{}".format(dest_folder, filename))
            i += 1

    print("Done!")


def download_from_json(filename, dest_folder):
    """ Downloads all videos from an existing JSON file. """
    links = video_links_from_file(filename)
    download_all_videos(links, dest_folder)

get_video_links_udemy()
