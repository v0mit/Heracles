"""
Project:Heracles
Last-Edit:Fri 10 Jan 2012
Site:http://darkpy.net/python/Heracles/

Author(s):
    v0mit: v0mit@darkpy.net
"""
import urllib, urllib2, base64, httplib, logging, sys

class http_handler():
    def __init__(self, proxy=None, l_lvl=20):
        if l_lvl == 10:
            logging.basicConfig(stream=sys.stderr, level=l_lvl,
                format='[%(levelname)s] (%(thread)d) %(message)s')
        else:
            logging.basicConfig(stream=sys.stderr, level=l_lvl,
                format='[%(levelname)s] %(message)s')

        if proxy:
            self.install_proxy(proxy)

        else:
            self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

        self.user_agent = 'http_handler.Py2.v1.2H v0mit@darkpy.net'
        urllib2.install_opener(self.opener)

    def request(self, url, auth=None, data=None):
        req = urllib2.Request(url)

        if auth:
            base64string = base64.encodestring('%s:%s' % (auth[0], auth[1])).replace('\n', '')
            req.add_header("Authorization", "Basic %s" % base64string)

        req.add_header('User-Agent', self.user_agent)

        if data:
            try:
                data = urllib.urlencode(data)
            except TypeError as errno:
                raise HTTPError("Invalid data: {0}".format(errno))

            try:
                response = self.opener.open(req,data)
                self.code = response.code
            except urllib2.URLError as errno:
                raise HTTPError("[!]urllib2.URLError({0})\n[URL:{1}][Data:{2}".format(errno, url, data))

            return response.read()
        else:
            try:
                response = self.opener.open(req)
                self.code = response.code
            except urllib2.URLError as errno:
                raise HTTPError("[!]urllib2.URLError({0})\n[URL:{1}]".format(errno, url))

            except ValueError as errno:
                raise HTTPError("[!]ValueError({0}\n".format(errno))

            except httplib.BadStatusLine as errno:
                raise HTTPError("[!]BadStatusLine({0}\n".format(errno))

            return response.read()

    def install_proxy(self, proxy):
        if len(proxy) is not 2:
            raise HTTPError("Invalid proxy.")
            return

        if proxy[0] == "SOCK":
            import socket

            try:
                import socks
            except ImportError:
                raise HTTPError("SocksiPy not installed, http://socksipy.sourceforge.net/")
                return

            try:
                ip, port = proxy[1].split(":")
            except ValueError as errno:
                raise HTTPError("{0} Invalid proxy(IP:PORT)".format(errno))

            socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, ip, int(port))
            socket.socket = socks.socksocket

            self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

        else:
            http_proxy= {"http":"http://{0}/".format(proxy[1])}
            proxy_support = urllib2.ProxyHandler(http_proxy)
            self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(), proxy_support)

    def installAuthProxy(self, auth, proxy):
        http_proxy= {"http":"http://{0}/".format(proxy[1])}
        proxy_handler = urllib2.ProxyHandler(http_proxy)
        auth_handler = urllib2.ProxyBasicAuthHandler()
        auth_handler.add_password(user=auth[0], passwd=auth[1])

        self.opener = urllib2.build_opener(proxy_handler, auth_handler)


class HTTPError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
