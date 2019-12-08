import interpreter
import parse
import getch
import sys
from sys import argv
import signal

# Handle ctrl+C
def handler(signum, frame):
    interpreter.abort_inference()

# Do inference and interacting with terminal
def inference(kb, goal):
    gen = interpreter.inference(kb, goal)

    try:
        found = False
        for res in gen:
            found = True
            # Print out the result
            print(interpreter.result_to_string(res), end = '')

            # Without flush the output is not shown yet when we getch
            sys.stdout.flush()
            c = getch.getch()
            print(';' if c == ';' else '.')
            # Only continue to print more result when input ';'
            if c != ';':
                break

        # If no solution is found then print no.
        if not found:
            print('no.')
    except Exception as e:
        print("\r" + str(e))
    print()
    # Clean up
    del gen

def main():
    signal.signal(signal.SIGINT, handler)

    if len(argv) > 2:
        print("Usage: python3 main.py <file.pl>")
        print("python >=3.6")
        print("Not support number, list yet")
        quit()

    if len(argv) == 2:
        # Tries to load the knowledge base, if there is any parsing error shown
        try:
            kb = parse.load_kb(argv[1])
        except Exception as e:
            print(str(e))
            return
    else:
        # If user does not input .pl file then init an empty kb
        kb = []

    # repeatedly get the query
    while True:
        try:
            goal = input("?- ")
        except Exception as e:
            # When get EOF (from ctrl-D)
            print("halt")
            return

        # Tries to parse the query
        try:
            goal = parse.parse_goal(goal)
            pass
        except Exception as e:
            print(str(e))
        else:
            # Do inference
            inference(kb, goal)

if __name__ == "__main__":
    main()