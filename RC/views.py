from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError, Error
from .models import Question, Submission, UserProfile, MultipleQues
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseForbidden
import datetime
import os, subprocess

global starttime
global end_time
global duration

# path = os.getcwd()
# path_usercode = path + '/data/usersCode'

NO_OF_QUESTIONS = 6
NO_OF_TEST_CASES = 5


def timer(request):
    if request.method == 'GET':
        return render(request, 'RC/timer.html')

    elif request.method == 'POST':
        global starttime
        global end_time
        global duration
        duration = request.POST.get('duration')
        start = datetime.datetime.now()
        time = start.second + start.minute * 60 + start.hour * 60 * 60
        starttime = time
        end_time = time + int(duration)
        return HttpResponse(" time is set ")


def calculate():
    time = datetime.datetime.now()
    nowsec = (time.hour * 60 * 60) + (time.minute * 60) + time.second
    global starttime
    global end_time
    diff = end_time - nowsec
    if nowsec < end_time:
        return diff
    else:
        return 0


def signup(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            name1 = request.POST.get('name1')
            name2 = request.POST.get('name2')
            phone1 = request.POST.get('phone1')
            phone2 = request.POST.get('phone2')
            email1 = request.POST.get('email1')
            email2 = request.POST.get('email2')

            if username == "" or password == "":
                return render(request, 'RC/Login.html')

            user = User.objects.create_user(username=username, password=password)
            userprofile = UserProfile(user=user, name1=name1, name2=name2, phone1=phone1, phone2=phone2, email1=email1,
                                      email2=email2)
            userprofile.save()
            os.system('mkdir {}/{}'.format(path_usercode, username))
            login(request, user)
            return redirect(reverse("instructions"))

        except IntegrityError:
            return HttpResponse("you have already been registered.")

        #except HttpResponseForbidden:
         #   return render(request, 'RC/Login.html')

    elif request.method == 'GET':
        return render(request, "RC/Login.html")


def instructions(request):
    return render(request, 'RC/instruction.html')


def questionHub(request):
    all_questions = Question.objects.all()
    var = calculate()
    if var != 0:
        return render(request, 'RC/qhub.html', context={'all_questions': all_questions, 'time': var})
    else:
        return render(request, 'RC/final.html')
