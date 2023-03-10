import asyncio
import logging
from cfg import *
from Worker import Worker
from instagrapi.types import UserShort
from threading import Thread
from queue import Queue
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
    username: str

    @validator('url')
    def is_need_url(cls, v):
        assert v, "String in blank"
        assert 'https://www.instagram.com/' in v, 'Not instagram url'
        return v


res_T = ResultItem


class Manager:
    loading: tqdm
    def __init__(self):
        self.count = None
        self.loop = asyncio.get_event_loop()
        self.accounts_queue = Queue()
        self.clients = Queue()
        [self.clients.put(i) for i in accounts]
        self.pattern = f"({'|'.join([f'({i})' for i in keywords])})"
        self.working = True
        self.test = False
        self.logger = getLogger(__name__)
        self.loading = None
        self.workers = []
        proxies.append(None) if not len(proxies) else None
        for proxy in proxies:
            i = self.clients.get()
            print(i)
            print(proxy)
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
    
    def add_account(self, v: acc_T):
        """
        Add account to abstract container for processing
        :param v: 
        :return: 
        """
        self.accounts_queue.put(v)

    def get_account(self):
        """
        Return account from abstract container
        :return: `acc_T`
        """
        item = self.accounts_queue.get()
        self.accounts_queue.task_done()
        return item

    def append_result(self, v: res_T):
        assert type(v) == res_T, "Not correct result var"
        ResultItemModel.add_if_not_exists(**v.dict())

    @staticmethod
    def url_format(username: str):
        return f'https://www.instagram.com/{username}/'

    def get_followers(self, username: str):
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
        self.count = int(count)
        for i in users:
            self.logger.info(f'Get user {i.username}')
            self.add_account(i)
        self.working = False

    def worker_job(self, worker: Worker):
        """
        Default work for worker
        :param worker:
        :return:
        """
        while self.working or not self.accounts_queue.empty() or self.loading.n <= self.count:
            try:
                job: acc_T = self.get_account()
                if Checked.is_exists(self.url_format(job.username)):
                    self.loading.update()
                    continue
                user = worker.get_account_info(job.pk)
                self.logger.info(f'Get info about {user.username}')
                word = self.is_need_biography(user.biography)
                if word:
                    self.append_result(res_T(
                        url=self.url_format(user.username),
                        word=word,
                        username=parsed_username
                    ))
                Checked.get_or_create(url=self.url_format(user.username))
                self.loading.update()
            except e:
                self.logger.error('Worker caught error ', e)
                print(f'Worker {worker.username} caught error, changing account')
                if self.clients.empty():
                    print('No free clients, stop worker')
                    return
                i = self.clients.get()
                worker.set_account(login=i[0], password=i[1])
                self.logger.info(f'Worker changed to {worker.username}')
                print(f'Worker changed to {worker.username}')

    def run(self):
        self.get_followers(parsed_username)
        process = []
        for i in self.workers:
            p = Thread(target=self.worker_job, args=(i,))
            p.start()
            process.append(p)
        process[0].join()


if __name__ == '__main__':
    ResultItemModel.create_table(safe=True)
    Checked.create_table(safe=True)
    man = Manager()
    man.run()

