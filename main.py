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
    if term.name[0] == '/':
        if (len(term.arg) > 0):
            raise Exception("Variable cannot have arguments")
        return True
    
    return False

def substitute(term, subs):
    if is_var(term):
        if term.name in subs:
            return subs[term.name]
        else:
            return term
    else:
        new_arg = [substitute(x, subs) for x in term.arg]
        return parse.Term(name = term.name, arg = new_arg)

def lsubstitute(lterm, subs):
    return [substitute(x, subs) for x in  lterm]

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
def simple_unify(eq1, eq2, subs):
    assert(len(eq1) == len(eq2))

    for i in range(len(eq1)):
        t1 = eq1[i]
        t2 = eq2[i]
        
        if term_equal(t1, t2):
            continue

        if not is_var(t1) and not is_var(t2):
            if t1.name != t2.name or len(t1.arg) != len(t2.arg):
                #conflict
                return False
            else:
                if not simple_unify(t1.arg, t2.arg, subs):
                    return False
        else:
            if is_var(t2):
                t = t1
                t1 = t2
                t2 = t

            if t1.name in subs:
                if not simple_unify([subs[t1.name]], [t2], subs):
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
            for i in range(len(term.arg)):
                term.arg[i] = remove_ref_term(term.arg[i], d, done, stack)
                if term.arg[i] is None:
                    return None

            return term

    d = dict(subs)
    done = {}

    while len(d) > 0:
        next_var = parse.Term(next(iter(d)), [])
        if remove_ref_term(next_var, d, done, set()) is None:
            return None
    
    return done

def stand_term(term, idx):
    if is_var(term):
        return parse.Term(name = term.name + "//" + str(idx), arg = [])
    else:
        return parse.Term(name = term.name, arg = [stand_term(x, idx) for x in term.arg])

#change variable name so that they won't overlap
def standardize(sen, idx):
    return parse.Sentence(imp = stand_term(sen.imp, idx), pcnd =  [stand_term(x, idx) for x in sen.pcnd])

def lterm_to_string(lterm, full):
    return ','.join([term_to_string(x, full) for x in lterm])

def need_quote(s):
    for c in s:
        if not c.isalnum() and c != '_':
            return True
    return False

def name_to_string(term, full):
    if is_var(term):
        if not full and term.name.find("//") >= 0:
            return '_'
        else:
            return term.name[1:]
    elif need_quote(term.name):
        return f"'{term.name}'"
    else:
        return term.name

def term_to_string(term, full):
    if len(term.arg) == 0:
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
        if not full and x.name.find("//") >= 0:
            continue
        
        s.append(f"{name_to_string(x, full)} = {term_to_string(y, full)}")
    
    if len(s) == 0:
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

def unify(eq1, eq2, subs):
    new_subs = dict(subs)
    if not simple_unify(eq1, eq2, new_subs):
        return None

    return remove_ref(new_subs)

#return found, continue
def backchain_ask(kb, goal, subs, depth, prove):
    global aborted
    if aborted:
        return False, False

    if len(goal) == 0:
        if prove:
            return True, False

        print_subs(subs, False)

        c = getch.getch()
        print(';' if c == ';' else '.')
        return True, c == ';'

    q = substitute(goal[0], subs)

    if is_fail(q):
        return False, True

    if is_not(q):
        found, _ = backchain_ask(kb, q.arg, subs, depth, True)
        if found:
            #if provable then no
            return False, True
        else:
            #if not provable then continue
            return backchain_ask(kb, goal[1:], subs, depth, prove)

    if is_cut(q):
        found, _ = backchain_ask(kb, goal[1:], subs, depth, prove)
        return found, False

    if is_smaller(q):
        if term_to_string(q.arg[0], True) < term_to_string(q.arg[1], True):
            return backchain_ask(kb, goal[1:], subs, depth, prove)
        else:
            return False, True

    found = False
    cont = True

    print('-'*40)
    for p in kb:
        if aborted:
            return found, False

        p = standardize(p, depth)

        new_subs = unify([p.imp], [q], subs)

        if new_subs is None:
            continue

        new_goal = p.pcnd + goal[1:]

        print('  ' * depth + "use rule: ", end = '')
        print_rule(p, True)
        print("\n" + '  ' * depth +  "subs: ", end = '')
        print_subs(new_subs, True)
        print("\n" + '  ' * depth + "goals:", end = '')
        print_lterm(new_goal, True)
        print()

        f, cont = backchain_ask(kb, new_goal, new_subs, depth + 1, prove)
        found = found or f
        
        if found and prove:
            return True, False #already found one instance

        if not cont:
            break

    print('  ' * depth + "Backtrack")
    print('-' * 40)

    return found, cont

def inference(kb, goal):
    #backward chaining
    global aborted
    aborted = False
    found, _ = backchain_ask(kb, goal, {}, 0, False)
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