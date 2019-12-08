from collections import namedtuple

# Structure of a term
# <term> : <term>(list of <term>)
# ["string",["string", "string", "string"]]

Term = namedtuple('Term', 'name arg')

unique_id = 0

# Naming convention
#   Variable: Always start with '/' and arg list is empty
#   '_' variable: '/_' + unique_id, always increase after using the id
#   Standardized variable: To reuse the rule we have to std variable, so that they won't overlap
#       std var name is '//' + <depth> + '/' + real name
#   Constant (literal): Don't contain '/' in the name

# Parser always have the input (except parse_list)
#   s: the string need to be parse
#   start: the starting position
# Parser should always remove trailing space after parsing (or guarantee that it is not space)
# s[start] can be space (except for parse name)

# Parser always return
#   return (pos of the stop token, <term>/None)
# The return position should not be a space character

# Currently parsing is having the following chain (or cycle?)
#   0. Parse knowledge base: Contain many terms, each term is a rule
#   1. Parse rule: <term> :- <list of term>. or <term>. Each term will be parse by parse conjunction
#   2. Parse disjuction <term1>; <term2>;... will be parse to ';'(<list of term>) 
#       terms will be parsed by parse conjunction
#       if The list of term has only one term. Then that term will be return instead
#       if the list is empty then None is returned
#   3. Parse conjunction: similar to parse disjunction but terms are split by ','
#       and terms are parsed by parse operators
#   4. Parse operators: tries to parse term in these structures (in order)
#          <term1>=None <unary op> <term2>
#           <term1> <binary_op> <term2>
#       Term1 is parsed by parse term, and term2 is parse by parse opterators again
#       This will support \+ a = b or \+ \+ a
#   5. Parse term: tries to parse term with canonical form like xyz(abc,hihi(stuff))
#       If the first character is started with '(', it means this term is enclosed in a bracket, 
#           then call parse bracket to parse this term
#       First parse name
#       If there is a bracket, then parse the list inside the bracket by parse term
#   6. Parse bracket:
#       Check for the closing bracket
#       Restart the parse chain by parsing the term by parse disjunction



# Normally, name must start with an alphabet character
# After the first character, it can contains alphabet, digit, or '_'
# For constant, other character (except '/') is permitted when put inside the quote '...'
# Special name like '!', '_' needs to be handle
# Automatically add '/' to variable name
# Assume that s[start] is not space
# Also skip comments % and /* */
def skip_space(s, start):
    comments = None
    while start < len(s):  
        if comments == '%' and s[start] == '\n':
            comments = None
        elif comments == '/*' and s[start:start+2] == '*/':
            comments = None
            start += 1
        elif comments is None:
            if s[start] == '%':
                comments = '%'
            elif s[start:start + 2] == '/*':
                comments = '/*'
            elif not s[start].isspace():
                break

        start += 1
    return start

def _parse_name(s, start):
    global unique_id

    # Check for safty
    i = start
    if i >= len(s):
        return i, ''

    name = ''

    # Check special name
    if s[i] == '!':
        name = '!'
        i += 1
    elif s[i] == '_':
        name = '/_' + str(unique_id)
        unique_id += 1
        i += 1
    else:
        # Check if the name is in quote
        if s[i] == '\'':
            i += 1

            # Find the closing quote
            j = s.find('\'', i)
            if j < 0:
                raise Exception(f"{i+1}: Closing for \"'\" at {i+1} not found")

            # It should not contain '/'
            t = s.find('/', i, j)
            if t >= 0:
                raise Exception(f"{t+ 1}: variable name cannot contain '/'")
            
            name = s[i:j]
            i = j + 1
        else:
            # Check if the first character of the name is alphabetical
            if not s[i].isalpha():
                return i, ''

            # Finding the valid characters
            j = i
            while j < len(s) and (s[j].isalnum() or s[j] == '_'):
                j += 1

            name = s[i:j]
            
            # If it is a variable add '/'
            if name[0].isupper():
                name = '/' + name

            i = j
        
    # Remove the trailing space after the name
    return skip_space(s, i), name

# parse_list will not return a term like other parser
# parse_list will return a list of term that is seperated by the delim
# each term will be parsed by the parser that is in the function argument
# If there is no term it will return []
# Will remove trailing space
def parse_list(s, delim, parser, start):
    j = start

    lterm = []

    is_none = False

    while (j < len(s)):
        j, term = parser(s, j)
        
        # Beware when the parser return None, if only one None term is okay
        if term is None:
            is_none = True
        
        lterm.append(term)

        # check for the delim
        if j >= len(s) or s[j] != delim:
            break

        j += 1
    
    #It is not permitted to have both a None term and other stuff like in abc(,xyz) or abc(,)
    if is_none:
        if len(lterm) > 1:
            raise Exception(f"{j + 1}: Cannot have an empty term in the list")
        else:
            return j, []

    # s[j] is guaranteed not to be a space character since the parser will return non-space pos 
    return j, lterm

# Parsing stuff in bracket
# Restart the parse chain
def parse_bracket(s, start):
    assert(s[start] == '(')
    
    i, term = parse_disjunction(s, start + 1)

    # Check for the closing bracket
    if i >= len(s) or s[i] != ')':
        raise Exception(f"{i + 1}: Expected bracket close for the bracket open at {start + 1}")
    
    return skip_space(s, i + 1), term

# Parse term
def parse_term(s, start):
    # Remove starting space
    start = skip_space(s, start)

    # If it start with a bracket then call parse bracket
    if s[start] == '(':
        return parse_bracket(s, start)

    # Parse name
    i, name = _parse_name(s, start)

    if not name:
        return i, None

    # If found '(', it means there is a argument list
    if i >= len(s) or s[i] != '(':
        return i, Term(name = name, arg = [])

    j, arg = parse_list(s, ',', parse_term, i + 1)

    # If the name is a variable then it cannot have arguments
    if name[0] == '/' and len(arg) > 0:
        raise Exception(f"{i + 1}: Variable can't have arguments")

    if j >= len(s) or s[j] != ')':
        raise Exception(f"{j + 1}: Expected bracket close for the bracket open at {i + 1}")
    
    # Skip the ')' and then find the next non space
    return skip_space(s, j + 1), Term(name = name, arg = arg)

# Parse operator
def parse_op(s, start):
    start, term1 = parse_term(s, start)

    Operator = namedtuple('Operator', 'name ary builder')
    ops = [ Operator('\\+', 1, lambda x , y : Term('\\+', [y])),
            Operator('==', 2, lambda x , y : Term('==', [x,y])),
            Operator('\\==', 2, lambda x , y : Term('\\+', [Term('==', [x,y])])),

            Operator('=', 2, lambda x , y : Term('=', [x,y])),
            Operator('\\=', 2, lambda x , y : Term('\\+', [Term('=', [x,y])])),

            Operator('@<', 2, lambda x , y : Term('@<', [x,y])),
            Operator('@>', 2, lambda x , y : Term('@<', [y,x]))
        ]

    #Find the matching operator
    builder = None
    for op in ops:
        if (term1 is not None or op.ary == 1) and s[start:start + len(op.name)] == op.name:
            builder = op.builder
            break

    if builder is None:
        return start, term1

    start += len(op.name)
    
    # Parse the second term
    start, term2 = parse_op(s, start)

    # Not support postfix operators (yet)
    if term2 is None:
        raise Exception (f"{start + 1}: Expected a term here")

    return start, builder(term1, term2)

# Pase conjunction
def parse_conjunction(s, start):
    n, arg = parse_list(s, ',', parse_op, start)
    
    if len(arg) == 0:
        return n, None
    elif len(arg) == 1:
        return n, arg[0]
    else:
        return n, Term(',', arg)

# Parse disjunction
# Just apply the parse list and handle cases with no or only one term
def parse_disjunction(s, start):
    n, arg = parse_list(s, ';', parse_conjunction, start)
    
    if len(arg) == 0:
        return n, None
    elif len(arg) == 1:
        return n, arg[0]
    else:
        return n, Term(';', arg)


# Parse rule
def parse_rule(s, start):
    # rule: <imp term> :- <goal term>
    # Parse the implication term of the rule
    n, imp = parse_term(s, start)

    if imp is None:
        raise Exception(f"{n + 1}: Expected a term for rule")

    # check if there is :- if not then parse as <imp term> :- true
    if n < len(s) and s[n] != '.':
        if s[n:n + 2] != ':-':
            raise Exception(f"{n + 1} Expected '.' or ':-'")
        n, pcnd = parse_disjunction(s, n + 2)
    else:
        pcnd = Term(name = 'true', arg = []) #no pre condition

    if n >= len(s) or s[n] != '.':
        raise Exception(f"{n + 1} Expected '.'")

    return skip_space(s, n + 1), Term(name = ":-", arg = [imp, pcnd])

# Parse knowledge base
# Knowledge base is just a list of rule
def parse_kb(s):
    kb = []

    start = 0
    while start < len(s):
        start, sen = parse_rule(s, start)
        if sen is not None:
            kb.append(sen)

    return kb

# Parse goal, goal is a term (not containing rules)
def parse_goal(s):
    n, lterm = parse_disjunction(s, 0)
    if n < len(s) and s[n] != '.':
        raise Exception(f"{n + 1}: Unexpected end token {s[n]}")

    return lterm

def load_kb(file_name):
    with open(file_name, 'r') as file:
        kb = parse_kb(file.read())
    return kb