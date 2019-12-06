from collections import namedtuple

#structure of a sentence
# <sentence> : [<term>, [list of <term>]]
# <term> : <term>(list of <term>)
# ["string",["string", "string", "string"]]

#return (pos of the end tok, <term>)

Term = namedtuple('Term', 'name arg')

unique_id = 0

#if literal = False then name cannot be upper case
def parse_name(s, start, end):
    global unique_id

    i = start
    while i < end and s[i].isspace():
        i += 1

    if i == end:
        return i, ''

    name = ''
    if s[i] == '!':
        #cut
        name = '!'
        i += 1
    elif s[i] == '_':
        name = '/_' + str(unique_id)
        unique_id += 1
        i += 1
    else:
        if s[i] == '\'':
            i += 1
            j = s.find('\'', i, end)
            if j < 0:
                raise Exception(f"{end + 1}: not closing \"'\" at {i+1}")

            t = s.find('/', i, j)
            if t >= 0:
                raise Exception(f"{t+ 1}: variable name cannot contain '/'")
            
            name = s[i:j]
            i = j + 1
        else:
            if not s[i].isalpha():
                return i, ''

            j = i
            while j < end and (s[j].isalnum() or s[j] == '_'):
                j += 1

            name = s[i:j]
            if name[0].isupper():
                name = '/' + name

            i = j
        
    while i < end and s[i].isspace():
        i += 1

    return i, name

def parse_list(s, delim, parser, start, end):
    j = start

    lterm = []

    is_none = False

    while (j < end):
        j, term = parser(s, j, end)
        
        if term is None:
            is_none = True
        
        lterm.append(term)

        if j == end or s[j] != delim:
            break

        j += 1
    
    if is_none:
        if len(lterm) > 1:
            raise Exception(f"{j + 1}: Cannot have an empty term in the list")
        else:
            return j, []

    return j, lterm

def parse_bracket(s, start, end):
    assert(s[start] == '(')
    
    i, term = parse_conjunction(s, start + 1, end)

    if i == end or s[i] != ')':
        raise Exception(f"{i + 1}: Expected bracket close for the bracket open at {start + 1}")

    return i + 1, term

def parse_term(s, start, end):
    while start < end and s[start].isspace():
        start += 1
    
    if s[start] == '(':
        return parse_bracket(s, start, end)

    i, name = parse_name(s, start, end)

    if not name:
        return i, None

    if i == end or s[i] != '(':
        return i, Term(name = name, arg = [])
    
    #s[i]='(' => it cannot be a variable
    if name[0] == '/':
        raise Exception(f"{i + 1}: Variable can't have arguments")

    j, arg = parse_list(s, ',', parse_term, i + 1, end)    

    if j == end or s[j] != ')':
        raise Exception(f"{j + 1}: Expected bracket close for the bracket open at {i + 1}")
            
    j += 1
    while j < end and s[j].isspace():
        j += 1
    
    return j, Term(name = name, arg = arg)

def parse_2ary_op(s, start, end):
    start, term1 = parse_term(s, start, end)

    builder = None

    if term1 is None:
        #one ary op
        if start + 1 < end and s[start:start + 2] == '\\+':
            builder = lambda x , y : Term('\\+', [y])
            start += 2
    else:
        if start + 1 < end and s[start:start + 2] == '\\=':
            builder = lambda x , y : Term('\\+', [Term('=', [x,y])])
            start += 2
        elif start < end and s[start] == '=':
            builder = lambda x , y : Term('=', [x,y])
            start += 1

    if builder is None:
        return start, term1

    start, term2 = parse_2ary_op(s, start, end)

    if term2 is None:
        raise Exception (f"{start + 1}: Expected a term here")

    return start, builder(term1, term2)

def parse_disjunction(s, start, end):
    n, arg = parse_list(s, ';', parse_2ary_op, start, end)
    
    if len(arg) == 0:
        return n, None
    elif len(arg) == 1:
        return n, arg[0]
    else:
        return n, Term(';', arg)


def parse_conjunction(s, start, end):
    n, arg = parse_list(s, ',', parse_disjunction, start, end)
    
    if len(arg) == 0:
        return n, None
    elif len(arg) == 1:
        return n, arg[0]
    else:
        return n, Term(',', arg)

def parse_rule(s, start, end):
    n, imp = parse_term(s, start, end)

    if imp is None:
        raise Exception(f"{n + 1}: Expected a term for rule")

    if n < end and s[n] != '.':
        if n + 1 >= end or s[n:n + 2] != ':-':
            raise Exception(f"{n + 1} Expected '.' or ':-'")
        n, pcnd = parse_conjunction(s, n + 2, end)
    else:
        pcnd = Term(name = 'true', arg = []) #no pre condition

    if n == end or s[n] != '.':
        raise Exception(f"{n + 1} Expected '.'")
    
    n += 1

    return n, Term(name = ":-", arg = [imp, pcnd])

def parse_kb(s):
    kb = []

    start = 0
    while start < len(s):

        start, sen = parse_rule(s, start, len(s))
        if sen is not None:
            kb.append(sen)
    
        while start < len(s) and s[start].isspace():
            start += 1

    return kb

def parse_goal(s):
    n, lterm = parse_conjunction(s, 0, len(s))
    if n != len(s) and s[n] != '.':
        raise Exception(f"{n + 1}: Unexpected end token {s[n]}")

    return lterm

def load_kb(file_name):
    with open(file_name, 'r') as file:
        kb = parse_kb(file.read())
    return kb

if __name__ == "__main__":
    load_kb("test_parse")