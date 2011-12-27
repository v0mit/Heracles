__author__ = 'v0mit'
import HttpFormChecker, http_handler

p = HttpFormChecker.HttpFormChecker()
data = p.getPage("http://reddit.com/")
form_list = p.findLoginForms(data)
form_data = p.checkIfLogin(form_list)
post_form = p.createPostDict(form_data)
post_data = post_form[1]
action = post_form[0]

h = http_handler.http_handler()
post_data["passwd"] = "123qwe"
post_data["user"] = "DownGoat"
data = h.request(action, post_data)

a = open("login.html", "wb")
a.write(data)
a.close()