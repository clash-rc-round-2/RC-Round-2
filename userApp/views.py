from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from .models import Question, Submission, UserProfile, MultipleQues
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseForbidden
import datetime
import os
import re

from judgeApp.views import exec_main

starttime = 0
end_time = 0
duration = 0
flag = False
start = datetime.datetime(2020, 1, 1, 0, 0)

path_usercode = 'data/usersCode/'
standard = 'data/standard/'

NO_OF_QUESTIONS = 6
NO_OF_TEST_CASES = 6


def waiting(request):
    if request.user.is_authenticated:
        return redirect(reverse("questionHub"))
    else:
        global flag
        if not flag:
            return render(request, 'userApp/waiting.html')
        else:
            now = datetime.datetime.now()
            global start
            if now == start:
                return redirect(reverse("signup"))
            elif now > start:
                return redirect(reverse("signup"))
            else:
                return render(request, 'userApp/waiting.html')


def timer(request):
    if request.method == 'GET':
        return render(request, 'userApp/timer.html')

    elif request.method == 'POST':
        global starttime, start
        global end_time
        global duration
        global flag
        flag = True
        duration = 7200  # request.POST.get('duration')
        start = datetime.datetime.now()
        start = start + datetime.timedelta(0, 5)
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
    if request.user.is_authenticated:
        try:
            user = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            user = UserProfile()

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
                return render(request, 'userApp/login.html')

            user = User.objects.create_user(username=username, password=password)
            userprofile = UserProfile(user=user, name1=name1, name2=name2, phone1=phone1, phone2=phone2, email1=email1,
                                      email2=email2)
            userprofile.save()
            os.system('mkdir {}/{}'.format(path_usercode, username))
            login(request, user)
            return redirect(reverse("instructions"))

        except IntegrityError:
            return render(request, 'userApp/login.html')

        except HttpResponseForbidden:
            return render(request, 'userApp/login.html')

    elif request.method == 'GET':
        return render(request, "userApp/login.html")


def questionHub(request):
    if request.user.is_authenticated:
        try:
            user = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return signup(request)

        all_questions = Question.objects.all()
        all_users = User.objects.all()

        for que in all_questions:
            for user in all_users:
                try:
                    mul_que = MultipleQues.objects.get(user=user, que=que)
                except MultipleQues.DoesNotExist:
                    mul_que = MultipleQues(user=user, que=que)
                que.totalSub += mul_que.attempts

            try:
                que.accuracy = round((que.totalSuccessfulSub * 100 / que.totalSub), 1)
            except ZeroDivisionError:
                que.accuracy = 0

        var = calculate()
        if var != 0:
            return render(request, 'userApp/qhub.html', context={'all_questions': all_questions, 'time': var})
        else:
            return render(request, 'userApp/result.html')
    else:
        return redirect("signup")


def change_file_content(content, extension, code_file):
    if extension != 'py':
        sandbox_header = '#include"../../../include/sandbox.h"\n'
        try:
            # Inject the function call for install filters in the user code file
            # Issue with design this way (look for a better solution (maybe docker))
            # multiple main strings
            before_main = content.split('main')[0] + 'main'
            after_main = content.split('main')[1]
            index = after_main.find('{') + 1
            main = before_main + after_main[:index] + 'install_filters();' + after_main[index:]
            with open(code_file, 'w+') as f:
                f.write(sandbox_header)
                f.write(main)
                f.close()

        except IndexError:
            with open(code_file, 'w+') as f:
                f.write(content)
                f.close()

    else:
        with open(code_file, 'w+') as f:
            f.write('import temp\n')
            f.write(content)
            f.close()


def codeSave(request, username, qn):
    if request.user.is_authenticated:  # Check Authentication
        if request.method == 'POST':
            que = Question.objects.get(pk=qn)
            user = User.objects.get(username=username)

            content = request.POST['content']
            extension = request.POST['ext']

            user_profile = UserProfile.objects.get(user=user)
            user_profile.choice = extension

            temp_user = UserProfile.objects.get(user=user)
            temp_user.qid = qn
            temp_user.save()

            try:
                mul_que = MultipleQues.objects.get(user=user, que=que)
            except MultipleQues.DoesNotExist:
                mul_que = MultipleQues(user=user, que=que)
            att = mul_que.attempts

            user_question_path = '{}/{}/question{}/'.format(path_usercode, username, qn)

            if not os.path.exists(user_question_path):
                os.system('mkdir ' + user_question_path)

            code_file = user_question_path + "code{}.{}".format(att, extension)

            content = str(content)

            change_file_content(content, extension, code_file)

            testcase_values = exec_main(
                username=username,
                qno=qn,
                attempts=att,
                lang=extension
            )
            print(type(testcase_values))

            flag_ac = True

            for i in testcase_values:
                if i != 'AC':
                    score = 0
                    flag_ac = False
                    status = 'FAIL'
                    break

            if flag_ac:
                score = 100
                status = 'PASS'

            sub = Submission(code=content, user=user, que=que, attempt=att)
            sub.save()

            mul_que.attempts += 1
            mul_que.save()

            error_text = ""

            epath = path_usercode + '/{}/question{}/error.txt'.format(username, qn)

            if os.path.exists(epath):
                ef = open(epath, 'r')
                error_text = ef.read()
                error_text = re.sub('/.*?:', '', error_text)  # regular expression
                ef.close()

            data = {
                'testcase': testcase_values,
                'error': error_text,
                'score': score,
                'status': status,
            }

            return render(request, 'userApp/testcases.html', context=data)

        elif request.method == 'GET':
            que = Question.objects.get(pk=qn)
            user_profile = UserProfile.objects.get(user=request.user)
            user = User.objects.get(username=username)

            var = calculate()
            if var != 0:
                return render(request, 'userApp/codingPage.html', context={'question': que, 'user': user, 'time': var,
                                                                           'total_score': user_profile.totalScore,
                                                                           'question_id': user_profile.qid})
            else:
                return render(request, 'userApp/result.html')
    else:
        return HttpResponseRedirect(reverse("signup"))


def instructions(request):
    if request.user.is_authenticated:
        return render(request, 'userApp/instructions.html')
    else:
        return redirect("signup")


def leader(request):
    if request.user.is_authenticated:
        dict = {}
        for user in UserProfile.objects.order_by("-totalScore"):
            list = []
            for n in range(1, NO_OF_QUESTIONS + 1):
                que = Question.objects.get(pk=n)
                try:
                    mulQue = MultipleQues.objects.get(user=user.user, que=que)
                    list.append(mulQue.scoreQuestion)
                except MultipleQues.DoesNotExist:
                    list.append(0)
            list.append(user.totalScore)
            dict[user.user] = list

        sorted(dict.items(), key=lambda items: (items[1][6], user.latestSubTime))
        var = calculate()
        if var != 0:
            return render(request, 'userApp/leaderboard.html',
                          context={'dict': dict, 'range': range(1, NO_OF_QUESTIONS + 1, 1),
                                   'time': var})
        else:
            return render(request, 'userApp/result.html')
    else:
        return HttpResponseRedirect(reverse("signup"))


def submission(request, username, qn):
    user = User.objects.get(username=username)
    que = Question.objects.get(pk=qn)
    all_submission = Submission.objects.all()
    userQueSub = list()

    for submissions in all_submission:
        if submissions.user == user and submissions.que == que:
            userQueSub.append(submissions)
    var = calculate()
    print(userQueSub)
    print("working")
    if var != 0:
        return render(request, 'userApp/submissions.html', context={'allSubmission': userQueSub, 'time': var})
    else:
        return render(request, 'userApp/result.html')


def user_logout(request):
    if request.user.is_authenticated:
        try:
            user = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return signup(request)
        object = UserProfile.objects.order_by("-totalScore", "latestSubTime")
        rank = 0
        i = 0
        dict = {}
        for user in object:
            if rank < 3:
                dict[user.user] = user.totalScore
                rank = rank + 1
            else:
                break

        for user in object:
            i += 1
            if str(user.user) == str(request.user.username):
                break

        logout(request)
        return render(request, 'userApp/result.html', context={'dict': dict, 'rank': i, 'name': user.user,
                                                           'score': user.totalScore})
    else:
        return HttpResponseRedirect(reverse("signup"))


def loadBuffer(request):
    username = request.POST.get('username')
    user = UserProfile.objects.get(user=request.user)
    qn = request.POST.get('question_no')
    que = Question.objects.get(pk=qn)
    mul_que = MultipleQues.objects.get(user=user.user, que=que)
    attempts = mul_que.attempts
    ext = request.POST.get('ext')
    response_data = {}

    codeFile = '{}/{}/question{}/code{}.{}'.format(path_usercode, username, qn, attempts - 1, user.lang)

    f = open(codeFile, "r")
    txt = f.read()
    if not txt:
        data = ""
    response_data["txt"] = txt

    return JsonResponse(response_data)


def check_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    if data['is_taken']:
        data['error_message'] = 'username already exits.'

    return JsonResponse(data)
