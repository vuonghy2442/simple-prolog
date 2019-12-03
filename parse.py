from collections import namedtuple

#structure of a sentence
# <sentence> : [<term>, [list of <term>]]
# <term> : <term>(list of <term>)
# ["string",["string", "string", "string"]]

#return (pos of the end tok, <term>)

Term = namedtuple('Term', 'name arg')
Sentence = namedtuple('Sentence', 'imp pcnd')

def parse_name(s, start, end):
    i = start
    while i < end and s[i].isspace():
        i += 1

    if i == end:
        raise Exception(f"{i + 1}: Name should not be empty")

    name = ''

    if not s[i].isalpha():
        raise Exception(f"{i + 1}: Name should start with a english character not '{s[i]}'")

    while i < end and s[i].isalnum():
        name += s[i]
        i += 1
    
    while i < end and s[i].isspace():
        i += 1

    if i != end:
        raise Exception(f"{i + 1}: Unexpected character '{s[i]}' in name")

    return name

def parse_list_term(s, start, end):
    j = start

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
        if i == end or s[i] == ',' or s[i] == '(' or s[i] == ')':
            name = parse_name(s, start, i)

            if i == end or s[i] != '(':
                arg = [] #no args
                n = i
                break

            j, arg = parse_list_term(s, i + 1, end)
            if j == end or s[j] != ')':
                raise Exception(f"{j + 1}: Expected bracket close for the bracket open at {i + 1}")
            
            j += 1
            while j < end and s[j] != ',' and s[j] != ')':
                if not s[j].isspace():
                    raise Exception(f"{j + 1}: Unexpected character '{s[j]}' (expected ',' or ')')")
                j += 1

            n = j
            break
    
    return n, Term(name = name, arg = arg)


def parse_goal(s, start = 0, end = -1):
    if end == -1:
        end = len(s)

    n, pcnd = parse_list_term(s, start, end)

    if n != end:
        raise Exception(f"{n + 1}: Unexpected stop token '{s[n]}' in pre-condition term")

    return pcnd

def parse_sentence(s, start, end):
    pos = s.find(":-", start, end)

    if pos < 0:
        pos = len(s)

    n, imp = parse_term(s, start, pos)

    if n != pos:
        raise Exception(f"{n + 1}: Unexpected stop token '{s[n]}' in implication term")

    if pos == len(s):
        pcnd = [] #no pre condition
    else:
        pcnd = parse_goal(s, pos + 2, end)

    return Sentence(imp = imp, pcnd = pcnd)

def load_kb(file):
    f = open(file)

    kb = []

    for i, l in enumerate(f):
        try:
            kb.append(parse_sentence(l, 0, len(l)))
        except Exception as e:
            print(f"Error at line {i + 1}, col {str(e)}")

    f.close()

    return kb

if __name__ == "__main__":
    load_kb("test_parse")