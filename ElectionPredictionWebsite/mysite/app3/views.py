import os

from django.shortcuts import render
from socket import *
from threading import *
from django.http import HttpResponse
from tkinter import *
input_obtained = ""
months = ""


def index(request):
    return render(request, 'index.html', {})


def about(request):
    return render(request, 'about.html', {})


def contact(request):
    return render(request, 'contact.html', {})


def giveportfolio(request):
    return render(request, 'portfolio.html', {})


def download(request):
    global input_obtained
    global months
    rootDir = os.path.dirname(os.path.abspath(__file__))
    response = HttpResponse(open(rootDir+"/"+input_obtained+months+"tweets.csv", encoding="utf8").read())
    response['Content-Type'] = "text/csv"
    file_name = input_obtained + " " + "tweets.csv"
    response['Content-Disposition'] = 'attachment; filename='+file_name
    return response


result = ""


class ResultWaitThread(Thread):
    def __init__(self, input_obtained):
        Thread.__init__(self)
        self.input_obtained = input_obtained

    def run(self):
        global result
        client_socket = socket(AF_INET, SOCK_STREAM)
        host_name = "localhost"
        host_port = 1234
        host_addr = (host_name, host_port)
        client_socket.connect(host_addr)
        client_socket.send(self.input_obtained.encode())
        result = client_socket.recv(1024).decode()


def getresults(request):
    global result
    global input_obtained
    global months
    input_obtained = request.GET.get("hashtag")
    if input_obtained == "":
        return render(request, "finalresult1.html",
                      {'something_wrong':"Please enter the candidate name and try again."})
    input_obtained = input_obtained.replace(" ", "").lower()
    months = request.GET.get("months")
    if months == "":
        return render(request, "finalresult1.html", {'something_wrong': "Please enter the number of months and try again."})
    x = re.findall("\D", str(months))
    if x:
        return render(request, "finalresult1.html", {'something_wrong': "Hmm. Something's wrong. Probably, the input which you have provided is invalid. Please try again."})
    if int(months) == 0:
        return render(request, "notweets.html")
    result_wait = ResultWaitThread(input_obtained+","+str(months))
    result_wait.start()
    result_wait.join()
    print(result)
    result_list = result.split(",")
    if result == "no tweets":
        return render(request, "notweets.html")
    # probab_str = str("%.2f" % )
    probab_str = round(int(result_list[0])*100/(int(result_list[0])+int(result_list[2])), 2)
    return render(request, "finalresult.html", {'hashtag': input_obtained, 'positive': result_list[0], 'negative': result_list[2], 'neutral': result_list[1], 'probability': probab_str})
