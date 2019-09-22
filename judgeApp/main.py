import resource
import subprocess


def initialize_quota(quota, lang):
    cpu_time = quota['time']
    mem = quota['mem']

    if lang == 'py':
        cpu_time = 5

    def setlimits():
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_time, cpu_time))
        resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
        # resource.setrlimit(resource.RLIMIT_STACK, (1310720, 1310720))

    return setlimits


def run_in_sandbox(exec_path, lang, ipf, opf, errf, quota):
    if lang == 'py':
        child = subprocess.Popen(
            ['python3 ' + exec_path], preexec_fn=initialize_quota(quota, lang),
            stdin=ipf, stdout=opf, stderr=errf, shell=True
        )
    else:
        child = subprocess.Popen(
            ['./' + exec_path], preexec_fn=initialize_quota(quota, lang),
            stdin=ipf, stdout=opf, stderr=errf, shell=True
        )

    child.wait()
    rc = child.returncode

    if rc < 0:
        return 128 - rc
    else:
        return rc
