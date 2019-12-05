import interpreter
import parse
import getch
import sys
from sys import argv
import signal

def handler(signum, frame):
    global aborted
    aborted = True

def parse_goal(s):
    n, lterm = parse.parse_list_term(s, 0, len(s))
    if n != len(s) and s[n] != '.':
        raise Exception(f"{n + 1}: Unexpected end token {s[n]}")

    return lterm

def inference(kb, goal):
    #backward chaining
    gen = interpreter.inference(kb, goal)
    try:
        found = False
        for subs_stack in gen:
            found = True
            subs = interpreter.trace_subs(subs_stack)
            interpreter.print_subs(subs, False)

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
            goal = parse_goal(goal)
        except Exception as e:
            print(str(e))
        else:
            inference(kb, goal)