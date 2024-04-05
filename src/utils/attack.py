# imports
import time
import random
import threading
import http.client
from termcolor import colored


class Attack():
    def __init__(self):
        self.url = 'http://127.0.0.1:9000'
        self.routes = [
            '/',
            '/a',
            '/b',
            '/c',
        ]
	
        # list of proxies
        self.proxies = [line.strip() for line in open('proxies', 'r')]
        self.clients = [ip for ip in self.proxies if not ip.endswith('.255')]
        self.parse()


    # splitup clients list
    def parse(self):
        # Calculate the midpoint to evenly split the list
        midpoint = len(self.clients) // 2

        # clients for basic crawling
        self.clients_a = self.clients[:midpoint]

        # clients for random crawling (some basic & some intensive) 
        self.clients_b = self.clients[midpoint:]


    # website crawler
    def requester(self, client):
        # setup socket
        socket = http.client.HTTPConnection('localhost', 9000, source_address=(client, 0))

        # send request to a random server page
        random_route = self.url + random.choice(self.routes)
        socket.request('GET', random_route)

        # get the response
        response = socket.getresponse()
        status_code = response.status

        c = '[' + colored(f'Crawler', 'magenta', attrs=['bold']) + ']'
        r = colored(f'{random_route}', 'blue', attrs=['underline'])
        print(f'{c} : Client {client} - accessed {r}, status: {status_code}')

        # close the socket
        socket.close()


    # website crawl handler
    def crawl(self):
        # setup threads for crawl_basic and crawl_intensive
        thread_basic = threading.Thread(target=self.crawl_basic)
        thread_intensive = threading.Thread(target=self.crawl_intensive)

        # start the threads
        thread_basic.start()
        thread_intensive.start()

        # wait for threads to complete
        thread_basic.join()
        thread_intensive.join()


    # continually crawl the website routes
    def crawl_basic(self):
        # each client makes a request every 1 minute
        num_clients = len(self.clients_a)
        total_time = 60  
        sleep_time = total_time / num_clients

        while True:
            for client in self.clients_a:
                # send x amount of requests from the client
                x = random.randint(1, 100)
                for _ in range(x):
                    self.requester(client)

                time.sleep(sleep_time)


    # crawl the website routes intensively (potentially)
    def crawl_intensive(self):
        while True:
            for client in self.clients_b:
                # send x amount of requests from the client
                x = random.randint(300, 1000)
                for _ in range(x):
                    self.requester(client) 
    
# start
if __name__ == '__main__':
    attack = Attack()
    attack.crawl()