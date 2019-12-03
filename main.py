import parse
from collections import namedtuple

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

def compose(subs, rule):
    for name, term in rule.items():
        if name in subs:
            raise Exception("Compose error")
            
        term = substitute(term, subs)
        subs[name] = term #add to subs

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
def unify(eq1, eq2):
    assert(len(eq1) == len(eq2))

    if len(eq1) == 0:
        return []

    change = True
    done_var = set()

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

    #convert to subsitution
    subs = {}
    for x, y in zip(eq1, eq2):
        assert(is_var(x))
        subs[x.name] = y

    return subs

def stand_term(term, idx):
    if is_var(term):
        return parse.Term(name = term.name + "/" + str(idx), arg = term.arg)
    else:
        return parse.Term(name = term.name, arg = [stand_term(x, idx) for x in term.arg])

#change variable name so that they won't overlap
def standardize(sen, idx):
    return parse.Sentence(imp = stand_term(sen.imp, idx), pcnd =  [stand_term(x, idx) for x in sen.pcnd])

def backchain_ask(kb, goal, subs, depth):
    if len(goal) == 0:
        print(subs)
        return input("Continue (y/n)? ") == 'y'
    
    q = substitute(goal[0], subs)

    for p in kb:
        p = standardize(p, depth)
        subs2 = unify([p.imp], [q])
        if subs2 is not None:
            new_goal = p.pcnd + goal[1:]
            subs2.update(subs)
            if not backchain_ask(kb, new_goal, subs2, depth + 1):
                return False

    return True

kb = parse.load_kb("test_infer")
backchain_ask(kb, parse.parse_goal(input("Goals: ")), {}, 0)