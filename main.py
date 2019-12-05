import parse
from collections import namedtuple
import getch
import sys
from sys import argv
import signal

aborted = False

def handler(signum, frame):
    global aborted
    aborted = True

#substitution subs is a dict

def is_var(term):
    return term.name[0] == '/'

def stand_name(s, depth):
    return "//" + str(depth) + s

#substitute
def sas_term(term, depth, subs):
    if term.name[0] == '/': #is_var(term) but inline
        if term.name in subs:
            return subs[term.name]
        elif term.name[1] != '/':
            #standarize
            return parse.Term(name = stand_name(term.name, depth), arg = [])
        else:
            return term
    else:
        new_arg = [sas_term(x, depth, subs) for x in  term.arg]
        return parse.Term(name = term.name, arg = new_arg)

def sas_lterm(lterm, depth, subs):
    return [sas_term(x, depth, subs) for x in  lterm]

def term_equal(p, q):
    if p.name != q.name or len(p.arg) != len(q.arg):
        return False

    for x, y in zip(p.arg, q.arg):
        if not term_equal(x, y):
            return False

    return True

def has_variable(term, var_name):
    if is_var(term):
        return term.name == var_name

    for x in term.arg:
        if has_variable(x, var_name):
            return True

    return False

#two list of equation :))
#simple unify, not fully replaced all term, and can be contradictory
#guarantee to return a dict
def simple_unify(t1, t2, subs):
    if not is_var(t1) and not is_var(t2):
        if t1.name != t2.name or len(t1.arg) != len(t2.arg):
            #conflict
            return False
        else:
            for x, y in zip(t1.arg, t2.arg):
                if not simple_unify(x, y, subs):
                    return False
    else:
        if is_var(t2):
            t1, t2 = t2, t1

        if is_var(t2) and t1.name == t2.name:
            return True

        if t1.name in subs:
            if not simple_unify(subs[t1.name], t2, subs):
                return False
        else:
            subs[t1.name] = t2

    return True

#replacify
def remove_ref(subs):
    def remove_ref_term(term, d, done, stack):
        if is_var(term):
            if term.name in stack:
                return None #self recursive
            elif term.name in done:
                return done[term.name] #done need to do recursive
            elif term.name in d:
                new_term = d.pop(term.name)

                stack.add(term.name)
                new_term = remove_ref_term(new_term, d, done, stack)
                stack.remove(term.name)

                done[term.name] = new_term
                return new_term
            else:
                return term
        else:
            new_term = parse.Term(term.name, [ None ] * len(term.arg))
            for i in range(len(term.arg)):
                new_term.arg[i] = remove_ref_term(term.arg[i], d, done, stack)
                if new_term.arg[i] is None:
                    return None

            return new_term

    d = dict(subs)
    done = {}

    while d:
        next_var = parse.Term(next(iter(d)), [])
        if remove_ref_term(next_var, d, done, set()) is None:
            return None
    
    return done

def stand_term(term, depth):
    if is_var(term) and term.name[1] != '/':
        return parse.Term(name = stand_name(term.name, depth), arg = [])
    else:
        return parse.Term(name = term.name, arg = [stand_term(x, depth) for x in term.arg])

def lterm_to_string(lterm, full):
    return ','.join([term_to_string(x, full) for x in lterm])

def need_quote(s):
    for c in s:
        if not c.isalnum() and c != '_':
            return True
    return False

def name_to_string(term, full):
    if is_var(term):
        if full:
            return term.name[1:]
        elif term.name[:4] != "//0/":
            return '_'
        else:
            return term.name[4:]

    elif need_quote(term.name):
        return f"'{term.name}'"
    else:
        return term.name

def term_to_string(term, full):
    if not term.arg:
        return name_to_string(term, full)
    else:
        return name_to_string(term, full) + '(' + lterm_to_string(term.arg, full) + ')'

def print_term(term, full):
    print(term_to_string(term, full), endl = '')

def print_lterm(lterm, full):
    print(lterm_to_string(lterm, full), end = '')

def print_subs(subs, full):
    s = []
    for x, y in subs.items():
        x = parse.Term(x, [])
        if not full and (x.name[:4] != "//0/" or x.name[4] == '_'):
            continue
        
        s.append(f"{name_to_string(x, full)} = {term_to_string(y, full)}")
    
    if not s:
        print('yes', end = '')
    else:
        print(', '.join(s), end = '')
    sys.stdout.flush()

def print_rule(rule, full):
    print(term_to_string(rule.imp, full), " :- ", lterm_to_string(rule.pcnd, full), end = '')

def is_cut(term):
    return len(term.arg) == 0 and term.name == "!"

def is_fail(term):
    return len(term.arg) == 0 and term.name == "fail"

def is_not(term):
    return len(term.arg) == 1 and term.name == "not"

def is_smaller(term):
    return len(term.arg) == 2 and term.name == "smaller"

def unify(eq1, eq2):
    new_subs = dict()
    if not simple_unify(eq1, eq2, new_subs):
        return None

    return remove_ref(new_subs)

def trace_subs(subs_stack):
    merge_subs = {}
    for idx, subs in enumerate(subs_stack):
        for var, term in subs.items():
            if var[:2] != '//':
                var = stand_name(var, idx + 1)
            merge_subs[var] = term
    
    return remove_ref(merge_subs)


#return found, continue
def backchain_ask(kb, goal, subs_stack, depth, prove):
    global aborted
    if aborted:
        return False, False

    if len(goal) == 0:
        if prove:
            return True, False

        subs = trace_subs(subs_stack)
        print_subs(subs, False)

        c = getch.getch()
        print(';' if c == ';' else '.')
        return True, c == ';'

    q = goal[0]

    if is_fail(q):
        return False, True

    if is_not(q):
        found, _ = backchain_ask(kb, q.arg, subs_stack, depth, True)
        if found:
            #if provable then no
            return False, True
        else:
            #if not provable then continue
            return backchain_ask(kb, goal[1:], subs_stack, depth, prove)

    if is_cut(q):
        found, _ = backchain_ask(kb, goal[1:], subs_stack, depth, prove)
        return found, False

    if is_smaller(q):
        if term_to_string(q.arg[0], True) < term_to_string(q.arg[1], True):
            return backchain_ask(kb, goal[1:], subs_stack, depth, prove)
        else:
            return False, True

    found = False
    cont = True

    for p in kb:
        if aborted:
            return found, False

        new_subs = unify(p.imp, q)

        if new_subs is None:
            continue

        for x, y in new_subs.items():
            new_subs[x] = stand_term(y, depth)

        new_goal = sas_lterm(p.pcnd + goal[1:], depth, new_subs)

        subs_stack.append(new_subs)
        f, cont = backchain_ask(kb, new_goal, subs_stack, depth + 1, prove)
        subs_stack.pop()

        found = found or f
        
        if found and prove:
            return True, False #already found one instance

        if not cont:
            break

    return found, cont

def inference(kb, goal):
    #backward chaining
    global aborted
    aborted = False
    goal = sas_lterm(goal, 0, {})
    found, _ = backchain_ask(kb, goal,[], 1, False)
    if aborted:
        print("\raborted")
    elif not found:
        print('no.')

def parse_goal(s):
    n, lterm = parse.parse_list_term(s, 0, len(s))
    if n != len(s) and s[n] != '.':
        raise Exception(f"{n + 1}: Unexpected end token {s[n]}")

    return lterm

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
            break
        else:
            try:
                goal = parse_goal(goal)
            except Exception as e:
                print(str(e))
            else:
                inference(kb, goal)