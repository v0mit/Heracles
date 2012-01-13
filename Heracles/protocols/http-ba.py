"""
Project:Heracles
Version:0.1
Site:http://darkpy.net/python/Heracles/

Author(s):
    v0mit: v0mit@darkpy.net
"""
import Heracles.http_handler, logging, sys


class AttackObject():
    def __init__(self, options, l_lvl=20):
        self.options = options
        self.url = options.get("host")
        if not self.url.startswith("http://"):
            self.url = "http://"+self.url

        if l_lvl == 10:
            logging.basicConfig(stream=sys.stderr, level=l_lvl,
                format='[%(levelname)s] (%(thread)d) %(message)s')
        else:
            logging.basicConfig(stream=sys.stderr, level=l_lvl,
                format='[%(levelname)s] %(message)s')

    def doLogin(self, user, passwd, proxy=None):
        if proxy:
            print(proxy)
            #Testing if it is a HTTP proxy
            ip, port = proxy.split(":")
            if port in ["80", "8080", "3128"]: #Most HTTP proxies run on those ports.
                try:
                    logging.debug("Passing proxy as HTTP1")
                    h = Heracles.http_handler.http_handler(("HTTP", proxy),
                        l_lvl=self.options.get("verbose"))
                except Heracles.http_handler.HTTPError as errno:
                    logging.debug(errno)
                    #Try it again as a SOCK proxy.
                    try:
                        logging.debug("Passing proxy as SOCK1")
                        h = Heracles.http_handler.http_handler(("SOCK", proxy),
                            l_lvl=self.options.get("verbose"))
                    except Heracles.http_handler.HTTPError as errno: #None worked, maybe proxy is down?
                        logging.debug(errno)
                        logging.debug("{0}:{1} failed.".format(user, passwd))
                        return "PROXY FAIL"
            else:
                try:    #Try it as a SOCK proxy first.
                    logging.debug("Passing proxy as SOCK2")
                    h = Heracles.http_handler.http_handler(("SOCK", proxy),
                        l_lvl=self.options.get("verbose"))
                except Heracles.http_handler.HTTPError as errno:
                    logging.debug(errno)
                    try:#
                        logging.debug("Passing proxy as HTTP2")
                        h = Heracles.http_handler.http_handler(("HTTP", proxy),
                            l_lvl=self.options.get("verbose"))
                    except Heracles.http_handler.HTTPError as errno:
                        logging.debug(errno)
                        logging.debug("{0}:{1} failed.".format(user, passwd))
                        return "PROXY FAIL"

            try:
                h.request(self.url, (user, passwd))
            except Heracles.http_handler.HTTPError as errno:
                logging.debug(errno)
                return "PROXY FAIL"

        #Not using a proxy
        else:
            try:
                h = Heracles.http_handler.http_handler(
                    l_lvl=self.options.get("verbose"))
                h.request(self.url, (user, passwd))
            except Exception:
                logging.debug("{0}:{1} failed.".format(user, passwd))
                return "PROXY FAIL"

        if h.code == 200: #A valid login returns HTTP code 200
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

        logging.debug("{0}:{1} failed.".format(user, passwd))

        return None
