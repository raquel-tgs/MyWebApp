# import subprocess
#
# output = subprocess.check_call(["git", "status"], stdin=None, stdout=None, stderr=None, shell=False)
#
# print("")


#test 2
# from subprocess import Popen, PIPE, CalledProcessError
#
# with Popen(["c:\\tgspoc\\check.bat", "status"], stdout=PIPE, bufsize=1, universal_newlines=True) as p:
#     for line in p.stdout:
#         print(line, end='') # process line here
#
# if p.returncode != 0:
#     raise CalledProcessError(p.returncode, p.args)
#
# print("")


#test 3
import subprocess
# from contextlib import ExitStack
# from subprocess import Popen
#
# def kill(process):
#     if process.poll() is None:  # still running
#         process.kill()
#
# stack = ExitStack()  # to clean up properly in case of exceptions
# process=stack.enter_context(Popen(["c:\\tgspoc\\check.bat", "status"]))  # start program
# process.wait()
#
# print("sss")
# stack.callback(kill, process)

#test 4
import os
import signal
import subprocess

# The os.setsid() is passed in the argument preexec_fn so
# it's run after the fork() and before  exec() to run the shell.
cmd="c:\\tgspoc\\check.bat"
p = subprocess.Popen( cmd, stdout=subprocess.PIPE, shell=True)

p.killpg()
print("d")