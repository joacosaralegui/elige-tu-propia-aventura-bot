"""
    Choreado de https://jon-e.net/blog/2019/07/23/Automating-Poll-Tweets-In-The-New-Layout-Hellscape/
    Dura lo que dure la interfaz de Twitter como está o actualizen la API o tweepy para incluir encuestas
"""

import traceback
import time 
import os

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select

class URL:
    TWITTER = 'http://twitter.com'
    TWITTER_STATUS = 'https://twitter.com/botamoud/status/'

class Constants:
    USERNAME = os.environ.get("user")
    PASSWORD = os.environ.get("password")
    GLOBAL_ENTRY_Q = '#globalentry'


class TwitterLocator:
    # login stuff    
    login_btn        = (By.XPATH, "//span[text()='Log in']")
    username         = (By.NAME, "session[username_or_email]")
    password         = (By.NAME, "session[password]")
    login_confirm    = (By.XPATH, "//span[text()='Log in']")

    # tweet stuff
    outer_tweet_box  = (By.CLASS_NAME, 'public-DraftStyleDefault-block')
    tweet_box        = (By.CLASS_NAME, "public-DraftEditor-content")
    tweet_btn        = (By.XPATH, "//span[text()='Tweet']")
    another_tweet    = (By.XPATH, "//div[@aria-label='Reply']")

    # challenge
    challenge_response = (By.ID, 'challenge_response')
    challenge_submit = (By.ID, 'email_challenge_submit')

    # poll stuff
    poll_btn         = (By.XPATH, '//div[@aria-label="Add poll"]')
    option_one       = (By.NAME, 'Choice1')
    option_two       = (By.NAME, 'Choice2')
    extra_opts       = (By.XPATH, '//div[@aria-label="Add a choice"]')
    option_three     = (By.NAME, 'Choice3')
    days             = (By.ID, 'Days')
    hours            = (By.ID, 'Hours')
    minutes          = (By.ID, 'Minutes')

    # etc.
    search_input     = (By.ID, "search-query")
    like_btn         = (By.CLASS_NAME, "HeartAnimation")
    latest_tweets    = (By.PARTIAL_LINK_TEXT, 'Latest')

class PollBot(object):

    def __init__(self):
        self.locator_dictionary = TwitterLocator.__dict__
        self.chrome_options = Options()
        self.chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--no-sandbox")
        self.browser = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),chrome_options=self.chrome_options)
        self.browser.get(URL.TWITTER)
        self.timeout = 2
    
    def _find_element(self, *loc):
        return self.browser.find_element(*loc)

    def __getattr__(self, what):
        try:
            if what in self.locator_dictionary.keys():
                try:
                    element = WebDriverWait(self.browser, self.timeout).until(
                        EC.presence_of_element_located(self.locator_dictionary[what])
                    )
                except(TimeoutException, StaleElementReferenceException):
                    traceback.print_exc()

                try:
                    element = WebDriverWait(self.browser, self.timeout).until(
                        EC.visibility_of_element_located(self.locator_dictionary[what])
                    )
                except(TimeoutException, StaleElementReferenceException):
                    traceback.print_exc()
                # I could have returned element, however because of lazy loading, I am seeking the element before return
                return self._find_element(*self.locator_dictionary[what])
        except AttributeError:
            super(PollBot, self).__getattribute__("method_missing")(what)


    def run(self, post_text, status_id, choice1, choice2, choice3, days, hours, minutes):
        self.login()
        self.tweet_poll(post_text, status_id, choice1, choice2, choice3, days, hours, minutes)
        self.browser.close()


    def login(self, username=Constants.USERNAME, password=Constants.PASSWORD):
        self.login_btn.click()
        time.sleep(1)
        self.username.click()
        time.sleep(0.1)
        self.username.send_keys(username)
        time.sleep(0.1)
        self.password.click()
        time.sleep(0.1)
        self.password.send_keys(password)
        time.sleep(0.1)
        self.login_confirm.click()
        time.sleep(1.5)

        try:
            self.challenge_response.send_keys(os.environ.get("phone_number"))
            time.sleep(1)
            self.challenge_submit.click()
            time.sleep(1)
        except Exception:
            print("No challenge")

    def tweet_poll(self, post_text, status_id, choice1, choice2, choice3, days, hours, minutes=15):
        self.browser.get(URL.TWITTER_STATUS+str(status_id))
        self.timeout = 2
        # click the tweet box
        self.another_tweet.click()
        time.sleep(1)

        # type the tweet
        self.tweet_box.send_keys(post_text)
        time.sleep(1)

        # make the poll
        self.poll_btn.click()
        time.sleep(0.1)
        self.option_one.click()
        time.sleep(0.1)
        self.option_one.send_keys(choice1)
        time.sleep(0.1)
        self.option_two.click()
        time.sleep(0.1)
        self.option_two.send_keys(choice2)
        time.sleep(0.2)

        if choice3:
            self.extra_opts.click()
            time.sleep(0.1)
            self.option_three.click()
            time.sleep(0.1)
            self.option_three.send_keys(choice3)

            
        self.days.click()
        time.sleep(0.1)
        Select(self.days).select_by_value(str(days))
        time.sleep(0.1)
        self.hours.click()
        time.sleep(0.1)
        Select(self.hours).select_by_value(str(hours))
        time.sleep(0.1)
        self.minutes.click()
        time.sleep(0.1)
        Select(self.minutes).select_by_value(str(minutes))
        time.sleep(0.1)

        # send the tweet
        self.tweet_btn.click()
        time.sleep(2)

    

if __name__=="__main__":
    pollBot = PollBot()
    pollBot.run("Hola","1","2","3",0,6,15)