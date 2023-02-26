import asyncio
import random
import time

from instagrapi import types as igaTypes
from instagrapi import Client
from instagrapi import exceptions
from fake_useragent import UserAgent
from timezone_api import TimeZoneApi


timezone_token = ''
t_api = TimeZoneApi(timezone_token)

def relogin_dec(func: callable):
    def wrapper(self, *args, **kwargs):
        num_count = 10
        cnt = 0
        while cnt < num_count:
            try:
                return func(self, *args, **kwargs)
            except exceptions.LoginRequired:
                self.relogin()
                cnt += 1
                print('Relogin')
            except exceptions.PleaseWaitFewMinutes:
                print('wait')
                time.sleep(random.randint(1200, 1800))
                cnt += 1
        raise exceptions.LoginRequired()

    return wrapper


class Worker:

    def __init__(self, *, proxy=None, login=None, password=None):

        self.is_login = None
        self.client = None
        self.proxy = proxy
        self.__login = login
        self.__password = password
        if not login:
            self.client = Client(proxy=proxy)
            return
        self.set_account(proxy=proxy, login=login, password=password)

    def set_account(self, *, proxy=None, login, password):
        self.client = Client()
        self.proxy = proxy if proxy else self.proxy
        self.configure_proxy()
        self.is_login = self.login(login, password)
        assert self.is_login, f"Account {login} cannot log in"
        self.__login = login
        self.__password = password
        
    def configure_proxy(self):
        self.client.set_proxy(self.proxy)
        t_data = t_api.get_info(self.proxy)
        self.client.set_locale(t_data['locale'])
        self.client.set_country_coee(t_data['num_prefix'])
        self.cliemt.set_timezone_offset(t_data['offset_seconds'])

    @property
    def username(self):
        return self.client.username

    def login(self, login, password):
        return self.client.login(login, password)

    def logout(self):
        self.client.logout()

    def relogin(self):
        self.set_account(proxy=self.proxy, login=self.__login, password=self.__password)

    @relogin_dec
    def get_user_followers(self, username: str):
        """

        :param username:
        :type username: str
        :return:
        """
        user = self.client.user_info_by_username_v1(username)
        print(f"Start get followers, need to get {user.follower_count}")
        return self.client.user_followers_v1(user.pk), user.follower_count

    @relogin_dec
    def get_account_info(self, user_id: int) -> igaTypes.User:
        """
        Return account info of user_id
        :param user_id:
        :return: User info
        :rtype: instagrapi.types.User
        """
        return self.client.user_info_v1(user_id)
