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

        # except HttpResponseForbidden:
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
        return render(request, 'RC/RESULTRC.html')


def submission(request, username):
    user = User.objects.get(username=username)
    allSubmission = Submission.objects.all()
    userQueSub = list()

    for submissions in allSubmission:
        if submissions.user == user:
            userQueSub.append(submissions)
    var = calculate()
    if var != 0:
        return render(request, 'RC/submission.html', context={'allSubmission': userQueSub, 'time': var})
    else:
        return render(request, 'RC/RESULTRC.html')


def leader(request):
    dict = {}
    for user in UserProfile.objects.order_by("-totalScore"):
        list = []
        for n in range(1, 7):
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
        return render(request, 'RC/leaderb.html',context={'dict': dict, 'range': range(1, 7, 1), 'time': var})
    else:
        return render(request, 'RC/RESULTRC.html')


def user_logout(request):
    user = UserProfile.objects.get(user=request.user)
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
    return render(request, 'RC/RESULTRC.html',
                  context={'dict': dict, 'rank': i, 'name': user.user, 'score': user.totalScore})


def codeSave(request, username, qn):
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

        codefile = open("{}/{}/question{}/code{}-{}.{}".format(path_usercode, username, qn, qn, att, extension), "w+")
        codefile.write(content)
        codefile.close()

        ans = subprocess.Popen(['python2', "{}/data/Judge/main.py".format(path), path, username, str(qn), str(att),
                                extension, "{}/{}/question{}/code{}-{}.{}".format(path_usercode, username, qn, qn, att,
                                                                                  extension)], stdout=subprocess.PIPE)
        (out, err) = ans.communicate()
        submission = Submission(code=content, user=user, que=que, attempt=att, out=out)
        submission.save()

        mul_que.attempts += 1
        mul_que.save()

        return redirect("runCode", username=username, qn=qn, att=att)

    elif request.method == 'GET':
        que = Question.objects.get(pk=qn)
        user = User.objects.get(username=username)
        var = calculate()
        if var != 0:
            return render(request, 'RC/codingrcblue2 (2).html', context={'question': que, 'user': user, 'time': var})
        else:
            return render(request, 'RC/RESULTRC.html')


def runCode(request, username, qn, att):
    user = User.objects.get(username=username)
    que = Question.objects.get(pk=qn)
    try:
        mul_que = MultipleQues.objects.get(user=user, que=que)
    except MultipleQues.DoesNotExist:
        mul_que = MultipleQues(user=user, que=que)

    submission = Submission.objects.get(user=user, que=que, attempt=att)

    '''
        os.popen('python2 data/Judge/main.py ' + '{}/{}/question{}/code{}-{}.{}'.format(path_usercode, username, qn, qn,
             attempts-1, user_profile.choice) + ' ' + username + ' ' + str(qn))

        code will have text in form '1020301020'
        output_list will contain (10, 20, 30, 10, 20)  for 5 test cases

        Sandbox will return(save) these values in total_output.txt
        10 = right answer (PASS)
        20 = wrong answer (WA)
        30 = Time Limit Exceed (TLE)
        40 = compile time error (CTE)
    '''

    code = int(submission.out)
    output_list = list()
    correct_list = list()

    for i in range(0, NO_OF_TEST_CASES):
        correct_list.append('PASS')  # list of all PASS test Cases

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
        code = int(code / 100)
        print(code)

    print(output_list)
    print(correct_list)

    if output_list == correct_list:  # if all are correct then Score = 100
        mul_que.scoreQuestion = 100

    com_time_error = False
    tle_error = False
    wrg_ans = False

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

    error_text = 'No Error Found, Complied Successfully!'
    if com_time_error:
        for i in output_list:  # assigning each element with 40 (CTE will be for every test case)
            i = 40
        error_path = path_usercode + '/{}/question{}'.format(username, qn)
        error_file = open('{}/error.txt'.format(error_path), 'r')
        error_text = error_file.read()

    no_of_pass = 0
    for i in output_list:
        if i == 'PASS':
            no_of_pass += 1

    submission.correctTestCases = no_of_pass
    submission.TestCasesPercentage = (no_of_pass / NO_OF_TEST_CASES) * 100
    submission.save()

    dict = {'com_status': submission.subStatus, 'output_list': output_list, 'score': mul_que.scoreQuestion, 'error':
        error_text}

    return render(request, 'RC/testcases.html', dict)

