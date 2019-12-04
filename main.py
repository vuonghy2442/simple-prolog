import parse
from collections import namedtuple
import getch
import sys

#substitution subs is a dict

def is_var(term):
    if term.name[0].isupper():
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

def subs_to_dict(subs):
    d = {}
    for x, y in zip(*subs):
        assert(is_var(x))
        d[x.name] = y
    return d

def subs_to_set(subs):
    return set([x.name for x in subs[0]])

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
def unify(eq1, eq2, done_var = set()):
    assert(len(eq1) == len(eq2))

    if len(eq1) == 0:
        return []

    change = True

    while change:
        change = False

        new_eq1 = []
        new_eq2 = []
        for i in range(len(eq1)):
            t1 = eq1[i]
            t2 = eq2[i]
            #delete
            if term_equal(t1, t2):
                continue

            #decompose
            if not is_var(t1) and not is_var(t2):
                if t1.name != t2.name or len(t1.arg) != len(t2.arg):
                    #conflict
                    return None
                else:
                    change = True
                    new_eq1 += t1.arg
                    new_eq2 += t2.arg
                    continue
        
            #swap
            if not is_var(t1) and is_var(t2):
                t = t1
                t1 = t2
                t2 = t

            #eliminate
            if is_var(t1):
                #check if recursive
                if has_variable(t2, t1.name):
                    return None #since we check if they are equal in the first
                elif t1.name not in done_var:
                    change = True
                    done_var.add(t1.name)

                    new_eq1 += eq1[i + 1:]
                    new_eq2 += eq2[i + 1:]
                    
                    new_eq1 = lsubstitute(new_eq1, {t1.name : t2})
                    new_eq2 = lsubstitute(new_eq2, {t1.name : t2})

                    new_eq1.append(t1)
                    new_eq2.append(t2)
                else:
                    #done var is always at the end
                    new_eq1 += eq1[i:]
                    new_eq2 += eq2[i:]
                break

        eq1 = new_eq1
        eq2 = new_eq2

    return (eq1, eq2)

def stand_term(term, idx):
    if is_var(term):
        return parse.Term(name = term.name + "/" + str(idx), arg = [])
    else:
        return parse.Term(name = term.name, arg = [stand_term(x, idx) for x in term.arg])

#change variable name so that they won't overlap
def standardize(sen, idx):
    return parse.Sentence(imp = stand_term(sen.imp, idx), pcnd =  [stand_term(x, idx) for x in sen.pcnd])

#change to a canonical name
def term_rename(term, subs):
    if is_var(term):
        if term.name in subs:
            return subs[term.name]
        else:
            new_term = parse.Term(name = "/" + str(len(subs)), arg = [])
            subs[term.name] = new_term
            return new_term 
    else:
        return parse.Term(name = term.name, arg = [term_rename(x, subs) for x in term.arg])

def lterm_rename(lterm, subs):
    return [term_rename(x, subs) for x in lterm]

def lterm_to_string(lterm):
    return ','.join([term_to_string(x) for x in lterm])

def term_to_string(term):
    if len(term.arg) == 0:
        return term.name
    else:
        return term.name + '(' + lterm_to_string(term.arg) + ')'

def print_subs(subs):
    s = []
    for x, y in zip(*subs):
        assert(is_var(x))
        if x.name.find("/") >= 0:
            continue

        s.append(f"{x.name} = {term_to_string(y)}")
    
    if len(s) == 0:
        print('yes', end = '')
    else:
        print(', '.join(s), end = '')
    sys.stdout.flush()

def is_cut(term):
    return len(term.arg) == 0 and term.name == "!"

def is_fail(term):
    return len(term.arg) == 0 and term.name == "fail"

def is_not(term):
    return len(term.arg) == 1 and term.name == "not"

def is_smaller(term):
    return len(term.arg) == 2 and term.name == "smaller"

#return found, continue
def backchain_ask(kb, goal, subs, depth, prove):
    if len(goal) == 0:
        if prove:
            return True, False

        print_subs(subs)

        c = getch.getch()
        print(';' if c == ';' else '.')
        return True, c == ';'

    q = substitute(goal[0], subs_to_dict(subs))

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
        if term_to_string(q.arg[0]) < term_to_string(q.arg[1]):
            return backchain_ask(kb, goal[1:], subs, depth, prove)
        else:
            return False, True

    found = False
    cont = True

    for p in kb:
        p = standardize(p, depth)
        subs2 = unify([p.imp] + subs[0], [q] + subs[1], subs_to_set(subs))
        if subs2 is not None:
            new_goal = p.pcnd + goal[1:]
            f, cont = backchain_ask(kb, new_goal, subs2, depth + 1, prove)
            found = found or f
            
            if found and prove:
                return True, False #already found one instance

            if not cont:
                break

    return found, cont

def inference(kb, goal):
    #backward chaining
    found, _ = backchain_ask(kb, goal, ([], []), 0, False)
    if not found:
        print('no.')

def parse_goal(s):
    n, lterm = parse.parse_list_term(s, 0, len(s))
    if n != len(s) and s[n] != '.':
        raise Exception(f"{n + 1}: Unexpected end token {s[n]}")

    return lterm

from sys import argv

if len(argv) != 2:
    print("Usage: python3 main.py <file.pl>")
    print("python >=3.6")
    print("Not support number, ; yet")

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