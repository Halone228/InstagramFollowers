from instagrapi import types as igaTypes
from instagrapi import Client
from fake_useragent import UserAgent


class Worker:
    def __init__(self, *, proxy=None, login, password):
        self.client = Client(proxy=proxy)
        self.is_login = self.login(login, password)
        assert self.is_login, f"Account {login} cannot log in"

    @property
    def username(self):
        return self.client.username

    def login(self, login, password):
        return self.client.login(login, password)

    def logout(self):
        self.client.logout()

    def get_user_followers(self, username: str):
        """

        :param username:
        :type username: str
        :return:
        """
        user = self.client.user_info_by_username_v1(username)
        print(f"Start get followers, need to get {user.follower_count}")
        return self.client.user_followers_v1(user.pk), user.follower_count

    def get_account_info(self, user_id: int) -> igaTypes.User:
        """
        Return account info of user_id
        :param user_id:
        :return: User info
        :rtype: instagrapi.types.User
        """
        return self.client.user_info_v1(user_id)
