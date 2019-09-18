from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from .models import Question, Submission, UserProfile, MultipleQues
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseForbidden
import datetime
import os, subprocess
import re

starttime =0

end_time=10
duration=0

start = datetime.datetime(2020, 1, 1, 0, 0)
flag = False

path = os.getcwd()
path_usercode = path + '/data/usersCode'

NO_OF_QUESTIONS = 6
NO_OF_TEST_CASES = 6


def waiting(request):
    if request.user.is_authenticated:
        return redirect(reverse("questionHub"))
    else:
        global flag
        if flag == False:
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

            try:
                os.system('mkdir {}/{}/question{}'.format(path_usercode, username, qn))
            except FileExistsError:
                pass

            print(extension)
            codefile = open("{}/{}/question{}/code{}-{}.{}".format(path_usercode, username, qn, qn, att, extension),
                            "w+")
            codefile.write(content)
            codefile.close()

            ans = subprocess.Popen(['python2', "{}/data/Judge/main.py".format(path), path, username, str(qn), str(att),
                                    extension,
                                    "{}/{}/question{}/code{}-{}.{}".format(path_usercode, username, qn, qn, att,
                                                                           extension)], stdout=subprocess.PIPE)
            (out, err) = ans.communicate()
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

            submission = Submission(code=content, user=user, que=que, attempt=att, out=out, subTime=subTime)
            submission.save()

            mul_que.attempts += 1
            mul_que.save()

            return redirect("runCode", username=username, qn=qn, att=att)

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


def runCode(request, username, qn, att):
    if request.user.is_authenticated:
        user = User.objects.get(username=username)
        que = Question.objects.get(pk=qn)
        user_profile = UserProfile.objects.get(user=request.user)

        try:
            mul_que = MultipleQues.objects.get(user=user, que=que)
        except MultipleQues.DoesNotExist:
            mul_que = MultipleQues(user=user, que=que)

        submission = Submission.objects.get(user=user, que=que, attempt=att)

        '''
            code will have text in form '1020301020'
            output_list will contain (10, 20, 30, 10, 20)  for 6 test cases
    
            Sandbox will return(save) these values in total_output.txt
            10 = right answer (PASS)
            20 = wrong answer (WA)
            30 = Time Limit Exceed (TLE)
            40 = compile time error (CTE)
            50 = core Dumped (RTE)
            60 = Abnormal Termination (RTE)
        '''

        code = int(submission.out)
        output_list = list()
        correct_list = list()

        for i in range(0, NO_OF_TEST_CASES):
            correct_list.append('PASS')  # list of all PASS test Cases

        check50 = False  # for checking return value is 50 or 60

        for i in range(0, NO_OF_TEST_CASES):
            var = code % 100
            if var == 10:
                output_list.append('PASS')
            elif var == 20:
                output_list.append('WA')
            elif var == 30:
                output_list.append('TLE')
            elif var == 40:
                output_list.append('CTE')
            elif var == 50 or var == 60:
                output_list.append('RTE')
                check50 = True if var == 50 else False
            code = int(code / 100)
            print(code)

        flag = True  # for checking condition of multiple submission
        output_list.reverse()
        print(output_list)
        print(correct_list)

        if output_list == correct_list:  # if all are correct then Score = 100
            if mul_que.scoreQuestion == 0:
                que.totalSuccessfulSub += 1
                mul_que.scoreQuestion = 100
                submission.subStatus = 'PASS'
                user_profile.totalScore += mul_que.scoreQuestion
                que.save()
                mul_que.save()
            else:
                submission.subStatus = 'PASS'
                flag = False

        if flag:
            user_profile.save()

        com_time_error = False
        tle_error = False
        wrg_ans = False
        run_time_error = False

        for i in output_list:
            if i == 'CTE':
                com_time_error = True
                submission.subStatus = 'CTE'
            elif i == 'TLE':
                tle_error = True
                submission.subStatus = 'TLE'
            elif i == 'WA':
                wrg_ans = True
                submission.subStatus = 'WA'
            elif i == 'RTE':
                run_time_error = True
                submission.subStatus = 'RTE'
            mul_que.scoreQuestion = 100 if submission.subStatus == 'PASS' else 0

        error_text = 'Wrong Answer!'

        if not (wrg_ans or tle_error or com_time_error or run_time_error):
            error_text = 'No Error Found, Compiled Successfully! Your Answer is Correct!'

        if run_time_error and check50:
            error_text = 'Run Time Error! Core Dumped!'
        elif run_time_error and (check50 is False):
            error_text = 'Run Time Error! Abnormal Termination!'

        if com_time_error:
            for i in output_list:  # assigning each element with 40 (CTE will be for every test case)
                i = 40
            error_path = path_usercode + '/{}/question{}'.format(username, qn)
            error_file = open('{}/error.txt'.format(error_path), 'r')
            error_text = error_file.readline()

        error_text = re.sub('/.*?:', '', error_text)  # regular expression

        no_of_pass = 0
        for i in output_list:
            if i == 'PASS':
                no_of_pass += 1

        print(error_text)

        submission.correctTestCases = no_of_pass
        submission.TestCasesPercentage = (no_of_pass / NO_OF_TEST_CASES) * 100
        submission.save()

        status = 'PASS' if no_of_pass == NO_OF_TEST_CASES else 'FAIL'

        # for i in output_list:
        #     if i == 'WA' or i == 'RTE' or i == 'CTE':
        #         i = 'FAIL'

        test_case_1 = output_list[0]
        test_case_2 = output_list[1]
        test_case_3 = output_list[2]
        test_case_4 = output_list[3]
        test_case_5 = output_list[4]
        test_case_6 = output_list[5]

        dict = {'com_status': status, 'test_case_1': test_case_1, 'test_case_2': test_case_2,
                'test_case_3': test_case_3,
                'test_case_4': test_case_4, 'test_case_5': test_case_5, 'test_case_6': test_case_6,
                'output_list': output_list, 'score': mul_que.scoreQuestion, 'error': error_text}

        return render(request, 'userApp/testcases.html', dict)
    else:
        return HttpResponseRedirect(reverse("signup"))


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
