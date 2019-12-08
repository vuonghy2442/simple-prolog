import parse
from collections import namedtuple

# Whether the task is aborted
aborted = False

# Giving an interface to set abort
def abort_inference():
    global aborted
    aborted = True

# Check if a term is a variable
# Call is quite expensive, so when the task is critical, tries to use inline check
def is_var(term):
    return term.name[0] == '/'

# Return standardized name, should only call when s is a non standardized name
def stand_name(s, depth):
    return "//" + str(depth) + s

# Substitute and standardize (sas)
# Assume that the subs is already standardized
def sas_term(term, depth, subs):
    if term.name[0] == '/': #is_var(term) but inline
        # if the variable is not standarized then do it
        if term.name[1] != '/':
            term = parse.Term(name = stand_name(term.name, depth), arg = [])

        # check if it is in the substituion dict
        if term.name in subs:
            return subs[term.name]
        else:
            return term
    else:
        # If it is a predicate, then recursively do sas for its arguments
        new_arg = [sas_term(x, depth, subs) for x in  term.arg]
        return parse.Term(name = term.name, arg = new_arg)

# Do sas for a list of terms
def sas_lterm(lterm, depth, subs):
    return [sas_term(x, depth, subs) for x in  lterm]

# t1, t2 is 2 terms
# Do simple unify that t1 = t2
# This is not guarantee to return a non referencing substitution dict
# This function is called a lot
# Return true iif unifiable
def simple_unify(t1, t2, subs):
    # Inline check that if both is not variable
    if t1.name[0] != '/' and t2.name[0] != '/':
        if t1.name != t2.name or len(t1.arg) != len(t2.arg):
            # If they are not compatible then return false
            return False
        else:
            # If they are compatible then tries to unify its arguments
            return all(simple_unify(x, y, subs) for x, y in zip(t1.arg, t2.arg))
                
    elif t1.name == '/' and t2.name == '/':
        # Both term are variable
        # if X = X then ignore it
        if t1.name == t2.name:
            return True

    else:
        # If both term is the same variable e.g. X=X then it's unifiable
        if t1.name == t2.name:
            return True

        #if t2 is a variable then switch it with t1
        # or if both are variables then switch the lexicographical smaller one first
        # This and the check X = X are needed to prevent infinite loop in
        if t1.name[0] !='/' or (t2.name[0] == '/' and t2.name < t1.name):
            t1, t2 = t2, t1

        # Now t1 must be a variable, we have the subsituion t1 = t2
        if t1.name in subs:
            # If t1 is already in the dict, we cannot add it to the dict again
            # We tries to unify 2 substituion t1 = subs[t1], and t1 = t2
            if not simple_unify(subs[t1.name], t2, subs):
                return False
        else:
            # Else just add to the substituion dict
            subs[t1.name] = t2

    return True

# This function will tries to remove referencing in the simply_unify result
# It is also tries to standardize the subtituion dict when depth >= 0
def remove_ref(subs, depth):
    # d is the non-standardized/dereferenced substituion dict
    # done is standardized and non-selfreferencing
    # stack is a set that stores the parent terms
    def remove_ref_term(term, depth, d, done, stack):
        if is_var(term):
            # Save the old term to search in the non-standardized subs dict d
            old_term = term

            # Standardizing name
            if depth >= 0 and term.name[1] != '/':
                term =  parse.Term(name = stand_name(term.name, depth), arg = [])

            if term.name in done:
                # if the variable is in done, no need to do anything further
                return done[term.name]
            elif term.name in stack:
                # Cyclic term like X = f(X) will be kept not expanding forever
                return term
            elif old_term.name in d:
                # if the variable is in d
                new_term = d.pop(old_term.name)

                # If the new term is a variable then no need to add to stack because they can self reference
                if not is_var(new_term):
                    stack.add(term.name)

                # tries to remove_ref it self
                new_term = remove_ref_term(new_term, depth, d, done, stack)

                # No need to remove from stack because tis term is in done now
                # the new term is standardized
                done[term.name] = new_term
                return new_term
            else:
                #already standardized and not found in substitution dict
                return term
        else:
            # if it is a predicate, tries to remove refs its arguments, if any of its arguments fails, the process fails
            new_term = parse.Term(term.name, [ None ] * len(term.arg))
            for i in range(len(term.arg)):
                new_term.arg[i] = remove_ref_term(term.arg[i], depth, d, done, stack)
                if new_term.arg[i] is None:
                    return None

            return new_term

    d = dict(subs)
    done = {}

    # while the d dict is still not empty, get one substitution and remove reference from it
    while d:
        next_var = parse.Term(next(iter(d)), [])
        if remove_ref_term(next_var, depth, d, done, set()) is None:
            return None
    
    return done

def unify(eq1, eq2, depth):
    new_subs = dict()
    if not simple_unify(eq1, eq2, new_subs):
        return None

    return remove_ref(new_subs, depth)

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

def lterm_to_string(lterm, full):
    return ','.join([term_to_string(x, full) for x in lterm])

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
    return ', '.join(s)

def is_true(term):
    return len(term.arg) == 0 and term.name == "true"

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

def is_same(term):
    return len(term.arg) == 2 and term.name == "=="

def is_conjuction(term):
    return term.name == ","

def is_disjuction(term):
    return term.name == ";"

def is_dif(term):
    return len(term.arg) == 2 and term.name == "dif"

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
        return

    new_goal = sas_lterm(cond + goal, depth, new_subs)

    subs_stack.append(new_subs)
    yield from backchain_ask(kb, new_goal, subs_stack, depth + 1)
    subs_stack.pop()

def pre_eval(term):
    #do pre evaluation
    if is_dif(term):
        res = unify(term.arg[0], term.arg[1], -1)
        if res is None:
            return parse.Term('true', []) #if not unifable then return true
        elif len(res) == 0:
            return parse.Term('fail', []) #nope
        else:
            #update the term
            left = []
            right = []
            for var, t in res.items():
                left.append(parse.Term(var, []))
                right.append(t)

            if len(left) > 1:
                term.arg[0] = parse.Term('f', left)
                term.arg[1] = parse.Term('f', right)
            else:
                term.arg[0], term.arg[1] = left[0], right[0]
            return None  #not evaluable yet
    
    return term


#return found, continue
def backchain_ask(kb, goal, subs_stack, depth):
    global aborted
    if aborted:
        aborted = False
        raise Exception("aborted")

    q = None

    for i in range(len(goal)):
        q = pre_eval(goal[i])
        if q is not None:
            del goal[i]
            break

    if q is None:
        yield (goal, subs_stack)
    elif is_true(q):
        yield from backchain_ask(kb, goal, subs_stack, depth)
    elif is_fail(q):
        pass
    elif is_not(q):
        gen = backchain_ask(kb, q.arg, [], depth)
        try:
            next(gen)
        except StopIteration:
            yield from backchain_ask(kb, goal, subs_stack, depth)
    elif is_smaller(q):
        if term_to_string(q.arg[0], True) < term_to_string(q.arg[1], True):
            yield from backchain_ask(kb, goal, subs_stack, depth)
    elif is_conjuction(q):
        yield from backchain_ask(kb, q.arg + goal, subs_stack, depth)
    elif is_disjuction(q):
        for term in q.arg:
            yield from backchain_ask(kb, [term] + goal, subs_stack, depth)
    elif is_equal(q):
        yield from matching(q.arg[0], q.arg[1], [], kb, goal, subs_stack, depth, False)
    elif is_same(q):
        if term_to_string(q.arg[0], True) == term_to_string(q.arg[1], True):
            yield from backchain_ask(kb, goal, subs_stack, depth)
    else:
        #must be rule
        for p in kb:    
            if aborted:
                aborted = False
                raise Exception("aborted")

            yield from matching(p.arg[0], q, [p.arg[1]], kb, goal, subs_stack, depth, True)

def inference(kb, goal):
    #backward chaining
    global aborted
    aborted = False
    goal = sas_term(goal, 0, {})

    for r_goal, subs_stack in backchain_ask(kb, [goal],[], 1):
        yield (r_goal, filter_subs(trace_subs(subs_stack)))


# result return by inference
def result_to_string(res, full = False):
    r_goal, subs = res
    subs_str = subs_to_string(subs, full)
    r_goal_str = lterm_to_string(r_goal, full)

    if r_goal and subs:
        return subs_str + ', ' + r_goal_str
    elif subs:
        return subs_str
    elif r_goal:
        return r_goal_str
    else:
        return 'yes'
