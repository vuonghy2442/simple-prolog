from collections import namedtuple

#structure of a sentence
# <sentence> : [<term>, [list of <term>]]
# <term> : <term>(list of <term>)
# ["string",["string", "string", "string"]]

#return (pos of the end tok, <term>)

Term = namedtuple('Term', 'name arg')
Sentence = namedtuple('Sentence', 'imp pcnd')

unique_id = 0

#if literal = False then name cannot be upper case
def parse_name(s, start, end, literal):
    global unique_id

    i = start
    while i < end and s[i].isspace():
        i += 1

    if i == end:
        return ''

    name = ''

    if s[i] == '!' and literal:
        #cut
        name = '!'
        i += 1
    elif s[i] == '_' and literal:
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

            if not literal and s[i].isupper():
                raise Exception(f"{i + 1}: Unexpected variable")

            j = i
            while j < end and (s[j].isalnum() or s[j] == '_'):
                j += 1

            name = s[i:j]
            if name[0].isupper():
                name = '/' + name

            i = j
        
    while i < end and s[i].isspace():
        i += 1

    if i != end:
        raise Exception(f"{i + 1}: Unexpected character '{s[i]}' in name")

    return name

def parse_list_term(s, start, end):
    j = start

    n = end

    lterm = []
    while (j < end):
        j, term = parse_term(s, j, end)
        lterm.append(term)

        if j == end or s[j] != ',':
            n = j
            break
        
        j += 1
    
    return n, lterm

def parse_term(s, start, end):
    for i in range(start, end + 1):
        if i == end or s[i] == ':' or s[i] == ',' or s[i] == '.' or s[i] == '(' or s[i] == ')':
            name = parse_name(s, start, i, i == end or s[i] != '(')

            if name == '':
                raise Exception(f"{i + 1}: Name should not be empty")

            if i == end or s[i] != '(':
                arg = [] #no args
                n = i
                break

            j, arg = parse_list_term(s, i + 1, end)
            if j == end or s[j] != ')':
                raise Exception(f"{j + 1}: Expected bracket close for the bracket open at {i + 1}")
            
            j += 1
            while j < end and s[j].isspace():
                j += 1

            n = j
            break
    
    return n, Term(name = name, arg = arg)

def parse_sentence(s, start, end):
    n, imp = parse_term(s, start, end)

    if n < end and s[n] != '.':
        if n + 1 >= end or s[n:n + 2] != ':-':
            raise Exception(f"{n + 1} Expected '.' or ':-'")
        n, pcnd = parse_list_term(s, n + 2, end)
    else:
        pcnd = [] #no pre condition

    if n == end or s[n] != '.':
        raise Exception(f"{n + 1} Expected '.'")
    
    n += 1

    return n, Sentence(imp = imp, pcnd = pcnd)

def parse_kb(s):
    kb = []

    start = 0
    while start < len(s):
        start, sen = parse_sentence(s, start, len(s))
        if sen is not None:
            kb.append(sen)
    
    return kb

def load_kb(file_name):
    with open(file_name, 'r') as file:
        kb = parse_kb(file.read().strip())
    return kb

if __name__ == "__main__":
    load_kb("test_parse")