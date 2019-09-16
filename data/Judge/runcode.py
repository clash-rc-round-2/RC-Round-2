import os,sys,subprocess

path = sys.argv[1]
path_usercode = sys.argv[2]
username = sys.argv[3]
que_no = int(sys.argv[4])
ext = sys.argv[5]

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

def config_sandbox(que,user ,in_file_fd, user_out_fd):
    cookbook = {
        'args': "{}/{}/question{}/sample".format(path_usercode,user, que),  # targeted program
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
    else:
        return 20

def runcode():
    input_file = "{}/data/standard/input/question{}/input1.txt".format(path, que_no)
    e_output_file = "{}/data/standard/output/question{}/expected_output1.txt".format(path, que_no)
    err_file = "{}/{}/question{}/error.txt".format(path_usercode, username, que_no)
    error = open(err_file, "w+")

    return_value = 0
    file_fd = "{}/{}/question{}/sample.{}".format(path_usercode, username, que_no, ext)
    if ext == 'c':
        return_value = os.system("gcc " + file_fd + " -o " + "{}/{}/question{}/sample".format(path_usercode, username,que_no) + " -lm 2> " + err_file)

    elif ext == 'cpp':
        return_value = os.system("g++ " + file_fd + " -o " + "{}/{}/question{}/sample".format(path_usercode, username,que_no) + " -lm 2> " + err_file)
    error.close()

    if return_value == 0:
        input_f = open(input_file, "r")
        user_out_file = '{}/{}/question{}/sample_out.txt'.format(path_usercode, username, que_no)
        user_out_f = os.open(user_out_file, os.O_RDWR | os.O_CREAT)

        return_value = config_sandbox(que_no, username, input_f, user_out_f)
        input_f.close()
        os.close(user_out_f)

        if return_value == 1:
            result_value = compare(user_out_file, e_output_file)
        elif return_value == 5:
            result_value = 30
        elif return_value == 6:
            result_value = 50
        else:
            result_value = 60
    else:
        result_value = 40

    return result_value

result = runcode()
print(str(result))
sys.exit(0)