from DB import mysql
from Crawler import base
import sys
import re

def get_proxy():
    from Helper import proxy
    proxy.run()


if __name__ == '__main__':
    command =  sys.argv[0]
    if len(sys.argv) == 1:
        pass
    elif sys.argv[1] == 'proxy':
        get_proxy()
