"""
Project:Heracles
Version:0.1
Site:http://darkpy.net/python/Heracles/

Author(s):
    v0mit: v0mit@darkpy.net
"""
import threading, logging, Queue, sys


class AttackThread(threading.Thread):
    def __init__(self, attack_q, attack_object, result_queue, l_lvl=20):
        super(AttackThread, self).__init__()
        if l_lvl == 10:
            logging.basicConfig(stream=sys.stderr, level=l_lvl,
                format='[%(levelname)s] (%(thread)d) %(message)s')
        else:
            logging.basicConfig(stream=sys.stderr, level=l_lvl,
                format='[%(levelname)s] %(message)s')

        self.attack_q = attack_q
        self.attack_object = attack_object
        self.result_queue = result_queue

        self.stopreq = threading.Event()

    def run(self):
        while not self.stopreq.isSet():
            try:
                login_info = self.attack_q.get(True, 0.05)
            except Queue.Empty:
                continue

            user = login_info[0][0]
            passwd = login_info[0][1]
            proxy = login_info[1]

            logging.debug("Trying {0}:{1}".format(user, passwd))

            if proxy:
                result = self.attack_object.doLogin(user, passwd, proxy)
            else:
                result = self.attack_object.doLogin(user, passwd)

            if result == "PROXY FAIL":
                self.result_queue.put(("PROXY FAIL", (user, passwd)))

            self.attack_q.task_done()

    def join(self, timeout=None):
        self.stopreq.set()
        super(AttackThread, self).join(timeout)