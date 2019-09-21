from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from .models import Question, Submission, UserProfile, MultipleQues
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseForbidden
import datetime
import os, subprocess
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
        start = start + datetime.timedelta(0, 15)
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
    else:
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
                junior = request.POST.get('optradio')

                junior = True if (junior == 'fe' or junior == 'se') else False

                if username == "" or password == "":
                    return render(request, 'userApp/login.html')
                print(junior)
                user = User.objects.create_user(username=username, password=password)
                userprofile = UserProfile(user=user, name1=name1, name2=name2, phone1=phone1, phone2=phone2, email1=email1,
                                          email2=email2, junior=junior)
                userprofile.save()
                print(username)
                os.system('mkdir {}/{}'.format(path_usercode, username))
                login(request, user)
                return redirect(reverse("instructions"))

            except IntegrityError:
                return render(request, 'userApp/login.html')

            except HttpResponseForbidden:
                return render(request, 'userApp/login.html')

        elif request.method == 'GET':
            return render(request, "userApp/login.html")

    return HttpResponseRedirect(reverse("questionHub"))


def questionHub(request):
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
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
                que.totalSub += 1 if mul_que.attempts > 0 else 0
            try:
                que.accuracy = round((que.totalSuccessfulSub * 100/que.totalSub), 1)
            except ZeroDivisionError:
                que.accuracy = 0

        var = calculate()
        if var != 0:
            return render(request, 'userApp/qhub.html', context={'all_questions': all_questions, 'time': var})
        else:
            return render(request, "userApp/result.html")
    else:
        return HttpResponseRedirect(reverse("signup"))


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


def codeSave(request, qn):
    if request.user.is_authenticated:  # Check Authentication
        if request.method == 'POST':
            que = Question.objects.get(pk=qn)
            user = request.user
            username= user.username

            content = request.POST['content']
            extension = request.POST['ext']

            user_profile = UserProfile.objects.get(user=user)
            user_profile.choice = extension

            temp_user = UserProfile.objects.get(user=user)
            temp_user.qid = qn
            temp_user.lang = extension
            temp_user.save()

            try:
                mul_que = MultipleQues.objects.get(user=user, que=que)
            except MultipleQues.DoesNotExist:
                mul_que = MultipleQues(user=user, que=que)
                mul_que.save()
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

            code_f = open(code_file, 'w+')
            code_f.write(content)
            code_f.close()

            now_time = datetime.datetime.now()
            now_time_sec = now_time.second + now_time.minute * 60 + now_time.hour * 60 * 60
            global starttime
            submit_Time = now_time_sec - starttime

            hour = submit_Time // (60 * 60)
            val = submit_Time % (60 * 60)
            min = val // 60
            sec = val % 60

            subTime = '{}:{}:{}'.format(hour, min, sec)

            print(subTime)
            print("submit time" + str(submit_Time))

            sub = Submission(code=content, user=user, que=que, attempt=att, subTime=subTime)
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

            no_of_pass = 0
            for i in testcase_values:
                if i == 'AC':
                    no_of_pass += 1

            print(error_text)

            sub.correctTestCases = no_of_pass
            sub.TestCasesPercentage = (no_of_pass / NO_OF_TEST_CASES) * 100
            sub.save()

            status = 'AC' if no_of_pass == NO_OF_TEST_CASES else 'WA'  # overall Status

            if status == 'AC':
                if mul_que.scoreQuestion == 0:
                    user_profile.totalScore += 100
                    que.totalSuccessfulSub += 1
                    que.save()
                mul_que.scoreQuestion = 100
                user_profile.save()
                mul_que.save()

            var = calculate()
            data = {
                'testcase': testcase_values,
                'error': error_text,
                'status': status,
                'score': mul_que.scoreQuestion,
                'time': var
            }
            if var != 0:
                return render(request, 'userApp/testcases.html', context=data)
            else:
                render(request, "userApp/result.html")

        elif request.method == 'GET':
            que = Question.objects.get(pk=qn)
            user_profile = UserProfile.objects.get(user=request.user)
            user = request.user

            var = calculate()
            if var != 0:
                return render(request, 'userApp/codingPage.html', context={'question': que, 'user': user, 'time': var,
                                                                           'total_score': user_profile.totalScore,
                                                                           'question_id': qn, 'code': '',
                                                                           'junior':user_profile.junior})
            else:
                return render(request, 'userApp/result.html')
    else:
        return HttpResponseRedirect(reverse("signup"))


def instructions(request):
    if request.user.is_authenticated:
        try:
            user = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            user = UserProfile()
        if user.flag:
            return HttpResponseRedirect(reverse('questionHub'))
        if request.method == "POST":
            return HttpResponseRedirect(reverse('questionHub'))
        return render(request, 'userApp/instructions.html')
    else:
        return HttpResponseRedirect(reverse("signup"))


def leader(request):
    if request.user.is_authenticated:
        data = {}
        for user in UserProfile.objects.order_by("-totalScore"):
            l = []
            for n in range(1, 7):
                que = Question.objects.get(pk=n)
                try:
                    mulQue = MultipleQues.objects.get(user=user.user, que=que)
                    l.append(mulQue.scoreQuestion)
                except MultipleQues.DoesNotExist:
                    l.append(0)
            l.append(user.totalScore)
            data[user.user] = l

        sorted(data.items(), key=lambda items: (items[1][6], user.latestSubTime))
        var = calculate()
        if var != 0:
            return render(request, 'userApp/leaderboard.html', context={'dict': data, 'range': range(1, 7, 1),
                                                                        'time': var})
        else:
            return render(request, 'userApp/result.html')
    else:
        return HttpResponseRedirect(reverse("signup"))


def submission(request, qn):
    # print(qn)
    que = Question.objects.get(pk=qn)
    # all_submissions = Submission.objects.filter()
    all_submission = Submission.objects.all()
    userQueSub = list()

    for submissions in all_submission:
        if submissions.que == que and submissions.user == request.user:
            userQueSub.append(submissions)
    var = calculate()
    # print(userQueSub)
    # print("working")
    if var != 0:
        return render(request, 'userApp/submissions.html', context={'allSubmission': userQueSub, 'time': var, 'qn': qn,
                                                                    })
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
    user = UserProfile.objects.get(user=request.user)
    username = request.user.username
    qn = request.POST.get('question_no')
    que = Question.objects.get(pk=qn)
    mul_que = MultipleQues.objects.get(user=user.user, que=que)
    attempts = mul_que.attempts
    ext = request.POST.get('ext')

    response_data = {}

    codeFile = '{}/{}/question{}/code{}.{}'.format(path_usercode, username, qn, int(attempts) - 1, ext)

    f = open(codeFile, "r")
    txt = f.read()
    f.close()
    if not txt:
        data = ""
    response_data["txt"] = txt

    return JsonResponse(response_data)


def getOutput(request):
    if request.user.is_authenticated:
        response_data = {}
        user = UserProfile.objects.get(user=request.user)
        que_no = request.POST.get('question_no')
        i = request.POST.get('ip')
        i = str(i)

        ans = subprocess.Popen("data/standard/executable/question{}/./a.out".format(que_no),
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        (out, err) = ans.communicate(input=i.encode())
        response_data["out"] = out.decode()

        return JsonResponse(response_data)


def garbage(request, garbage):
    return HttpResponseRedirect(reverse('questionHub'))


def check_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    if data['is_taken']:
        data['error_message'] = 'username already exits.'

    return JsonResponse(data)


def view_sub(request, qno, _id):
    if request.method == 'GET':
        user_profile = UserProfile.objects.get(user=request.user)
        sub = Submission.objects.get(id=_id)
        code = sub.code

        # print(code)

        que = Question.objects.get(pk=int(qno))
        user = request.user

        var = calculate()

        return render(request, 'userApp/codingPage.html', context={'question': que, 'user': user, 'time': var,
                                                                   'total_score': user_profile.totalScore,
                                                                   'question_id': qno, 'code': code})
    else:
        return HttpResponse("fdshfhsdlkfnlksdjfnlsdnflkdsnflds")


def emergency_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        AdminPass = request.POST.get('admin_password')
        user = authenticate(username=username, password=password)
        if AdminPass == '1234':
            if user.is_active:
                login(request, user)
                return redirect(reverse('questionHub'))
        else:
            return HttpResponse('invalid details')
    else:
        return render(request, 'userApp/emerlogin.html')


def getOutput(request):
    if request.user.is_authenticated:
        response_data = {}
        username = request.POST.get('username')
        user = UserProfile.objects.get(user=request.user)
        que_no = request.POST.get('question_no')
        i = request.POST.get('ip')
        i = str(i)
        print(i)

        ans = subprocess.Popen("data/standard/executable/question{}/./a.out".format(que_no),
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        (out, err) = ans.communicate(input=i.encode())
        response_data["out"] = out.decode()

        return JsonResponse(response_data)
