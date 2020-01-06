"""
This Browser class provides helper functions to make an easily-programatically-controlled browser
"""

import pickle
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class Browser:

    def __init__(self,enable_headless_mode=True,headless_resolution=(1920,1080)):
        self.enable_headless_mode = enable_headless_mode
        chrome_options = Options()

        if enable_headless_mode:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument(f"--window-size={headless_resolution[0]},{headless_resolution[1]}")

        self.driver = webdriver.Chrome(options=chrome_options)

    def write_page_source(self,path):
        f = open(path,'w')
        f.write(self.driver.page_source)
        f.close()

    def is_driver_init(self):
        """
        Checks to see that the driver object is an initialized Selenium Webdriver

        :return: Boolean on if the driver object is initalized
        """
        return len(self.driver.find_elements_by_id("...")) != 0

    def extract_text_from_element(self,selenium_element):
        return selenium_element.text

    def wait_for_page_load(self,keywordToFind):
        """
        Returns when page source is fully loaded based on finding a keyword

        :param: keywordToFind: needle to find in page source to signify page fully loaded
        """
        while True:
            if keywordToFind in self.driver.page_source:
                break
            time.sleep(0.3)

    def load_cookies(self,cookie_content):
        """
        Loads cookie data into Selenium WebDriver object (browser)

        :param cookie_content: content obtained from dump_cookies()
        """

        cookies = pickle.loads(cookie_content)
        for cookie in cookies:
            self.driver.add_cookie(cookie)


    def dump_cookies(self):
        """
        Dumps all cookie content from browser
        :return cookie content of Selenium WebDriver object (browser)
        """
        cookie_content = pickle.dumps(self.driver.get_cookies())
        return cookie_content

    def take_full_page_screenshot(self,url,path,waitFuncArg=None):
        """
        Source: https://stackoverflow.com/questions/51653344/taking-screenshot-of-whole-page-with-python-selenium-and-firefox-or-chrome-headl

        Takes a full page screenshot of url and saves it to a file path

        :param url: string, url of the page you want a full screenshot of
        :param path: path to save screenshot image
        :param waitFuncArg: argument to waitFunc
        """
        def wait_for_page_load(driver,keywordToFind):
            if waitFuncArg is None:
                time.sleep(3)
            else:
                while True:
                    if keywordToFind in driver.page_source:
                        break
                    time.sleep(0.3)

        chrome_options = Options()
        chrome_options.add_argument("--headless")

        # Load page for the first time to get scrollHeight
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        wait_for_page_load(driver,waitFuncArg)

        # get scrollHeight
        height = driver.execute_script(
            "return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight )")
        # close browser
        driver.close()

        # Open another headless browser with height extracted above
        chrome_options.add_argument(f"--window-size=1920,{height}")
        chrome_options.add_argument("--hide-scrollbars")

        driver = webdriver.Chrome(options=chrome_options)

        driver.get(url)

        wait_for_page_load(driver,waitFuncArg)

        # save screenshot to file path
        driver.save_screenshot(path)
        driver.close()

    def find_elements_by_all(self,identifier):
        find_elements_dict = {}

        find_elements_dict['name'] = self.driver.find_elements_by_name(identifier)
        find_elements_dict['tag_name'] = self.driver.find_elements_by_tag_name(identifier)
        find_elements_dict['id'] = self.driver.find_elements_by_id(identifier)
        find_elements_dict['class_name'] = self.driver.find_elements_by_class_name(identifier)
        find_elements_dict['css_selector'] = self.driver.find_elements_by_css_selector(identifier)
        find_elements_dict['partial_link_text'] = self.driver.find_elements_by_partial_link_text(identifier)
        find_elements_dict['link_text'] = self.driver.find_elements_by_link_text(identifier)

        return find_elements_dict