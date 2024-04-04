# imports
import json
import time
import base64
import requests
import http.client
import urllib.parse
from termcolor import colored


class Attack():
    def __init__(self):
        self.url = 'http://127.0.0.1:9000'
        self.routes = [
            '/',
        ]
	
        # list of proxies
        self.proxies = [line.strip() for line in open('proxies', 'r')]


    # generate clients
    def clients(self):
        # once ip range ends, change virtual ip address range to next in list
        ranges = [ip for ip in self.proxies if ip.endswith('.254')]
        range_reached = False

        ''' 
            remove proxy range ending addresses
            split the proxies into 3 groups:
            
            1. basic crawling
            2. random crawling (some basic & some intensive) 
        '''
        
    # crawl the website routes
    def crawl_basic (self, client, level):
        pass


    # crawl the website routes intensively
    def crawl_intensive():
        pass


    # crawl the home page
    def crawl_test(self):
        site = self.url + self.routes[0]        
        for _ in range(200):
            result = requests.get(site)
            print(result.status_code)
    

# start
if __name__ == '__main__':
    attack = Attack()
    attack.crawl_test()