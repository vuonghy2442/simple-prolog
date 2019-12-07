import parse
from collections import namedtuple

aborted = False

def abort_inference():
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
        #standarize
        if term.name[1] != '/':
            term = parse.Term(name = stand_name(term.name, depth), arg = [])

        if term.name in subs:
            return subs[term.name]
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
    #if not is_var(t1) and not is_var(t2):
    if t1.name[0] != '/' and t2.name[0] != '/':
        if t1.name != t2.name or len(t1.arg) != len(t2.arg):
            #conflict
            return False
        else:
            for x, y in zip(t1.arg, t2.arg):
                if not simple_unify(x, y, subs):
                    return False
    else:
        #one of them is variable so it has / in the name
        if t1.name == t2.name:
            return True

        #if is_var(t2):
        if t2.name[0] == '/':
            t1, t2 = t2, t1

        if t1.name in subs:
            if not simple_unify(subs[t1.name], t2, subs):
                return False
        else:
            subs[t1.name] = t2

    return True

#replacify
def remove_ref(subs, depth):
    def remove_ref_term(term, depth, d, done, stack):
        if is_var(term):
            #standardize here
            old_term = term

            #standardizing name
            if depth >= 0 and term.name[1] != '/':
                term =  parse.Term(name = stand_name(term.name, depth), arg = [])

            if term.name in stack:
                return None #self recursive
            elif term.name in done:
                return done[term.name] #done need to do recursive
            elif old_term.name in d:
                new_term = d.pop(old_term.name)

                stack.add(term.name)
                new_term = remove_ref_term(new_term, depth, d, done, stack)
                stack.remove(term.name)

                #already standardize
                done[term.name] = new_term
                return new_term
            else:
                #already standardize
                return term
        else:
            new_term = parse.Term(term.name, [ None ] * len(term.arg))
            for i in range(len(term.arg)):
                new_term.arg[i] = remove_ref_term(term.arg[i], depth, d, done, stack)
                if new_term.arg[i] is None:
                    return None

            return new_term

    d = dict(subs)
    done = {}

    while d:
        next_var = parse.Term(next(iter(d)), [])
        if remove_ref_term(next_var, depth, d, done, set()) is None:
            return None
    
    return done

def stand_var(term, depth):
    assert(is_var(term))
    if term.name[1] != '/':
        return parse.Term(name = stand_name(term.name, depth), arg = [])
    else:
        return term

def lterm_to_string(lterm, full):
    return ','.join([term_to_string(x, full) for x in lterm])

def need_quote(s):
    if not s[0].isalpha():
        return True

    for c in s:
        if not c.isalnum() and c != '_':
            return True
    return False

def name_to_string(term, full):
    if is_var(term):
        if full:
            return term.name[1:]
        elif term.name.find("_") >= 0:
            return '_'
        elif term.name[:2] != '//':
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

def filter_subs(subs):
    new_subs = {}

    for x, y in subs.items():
        if x[:4] != "//0/" or x[4] == '_':
            continue
        new_subs[x] = y

    return new_subs

def subs_to_string(subs, full):
    s = []
    for x, y in subs.items():
        x = parse.Term(x, [])
        s.append(f"{name_to_string(x, full)} = {term_to_string(y, full)}")
    
    s.sort()

    if not s:
        return 'yes'
    else:
        return ', '.join(s)

def is_true(term):
    return len(term.arg) == 0 and term.name == "true"

def is_cut(term):
    return len(term.arg) == 0 and term.name == "!"

def is_fail(term):
    return len(term.arg) == 0 and term.name == "fail"

def is_not(term):
    return len(term.arg) == 1 and (term.name == "not" or term.name == '\\+')

def is_smaller(term):
    return len(term.arg) == 2 and term.name == "@<"

def is_rule(term):
    return len(term.arg) == 2 and term.name == ":-"

def is_equal(term):
    return len(term.arg) == 2 and term.name == "="

def is_conjuction(term):
    return term.name == ","

def is_disjuction(term):
    return term.name == ";"


def unify(eq1, eq2, depth):
    new_subs = dict()
    if not simple_unify(eq1, eq2, new_subs):
        return None

    return remove_ref(new_subs, depth)

def trace_subs(subs_stack):
    merge_subs = {}
    for idx, subs in enumerate(subs_stack):
        for var, term in subs.items():
            if var[:2] != '//':
                var = stand_name(var, idx + 1)
            merge_subs[var] = term
    
    return remove_ref(merge_subs, -1)

#p and q need to unify
#cond is the condition list need to satify
#goal is the rest of the goal
def matching(p, q, cond, kb, goal, subs_stack, depth, std):
    new_subs = unify(p, q, depth if std else -1)

    if new_subs is None:
        return True

    new_goal = sas_lterm(cond + goal, depth, new_subs)

    subs_stack.append(new_subs)
    if not (yield from backchain_ask(kb, new_goal, subs_stack, depth + 1)):
        return False
    subs_stack.pop()

    return True

#return found, continue
def backchain_ask(kb, goal, subs_stack, depth):
    global aborted
    if aborted:
        return False

    if len(goal) == 0:
        yield subs_stack
        return True

    q = goal[0]

    if is_true(q):
        return (yield from backchain_ask(kb, goal[1:], subs_stack, depth)) 

    if is_fail(q):
        return True

    if is_not(q):
        gen = backchain_ask(kb, q.arg, subs_stack, depth)
        try:
            next(gen)
        except StopIteration:
            return (yield from backchain_ask(kb, goal[1:], subs_stack, depth))
        return True

    if is_cut(q):
        yield from backchain_ask(kb, goal[1:], subs_stack, depth)
        return False

    if is_smaller(q):
        if term_to_string(q.arg[0], True) < term_to_string(q.arg[1], True):
            return (yield from backchain_ask(kb, goal[1:], subs_stack, depth))
        return True

    if is_conjuction(q):
        return (yield from backchain_ask(kb, q.arg + goal[1:], subs_stack, depth))

    if is_disjuction(q):
        for term in q.arg:
            if not (yield from backchain_ask(kb, [term] + goal[1:], subs_stack, depth)):
                return False
        return True

    if is_equal(q):
        return (yield from matching(q.arg[0], q.arg[1], [], kb, goal[1:], subs_stack, depth, False))

    #must be rule
    for p in kb:
        if aborted:
            return False
        if not (yield from matching(p.arg[0], q, [p.arg[1]], kb, goal[1:], subs_stack, depth, True)):
            return False

    return True

def inference(kb, goal):
    #backward chaining
    global aborted
    aborted = False
    goal = sas_term(goal, 0, {})

    for subs_stack in backchain_ask(kb, [goal],[], 1):
        yield filter_subs(trace_subs(subs_stack))

    if aborted:
        aborted = False
        raise Exception("aborted")
