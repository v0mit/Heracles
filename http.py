__author__ = 'v0mit'
import http_handler, HttpFormChecker


class HttpForm():
    def __init__(self, url, dictionary):
        self.parser = HttpFormChecker.HttpFormChecker()
        self.url = url
        self.dictionary = dictionary


