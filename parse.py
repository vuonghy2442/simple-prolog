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
                raise Exception(f"{i + 1}: Name should start with a english character not '{s[i]}'")

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

def parse_list(s, delim, start, end):
    j = start

    n = end

    lterm = []
    while (j < end):
        j, term = parse_term(s, j, end)
        lterm.append(term)

        if j == end or s[j] != delim:
            n = j
            break
        
        j += 1
    
    return n, lterm

def parse_conjunction(s, start, end):
    n, arg = parse_list(s, ',', start, end)
    return n, Term(',', arg)

def parse_term(s, start, end):
    i, name = parse_name(s, start, end)

    if not name:
        raise Exception(f"{i + 1}: Name should not be empty")

    if i == end or s[i] != '(':
        return i, Term(name = name, arg = [])
    
    #if it is a variable means s[i]='('
    if name[0] == '/':
        raise Exception(f"{i + 1}: Variable can't have arguments")

    j, arg = parse_list(s, ',', i + 1, end)    

    if j == end or s[j] != ')':
        raise Exception(f"{j + 1}: Expected bracket close for the bracket open at {i + 1}")
            
    j += 1
    while j < end and s[j].isspace():
        j += 1
    
    return j, Term(name = name, arg = arg)

def parse_rule(s, start, end):
    n, imp = parse_term(s, start, end)

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
    
    return kb

def parse_goal(s):
    n, lterm = parse_conjunction(s, 0, len(s))
    if n != len(s) and s[n] != '.':
        raise Exception(f"{n + 1}: Unexpected end token {s[n]}")

    return lterm

def load_kb(file_name):
    with open(file_name, 'r') as file:
        kb = parse_kb(file.read().strip())
    return kb

if __name__ == "__main__":
    load_kb("test_parse")