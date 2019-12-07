import parse
import interpreter

def compare(truth, gen, num = -1):
    if num == -1:
        sol = [interpreter.subs_to_string(subs, False) for subs in gen]
    else:
        sol = [interpreter.subs_to_string(next(gen), False) for i in range(num)]

    truth.sort()
    sol.sort()

    assert(len(truth) == len(sol))
    for a, b in zip(truth, sol):
        assert(a == b)

def check_term_valid(term):
    assert(term is not None)
    assert(term.name[0] != '/' or len(term.arg) == 0)
    for x in term.arg:
        check_term_valid(x)

def compare_parse(rule, truth_str):
    try:
        lterm = parse.parse_kb(rule)
        rule = interpreter.lterm_to_string(lterm,False)
    except Exception as e:
        if truth_str is not None:
            raise e
    else:
        for term in lterm:
            check_term_valid(term)

        assert(rule == truth_str)

def test_parse():
    compare_parse("  hihi.", "':-'(hihi,true)")
    compare_parse("hihi :-   xyz  .  ", "':-'(hihi,xyz)")
    compare_parse("hihi :- 'xyz'.", "':-'(hihi,xyz)")
    compare_parse("hihi :- 'leu leu'.", "':-'(hihi,'leu leu')")
    compare_parse("hihi :- Xyz().", "':-'(hihi,Xyz)")
    compare_parse("hihi :- xyz().", "':-'(hihi,xyz)")
    compare_parse("hihi :- xyz,abc.", "':-'(hihi,','(xyz,abc))")
    compare_parse("hihi :- xyz,abc,'ghi k'.", "':-'(hihi,','(xyz,abc,'ghi k'))")
    compare_parse("hihi :- xyz,abc;'leu x' ='ley','ghi k'.", "':-'(hihi,','(xyz,';'(abc,'='('leu x',ley)),'ghi k'))")
    compare_parse("hihi :- xyz( uv, s(ab)).", "':-'(hihi,xyz(uv,s(ab)))")
    compare_parse("hihi,tv :- xyz( uv, s(ab)).", None)
    compare_parse("Hihi.", "':-'(Hihi,true)")
    compare_parse("hihi(X,Y) :- \\+ X = Y.", "':-'(hihi(X,Y),'\\+'('='(X,Y)))")
    compare_parse("leu(first).", "':-'(leu(first),true)")
    compare_parse("check    (   leu   (fi_rst), \n xyz  ).", "':-'(check(leu(fi_rst),xyz),true)")
    compare_parse("leu :- :-.", None)
    compare_parse("test :=.", None)    
    compare_parse(" :- hihi.", None)    
    compare_parse("5hi.", None)    
    compare_parse("'5leu'.", "':-'('5leu',true)") 
    compare_parse("'sdf/'.", None)
    compare_parse("test, meo.", None)
    compare_parse("test(abc :- xyz.", None)
    compare_parse("test(abc) xyz.", None)
    compare_parse("test(abc) :- xyz).", None)
    compare_parse("a(X,Y):-b(X),(c(Y);d(Y)).", "':-'(a(X,Y),','(b(X),';'(c(Y),d(Y))))") 



def test_load():
    parse.load_kb("./test_sum")
    parse.load_kb("./test_puzzle")
    parse.load_kb("./test_infer")

def test0_1():
    kb = []
    gen = interpreter.inference(kb, parse.parse_goal("X=X"))
    truth =  ['yes']
    compare(truth, gen)

def test0_2():
    kb = []
    gen = interpreter.inference(kb, parse.parse_goal("X=a"))
    truth =  ['X = a']
    compare(truth, gen)

def test0_3():
    kb = []
    gen = interpreter.inference(kb, parse.parse_goal("a=b"))
    truth =  []
    compare(truth, gen)

def test0_4():
    kb = []
    gen = interpreter.inference(kb, parse.parse_goal("a@<b"))
    truth =  ['yes']
    compare(truth, gen)

def test0_5():
    kb = []
    gen = interpreter.inference(kb, parse.parse_goal("Y@<X"))
    truth =  []
    compare(truth, gen)

def test1_1():
    kb1 = parse.load_kb("./test_sum")
    gen = interpreter.inference(kb1, parse.parse_goal("sum(zero,X,X)"))
    truth =  ['X = _']
    compare(truth, gen)

def test1_2():
    kb1 = parse.load_kb("./test_sum")
    gen = interpreter.inference(kb1, parse.parse_goal("prod(X,Y,s(s(s(s(s(s(zero)))))))"))
    truth =  ['X = s(zero), Y = s(s(s(s(s(s(zero))))))',
              'X = s(s(zero)), Y = s(s(s(zero)))',
              'X = s(s(s(zero))), Y = s(s(zero))',
              'X = s(s(s(s(s(s(zero)))))), Y = s(zero)'
            ]
    compare(truth, gen)

def test1_3():
    kb1 = parse.load_kb("./test_sum")
    gen = interpreter.inference(kb1, parse.parse_goal("prod(X,Y,zero)"))
    truth =  ['X = zero, Y = _', 'X = s(_), Y = zero']
    compare(truth, gen)

def test1_4():
    kb1 = parse.load_kb("./test_sum")
    gen = interpreter.inference(kb1, parse.parse_goal("prime(zero)"))
    truth =  []
    compare(truth, gen)

def test1_5():
    kb1 = parse.load_kb("./test_sum")
    gen = interpreter.inference(kb1, parse.parse_goal("prime(s(s(s(zero))))"))
    truth =  ['yes']
    compare(truth, gen)

def test1_6():
    kb1 = parse.load_kb("./test_sum")
    gen = interpreter.inference(kb1, parse.parse_goal("prime(s(s(s(s(s(s(zero)))))))"))
    truth =  []
    compare(truth, gen)

def test1_7():
    kb1 = parse.load_kb("./test_sum")
    gen = interpreter.inference(kb1, parse.parse_goal("sum(X,zero,X),prime(X)"))
    truth =  ['X = s(s(zero))',
              'X = s(s(s(zero)))',
              'X = s(s(s(s(s(zero)))))',
              'X = s(s(s(s(s(s(s(zero)))))))',
              'X = s(s(s(s(s(s(s(s(s(s(s(zero)))))))))))',
              'X = s(s(s(s(s(s(s(s(s(s(s(s(s(zero)))))))))))))',
            ]
    compare(truth, gen, 6)

def test2_1():
    kb2 = parse.load_kb("./test_puzzle")

    gen = interpreter.inference(kb2, parse.parse_goal("puzzle(Houses)"))
    truth =  ['Houses = list(house(yellow,norwegian,water_,dunhill,cat),'
                'house(blue,danish,tea,blend,horse),'
                'house(red,british,milk,pall_mall,bird),'
                'house(green,german,coffee,prince,_),'
                'house(white,swedish,beer,bluemaster,dog))'
            ]
    compare(truth, gen)

def test3_1():
    kb3 = parse.load_kb("./test_infer")

    gen = interpreter.inference(kb3, parse.parse_goal("neg(love(a,b))"))
    truth =  []
    compare(truth, gen)

def test3_2():
    kb3 = parse.load_kb("./test_infer")

    gen = interpreter.inference(kb3, parse.parse_goal("neg(love(a,c))"))
    truth =  ["yes"]
    compare(truth, gen)

def test3_3():
    kb3 = parse.load_kb("./test_infer")

    gen = interpreter.inference(kb3, parse.parse_goal("neg(love(a,b)),fail"))
    truth =  []
    compare(truth, gen)