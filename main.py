import interpreter
import parse
import getch
import sys
from sys import argv
import signal

def handler(signum, frame):
    global aborted
    aborted = True

def inference(kb, goal):
    #backward chaining
    gen = interpreter.inference(kb, goal)
    try:
        found = False
        for subs in gen:
            found = True
            print(interpreter.subs_to_string(subs, False), end = '')
            sys.stdout.flush()

            c = getch.getch()
            print(';' if c == ';' else '.')
            if c != ';':
                break
            
        if not found:
            print('no.')
    except Exception as e:
        print("\r" + str(e))

signal.signal(signal.SIGINT, handler)

if len(argv) != 2:
    print("Usage: python3 main.py <file.pl>")
    print("python >=3.6")
    print("Not support number, ; yet")
    quit()

try:
    kb = parse.load_kb(argv[1])    
except Exception as e:
    print(str(e))
else:
    while True:
        try:
            goal = input("?- ")
        except Exception as e:
            print("halt")
            quit()

        try:
            goal = parse.parse_goal(goal)
        except Exception as e:
            print(str(e))
        else:
            inference(kb, goal)