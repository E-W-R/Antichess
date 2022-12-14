from subprocess import Popen, PIPE

script1 = Popen(["python3", "main.py", "white"], stdin=PIPE, stdout=PIPE)
script2 = Popen(["python3", "main.py", "black"], stdin=PIPE, stdout=PIPE)

while True:
    output1 = script1.stdout.readline()
    print(output1)
    script2.stdin.write(output1)
    script2.stdin.flush()

    output2 = script2.stdout.readline()
    print(output2)
    script1.stdin.write(output2)
    script1.stdin.flush()