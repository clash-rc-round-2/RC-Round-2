import os, sys, subprocess

path = sys.argv[1]
user = sys.argv[2]
que = int(sys.argv[3])
att = int(sys.argv[4])
lang = sys.argv[5]
file = sys.argv[6]

try :
    # check platform type
    system, machine = os.uname()[0], os.uname()[4]
    if system not in ('Linux',) or machine not in ('i686', 'x86_64',) :
        raise AssertionError("Unsupported platform type.\n")
    # check package availability / version
    import sandbox

    if not hasattr(sandbox, '__version__') or sandbox.__version__ < "0.3.4-3" :
        raise AssertionError("Unsupported sandbox version.\n")
    from sandbox import *
except ImportError :
    sys.stderr.write("Required package(s) missing.\n")
    sys.exit(os.EX_UNAVAILABLE)
except AssertionError as e :
    sys.stderr.write(str(e))
    sys.exit(os.EX_UNAVAILABLE)

NO_OF_QUESTIONS = 6

path_userCode = path + '/data/usersCode'
input_path = path + '/data/standard/input'
output_path = path + '/data/standard/output'


def compile(user, extension, que, att, err) :
    return_value = 1  # By default error while running file.
    if extension == 'c':
        return_value = os.system("gcc " + file + " -o " + "{}/{}/question{}/solution{}".format(path_userCode,user,que,que) + " -lm 2> " + err)

    elif extension == 'cpp':
        return_value = os.system("g++ " + file + " -o " + "{}/{}/question{}/solution{}".format(path_userCode,user,que,que) + " -lm 2> " + err)

    return return_value  # return 0 for success and 1 for error


def run_test_cases(test_case_no, filename, user, que, att) :
    input_file = "{}/question{}/input{}.txt".format(input_path, que, test_case_no)
    input_f = open(input_file, "r")  # standard input
    user_out_file = '{}/{}/question{}/output{}.txt'.format(path_userCode, user, que, test_case_no)
    user_out_f = os.open(user_out_file, os.O_RDWR | os.O_CREAT)  # user's output

    result_value = config_sandbox(que, input_f, user_out_f)
    input_f.close()

    os.close(user_out_f)

    e_output_file = '{}/question{}/expected_output{}.txt'.format(output_path, que, test_case_no)

    if result_value == 1:                                               # !!!This is the success value
        result_value = compare(user_out_file, e_output_file)
    elif result_value == 5:                                             # !!! Add statements for other codes as well
        result_value = 30
    # elif result_value:
    #     result_value = 50
    else:
        result_value = 60

    return result_value


def config_sandbox(que, in_file_fd, user_out_fd):
    cookbook = {
        'args': "{}/{}/question{}/solution{}".format(path_userCode, user, que, que),  # targeted program
        'stdin': in_file_fd,  # input to targeted program
        'stdout': user_out_fd,  # output from targeted program
        'stderr': sys.stderr,  # error from targeted program
        'quota': dict(wallclock=30000,  # 30 sec
                       cpu=2000,  # 2 sec
                       memory=268435456,  # 256 MB
                       disk=1048576)
    }  # 1 MB
    # create a sandbox instance and execute till end
    msb = sandbox.Sandbox(**cookbook)
    msb.run()
    # print "\n"
    d = Sandbox.probe(msb)
    d['cpu'] = d['cpu_info'][0]
    d['mem'] = d['mem_info'][1]
    d['result'] = msb.result
    # print("This is the output code", msb.result)
    return msb.result


def compare(user_out, e_out):
    user = open(user_out)
    expected = open(e_out)

    lines_user = user.readline()
    l1 = [i.strip() for i in lines_user]
    lines_expected = expected.readline()
    l2 = [i.strip() for i in lines_expected]
    if len(l1) == len(l2):
        for i in range(len(l1)):  # check if files of equal length
            if l1[i] == l2[i]:
                flag = 1
            else :
                flag = 0
                break
        if flag == 1:
            flag = 10
            return flag
        else:
            # print "not same"
            flag = 20
            return flag

    return 20


def main():
    filename = file.split(".")[0]  # FileName
    extension = file.split(".")[1]  # C or CPP or python

    error_file = "{}/{}/question{}/error.txt".format(path_userCode,user,que)
    if not os.path.isfile(error_file):
        error_fd=os.open(error_file, os.O_WRONLY|os.O_CREAT)
        os.close(error_fd)
    else:
        os.remove(error_file)
        error_fd = os.open(error_file, os.O_WRONLY | os.O_CREAT)
        os.close(error_fd)

    result = []
    return_value = compile(user, extension, que, att, error_file)  # calling compile()

    if return_value == 0:
        os.remove(error_file)
        for i in range(0, 5):
            run_code = run_test_cases(i + 1, filename, user, que, att)  # calling runTestCases()
            result.append(run_code)
    else :
        result = [40, 40, 40, 40, 40]

    return result


p = main()

ans = 0
ans = p[0]

if ans != 40:
    for i in range(0, 5):
        ans = ans*100+p[i]
else:
    ans = 4040404040

print(str(ans))
sys.exit(0)

# 10 = right answer
# 20 = wrong answer
# 30 = TLE
# 40 = compile time error
# 50 = RTE : core Dumped
# 60 = Abnormal Termination
