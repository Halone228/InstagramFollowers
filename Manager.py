import asyncio
import logging
from cfg import *
from Worker import Worker
from instagrapi.types import UserShort
from asyncio import Queue
import re
from pydantic import BaseModel, validator
from logging import basicConfig, getLogger
from tqdm import tqdm
from database import ResultItemModel, Checked
import random
basicConfig(filename='bot.log',format='[%(asctime)s] **%(levelname)s** :: %(message)s', level=logging.NOTSET)


acc_T = UserShort


class ResultItem(BaseModel):
    url: str
    word: str

    @validator('url')
    def is_need_url(cls, v):
        assert v, "String in blank"
        assert 'https://www.instagram.com/' in v, 'Not instagram url'
        return v


res_T = ResultItem


class Manager:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.accounts_queue = Queue()
        self.clients_queue = Queue()
        self.pattern = f"({'|'.join([f'({i})' for i in keywords])})"
        self.working = True
        self.test = True
        self.logger = getLogger(__name__)
        self.loading = None
        self.workers = []
        proxies.append(None)
        for i in accounts:
            proxy = random.choice(proxies)
            print(i)
            self.logger.info(f'Using proxy {proxy}')
            self.workers.append(Worker(
                login=i[0],
                password=i[1],
                proxy=proxy
            ))

    def is_need_biography(self, bio: str):
        """
        Return string with found word, else blank string
        :param bio: User bio
        :return: Word what was find
        :rtype: str
        """
        if self.test:
            return bio
        res = re.search(self.pattern, bio)
        if res:
            return res.group()
        return ''
    
    async def add_account(self, v: acc_T):
        """
        Add account to abstract container for processing
        :param v: 
        :return: 
        """
        await self.accounts_queue.put(v)

    async def get_account(self):
        """
        Return account from abstract container
        :return: `acc_T`
        """
        item = await self.accounts_queue.get()
        self.accounts_queue.task_done()
        return item

    async def append_result(self, v: res_T):
        assert type(v) == res_T, "Not correct result var"
        ResultItemModel.add_if_not_exists(**v.dict())

    @staticmethod
    def url_format(username: str):
        return f'https://www.instagram.com/{username}/'

    async def get_followers(self, username: str):
        """
        Uses instaloader for get user followers and push into `accounts_queue`
        :param username: user username
        :type username: str
        :return: None
        """
        print(username)
        worker = random.choice(self.workers)
        users, count = worker.get_user_followers(username)
        self.loading = tqdm(total=int(count))
        for i in users:
            self.logger.info(f'Get user {i.username}')
            await self.add_account(i)
        self.working = False

    async def worker_job(self, worker: Worker):
        """
        Default work for worker
        :param worker:
        :return:
        """
        while self.working or not self.accounts_queue.empty():
            job: acc_T = await self.get_account()
            if Checked.is_exists(self.url_format(job.username)):
                self.loading.update()
                continue
            user = worker.get_account_info(job.pk)
            self.logger.info(f'Get info about {user.username}')
            word = self.is_need_biography(user.biography)
            if word:
                await self.append_result(res_T(
                    url=self.url_format(user.username),
                    word=word
                ))
            Checked.get_or_create(url=self.url_format(user.username))
            self.loading.update()

    def run(self):
        self.loop.run_until_complete(self.get_followers(parsed_username))
        self.loop.run_until_complete(asyncio.gather(*[
            self.loop.create_task(self.worker_job(worker)) for worker in self.workers]
        ))


if __name__ == '__main__':
    ResultItemModel.create_table(safe=True)
    Checked.create_table(safe=True)
    man = Manager()
    man.run()

