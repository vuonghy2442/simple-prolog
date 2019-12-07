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
#   end: the ending position
# Parser always assume that the s[start] is not a space character

# Parser always return
#   return (pos of the stop token, <term>/None)
# The return position should not be a space character

# Currently parsing is having the following chain (or cycle?)
#   1. Parse rule <term> :- <list of term>. or <term>. Each term will be parse by parse conjunction
#   2. Parse conjuction <term1>, <term2>,... will be parse to ','(<list of term>) 
#       terms will be parsed by parse disjunction
#       if The list of term has only one term. Then that term will be return instead
#       if the list is empty then None is returned
#   3. Parse disjuction: similar to parse conjunction but terms are split by ';'
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
#       Restart the parse chain by parsing the term by parse conjunction



# Normally, name must start with an alphabet character
# After the first character, it can contains alphabet, digit, or '_'
# For constant, other character (except '/') is permitted when put inside the quote '...'
# Special name like '!', '_' needs to be handle
# Automatically add '/' to variable name
def parse_name(s, start, end):
    global unique_id

    # Check for safty
    i = start
    if i == end:
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
            j = s.find('\'', i, end)
            if j < 0:
                raise Exception(f"{end + 1}: not closing \"'\" at {i+1}")

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
            while j < end and (s[j].isalnum() or s[j] == '_'):
                j += 1

            name = s[i:j]
            
            # If it is a variable add '/'
            if name[0].isupper():
                name = '/' + name

            i = j
        
    # Remove the trailing space after the name
    while i < end and s[i].isspace():
        i += 1

    return i, name

# parse_list will not return a term like other parser
# parse_list will return a list of term that is seperated by the delim
# each term will be parsed by the parser that is in the function argument
# If there is no term it will return []
def parse_list(s, delim, parser, start, end):
    j = start

    lterm = []

    is_none = False

    while (j < end):
        # Find the first non space before enter parse
        if s[j].isspace():
            j += 1
            continue

        j, term = parser(s, j, end)
        
        # Beware when the parser return None, if only one None term is okay
        if term is None:
            is_none = True
        
        lterm.append(term)

        # check for the delim
        if j == end or s[j] != delim:
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
def parse_bracket(s, start, end):
    assert(s[start] == '(')
    
    i, term = parse_conjunction(s, start + 1, end)

    # Check for the closing bracket
    if i == end or s[i] != ')':
        raise Exception(f"{i + 1}: Expected bracket close for the bracket open at {start + 1}")
    
    i += 1
    
    # Should find the next non-space
    while i < end and s[i].isspace():
        i += 1
    
    return i, term

# Parse term
def parse_term(s, start, end):
    # If it start with a bracket then call parse bracket
    if s[start] == '(':
        return parse_bracket(s, start, end)

    # Parse name
    i, name = parse_name(s, start, end)

    if not name:
        return i, None

    # If found '(', it means there is a argument list
    if i == end or s[i] != '(':
        return i, Term(name = name, arg = [])

    j, arg = parse_list(s, ',', parse_term, i + 1, end)

    # If the name is a variable then it cannot have arguments
    if name[0] == '/' and len(arg) > 0:
        raise Exception(f"{i + 1}: Variable can't have arguments")

    if j == end or s[j] != ')':
        raise Exception(f"{j + 1}: Expected bracket close for the bracket open at {i + 1}")
    
    # Skip the ')' and then find the next non space
    j += 1
    while j < end and s[j].isspace():
        j += 1
    
    return j, Term(name = name, arg = arg)

# Parse operator
def parse_op(s, start, end):
    start, term1 = parse_term(s, start, end)

    builder = None

    if term1 is None:
        # Find if any unary operator matches
        if start + 1 < end and s[start:start + 2] == '\\+':
            builder = lambda x , y : Term('\\+', [y])
            start += 2
    else:
        # Find if any binary operator matches
        if start + 1 < end and s[start:start + 2] == '\\=':
            builder = lambda x , y : Term('\\+', [Term('=', [x,y])])
            start += 2
        elif start + 1 < end and s[start:start + 2] == '@<':
            builder = lambda x , y : Term('@<', [x,y])
            start += 2
        elif start + 1 < end and s[start:start + 2] == '@>':
            builder = lambda x , y : Term('@<', [y,x])
            start += 2
        elif start < end and s[start] == '=':
            builder = lambda x , y : Term('=', [x,y])
            start += 1

    if builder is None:
        return start, term1

    # Find the next non-space character
    while s[start].isspace():
        start += 1

    # Parse the second term
    start, term2 = parse_op(s, start, end)

    # Not support postfix operators (yet)
    if term2 is None:
        raise Exception (f"{start + 1}: Expected a term here")

    return start, builder(term1, term2)

# Parse disjunction
# Just apply the parse list and handle cases with no or only one term
def parse_disjunction(s, start, end):
    n, arg = parse_list(s, ';', parse_op, start, end)
    
    if len(arg) == 0:
        return n, None
    elif len(arg) == 1:
        return n, arg[0]
    else:
        return n, Term(';', arg)

# Pase conjuction
def parse_conjunction(s, start, end):
    n, arg = parse_list(s, ',', parse_disjunction, start, end)
    
    if len(arg) == 0:
        return n, None
    elif len(arg) == 1:
        return n, arg[0]
    else:
        return n, Term(',', arg)

# Parse rule
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

# Parse kb
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