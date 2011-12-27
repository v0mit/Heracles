"""
WARNING, this file contains horrible code :(
"""
from lxml import html, etree
import http_handler, logging, sys


__author__ = 'v0mit'


class HttpFormChecker():
    def __init__(self):
        self.h = http_handler.http_handler()
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        self.form_hints = ["login", "member", "user"]
        self.pass_synom = ["pass", "passw", "password", "passwd"]
        self.user_synom = ["login", "username", "user", "email", "e-mail", "mail"]
        self.input_hints =self.pass_synom+self.user_synom
        self.bad_hints = ["reg", "register", "signup"]

    def getPage(self, url):
        try:
            data = self.h.request(url)
        except http_handler.HTTPError as errno:
            return None

        return data

    def getInputs(self, form):
        doc = etree.tostring(form)
        doc = html.fromstring(doc)
        inputs = doc.xpath("//input")

        input_list = []
        for inp in inputs:
            buf = etree.tostring(inp)
            input_doc = html.fromstring(buf)

            name = input_doc.xpath("//input/@name")
            type = input_doc.xpath("//input/@type")
            _class = input_doc.xpath("//input/@class")
            id = input_doc.xpath("//input/@id")

            if not name:
                name = ""
            else:
                name = name[0]
            if not type:
                type = ""
            else:
                type = type[0]
            if not _class:
                _class = ""
            else:
                _class = _class[0]
            if not id:
                id = ""
            else:
                id = id[0]

            input_atts = {
                    "name":name,
                    "type":type,
                    "_class":_class,
                    "id":id
                         }
            input_list.append(input_atts)

        return input_list

    def findLoginForms(self, data):
        doc = html.fromstring(data)
        forms = doc.xpath("//form")

        form_list = []
        for form in forms:
            buf = etree.tostring(form)
            form_doc = html.fromstring(buf)

            action = form_doc.xpath("//form/@action")
            id = form_doc.xpath("//form/@id")
            _class = form_doc.xpath("//form/@class")

            if not action:
                action = ""
            else:
                action = action[0]
            if not id:
                id = ""
            else:
                id = id[0]
            if not _class:
                _class = ""
            else:
                _class = _class[0]

            form_list.append(({"action":action, "id":id, "_class":_class},
                              self.getInputs(form))) #getInput returns (name, type, _class, id) if there are any.

        return form_list

    def checkIfLogin(self, form_list):
        """
        Returns:
        tuple(
                #dict of form attributes
                {
                "action":action,
                "_class":class,
                "id":id
                },
                #List of dicts containing the attributes for the inputs
                [
                    {
                    "_class":class,
                    "type":type,
                    "name":name,
                    "id":id
                    }
              )#End of tuple
        """
        point_list = []
        for form in form_list:
            form_atts = form[0]
            input_att_list = form[1]
            points = self.checkForms(form_atts)

            for input_atts in input_att_list:
                points += self.checkInputs(input_atts)

            point_list.append(points)

        biggest = index = 0
        for idx, points in enumerate(point_list):
            if points > biggest:
                biggest = points
                index = idx

        if biggest < 5:
            print("This might not be the login form. Please check manually.")
        logging.debug("[?]Points:%d" % biggest)
        logging.debug("[?]Form index:%d" % index)
        logging.debug(form_list[index])

        return form_list[index]

    def checkForms(self, form_atts):
        #form_atts = {"action":action, "id":id, "_class":_class}
        points = 0

        for hint in self.form_hints:
            if form_atts.get("action").find(hint) != -1:
                logging.debug("[?]Possible login found.\nACTION:{0}".format(form_atts.get("action")))
                points += 1

            if form_atts.get("id").find(hint) != -1:
                logging.debug("[?]Possible login found.\nID:{0}".format(form_atts.get("id")))
                points += 1

            if form_atts.get("_class").find(hint) != -1:
                logging.debug("[?]Possible login found.\nCLASS:{0}".format(form_atts.get("_class")))
                points += 1

        for hint in self.bad_hints:
            if form_atts.get("action").find(hint) != -1:
                logging.debug("[?]Bad hint found.\nACTION:{0}".format(form_atts.get("action")))
                points -= 5

            if form_atts.get("id").find(hint) != -1:
                logging.debug("[?]Bad hint found.\nID:{0}".format(form_atts.get("id")))
                points -= 5

            if form_atts.get("_class").find(hint) != -1:
                logging.debug("[?]Bad hint found.\nCLASS:{0}".format(form_atts.get("_class")))
                points -= 5

        return points

    def checkInputs(self, input_atts):
        #input_atts = {"name":name, "type":type, "_class":class, "id":id}
        points = 0

        for hint in self.input_hints:
            if input_atts.get("name").find(hint) != -1:
                logging.debug("[?]Possible login found.\nNAME:{0}".format(input_atts.get("name")))
                points += 1

            if input_atts.get("type").find(hint) != -1:
                logging.debug("[?]Possible login found.\nTYPE:{0}".format(input_atts.get("type")))
                points += 1

            if input_atts.get("_class").find(hint) != -1:
                logging.debug("[?]Possible login found.\nCLASS:{0}".format(input_atts.get("_class")))
                points += 1

            if input_atts.get("id").find(hint) != -1:
                logging.debug("[?]Possible login found.\nID:{0}".format(input_atts.get("id")))
                points += 1

        for hint in self.bad_hints:
            if input_atts.get("name").find(hint) != -1:
                logging.debug("[?]Bad hint found.\nNAME:{0}".format(input_atts.get("name")))
                points -= 5

            if input_atts.get("type").find(hint) != -1:
                logging.debug("[?]Bad hint found.\nTYPE:{0}".format(input_atts.get("type")))
                points -= 5

            if input_atts.get("_class").find(hint) != -1:
                logging.debug("[?]Bad hint found.\nCLASS:{0}".format(input_atts.get("_class")))
                points -= 5

            if input_atts.get("id").find(hint) != -1:
                logging.debug("[?]Bad hint found.\nID:{0}".format(input_atts.get("id")))
                points -= 5

        return points

    def createPostDict(self, form_data):
        data = {}
        for  inp in form_data[1]:
            name = inp.get("name")

            if name in self.pass_synom or name in self.user_synom:
                data[name] = ""

        return form_data[0].get("action"), data