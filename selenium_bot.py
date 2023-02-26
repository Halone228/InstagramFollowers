import random
import time

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import fake_useragent
from webdriver_manager.chrome import ChromeDriverManager
import pickle
import pathlib
import os
import logging


save_cookies_path = pathlib.Path(os.getcwd()).joinpath('cookies')
save_cookies_path.mkdir(exist_ok=True)


class SeleniumWorker:

    def __init__(
            self,
            username: str,
            password: str
    ):
        self.username = username
        self.password = password
        self.options = ChromeOptions()
        self.__init_options()
        self.driver = Chrome(
            ChromeDriverManager().install(),
            options=self.options
        )
        self.driver.maximize_window()
        # self.read_cookies()

    def __init_options(self):
        self.options.add_argument('--allow-profiles-outside-user-dir')
        self.options.add_argument('--enable-profile-shortcut-manager')
        self.options.add_argument(f'--profile-directory={self.username}')
        self.options.add_argument(f'user-data-dir={str(save_cookies_path.joinpath(self.username))}')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument(f"user-agent={fake_useragent.UserAgent().random}")
        #Proxy?

    def login(self):
        try:
            self.driver.get('https://www.instagram.com')
            login_xpath = '/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/section/main/' \
                          'article/div[2]/div[1]/' \
                          'div[2]/form/div/div[1]/div/label/input'
            password_xpath = '/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/section/main/' \
                             'article/div[2]/div[1]/' \
                             'div[2]/form/div/div[2]/div/label/input'
            submit_selector = '#loginForm > div > div:nth-child(3) > button'
            save_data_xpath = '/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]/section/main/' \
                              'div/div/div/section/div/button'
            user_xpath = '/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[1]/' \
                         'div[1]/div/div/div/div/div[2]/div[8]/div/div/a/div/div[2]/div/div'
            try:
                WebDriverWait(self.driver, 15).until(
                    lambda driver:
                        driver.find_element(By.XPATH, login_xpath)
                )
            except TimeoutException:
                return True
            self.driver.find_element(By.XPATH, login_xpath).send_keys(self.username)
            self.driver.find_element(By.XPATH, password_xpath).send_keys(self.password)
            time.sleep(random.random()*2)
            self.driver.find_element(By.CSS_SELECTOR, submit_selector).click()
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, save_data_xpath))
            )
            self.driver.find_element(By.XPATH, save_data_xpath).click()
            return True
        except Exception as e:
            return False

    def save_cookies(self):
        with open(save_cookies_path.joinpath(f'{self.username}.pkl'), 'wb') as f:
            pickle.dump(self.driver.get_cookies(), f)

    def read_cookies(self):
        try:
            with open(save_cookies_path.joinpath(f'{self.username}.pkl'), 'rb') as f:
                cookies = pickle.load(f)
            for cookie in cookies:
                self.driver.add_cookie(cookie)
        except Exception as e:
            pass

    def get_subscribers(self, username: str):
        self.driver.get(f'https://www.instagram.com/{username}/')
        subs_xpath = '//*[@id="mount_0_0_eO"]/div/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]/section/' \
                     'main/div/header/section/ul/li[2]/a'
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.XPATH, subs_xpath))
        )
        subs_el = self.driver.find_element(By.XPATH, subs_xpath)
        subs_text = subs_el.text.strip()
        print(f"Parsing {subs_text}")
        subs_el.click()
        subs_block_xpath = '/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/' \
                           'div/div'
        WebDriverWait(self.driver, 15).until(
            EC.visibility_of_element_located((By.XPATH, subs_block_xpath))
        )


    def account_info(self):
        pass

    def stop(self):
        # self.save_cookies()
        self.driver.quit()
        del self.driver


if __name__ == '__main__':
    worker = SeleniumWorker('geraldtvoisilach','6754321Kirill!')
    is_login = worker.login()
    print(is_login)
    input()
    worker.stop()
