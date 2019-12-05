import main
import parse
import interpreter

kb1 = None
kb2 = None
kb3 = None

def compare(truth, gen):
    sol = [interpreter.subs_to_string(subs, False) for subs in gen]
    truth.sort()
    sol.sort()

    assert(len(truth) == len(sol))
    for a, b in zip(truth, sol):
        assert(a == b)

def test_load():
    global kb1, kb2, kb3
    kb1 = parse.load_kb("./test_sum")
    kb2 = parse.load_kb("./test_puzzle")
    kb3 = parse.load_kb("./test_infer")

def test1_1():
    global kb1
    gen = interpreter.inference(kb1, parse.parse_goal("sum(zero,X,X)"))
    truth =  ['X = _']
    compare(truth, gen)

def test1_2():
    global kb1
    gen = interpreter.inference(kb1, parse.parse_goal("prod(X,Y,s(s(s(s(s(s(zero)))))))"))
    truth =  ['X = s(zero), Y = s(s(s(s(s(s(zero))))))',
              'X = s(s(zero)), Y = s(s(s(zero)))',
              'X = s(s(s(zero))), Y = s(s(zero))',
              'X = s(s(s(s(s(s(zero)))))), Y = s(zero)'
            ]
    compare(truth, gen)

def test1_3():
    global kb1
    gen = interpreter.inference(kb1, parse.parse_goal("prod(X,Y,zero)"))
    truth =  ['X = zero, Y = _', 'X = s(_), Y = zero']
    compare(truth, gen)

def test1_4():
    global kb1
    gen = interpreter.inference(kb1, parse.parse_goal("prime(zero)"))
    truth =  []
    compare(truth, gen)

def test1_5():
    global kb1
    gen = interpreter.inference(kb1, parse.parse_goal("prime(s(s(s(zero))))"))
    truth =  ['yes']
    compare(truth, gen)

def test1_6():
    global kb1
    gen = interpreter.inference(kb1, parse.parse_goal("prime(s(s(s(s(s(s(zero)))))))"))
    truth =  []
    compare(truth, gen)

def test2_1():
    global kb2
    gen = interpreter.inference(kb2, parse.parse_goal("puzzle(Houses)"))
    truth =  ['Houses = list(house(yellow,norwegian,water_,dunhill,cat),'
                'house(blue,danish,tea,blend,horse),'
                'house(red,british,milk,pall_mall,bird),'
                'house(green,german,coffee,prince,_),'
                'house(white,swedish,beer,bluemaster,dog))'
            ]
    compare(truth, gen)

def test3_1():
    global kb3
    gen = interpreter.inference(kb3, parse.parse_goal("neg(love(a,b))"))
    truth =  []
    compare(truth, gen)

def test3_2():
    global kb3
    gen = interpreter.inference(kb3, parse.parse_goal("neg(love(a,c))"))
    truth =  ["yes"]
    compare(truth, gen)

def test3_3():
    global kb3
    gen = interpreter.inference(kb3, parse.parse_goal("neg(love(a,b)),fail"))
    truth =  []
    compare(truth, gen)