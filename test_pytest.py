import parse
import interpreter

def compare(truth, gen, num = -1):
    if num == -1:
        sol = [interpreter.result_to_string(res, False) for res in gen]
    else:
        sol = [interpreter.result_to_string(next(gen), False) for i in range(num)]

    truth.sort()
    sol.sort()

    assert(truth == sol)

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
    compare_parse("hihi :- xyz,abc;'leu x' ='ley','ghi k'.", "':-'(hihi,';'(','(xyz,abc),','('='('leu x',ley),'ghi k')))")
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
    compare_parse("a(X,Y):-%comments here\nb(X),(c(Y/*leu % \nleu*/);d(Y)%i adfd dk\n).", "':-'(a(X,Y),','(b(X),';'(c(Y),d(Y))))") 


def query(kb, query, truth, num = -1):
    gen = interpreter.inference(kb, parse.parse_goal(query))
    compare(truth, gen, num)

def test_load():
    parse.load_kb("./test_sum.pl")
    parse.load_kb("./test_puzzle.pl")
    parse.load_kb("./test_infer.pl")

def test0():
    query([], "X=X", ["yes"])
    query([], "X=a", ["X = a"])
    query([], "a=b", [])
    query([], "a@<b", ["yes"])
    query([], "Y @< X", [])
    query([], "Y == X", [])
    query([], "X == X", ["yes"])
    query([], "a \\== X", ["yes"])
    query([], "dif(A, B)", ["dif(A,B)"])
    query([], "dif(A, B),A=a", ["A = a, dif(a,B)"])
    query([], "dif(A, B),A=a,B=a", [])
    query([], "dif(A, B),B = A", [])
    query([], "dif(A, B),A = a, B = b", ["A = a, B = b"])


def test1_1():
    kb1 = parse.load_kb("./test_sum.pl")
    query(kb1, "sum(zero,X,X)", ['X = _'])

def test1_2():
    kb1 = parse.load_kb("./test_sum.pl")
    query(kb1, "prod(X,Y,s(s(s(s(s(s(zero)))))))",
        [   'X = s(zero), Y = s(s(s(s(s(s(zero))))))',
            'X = s(s(zero)), Y = s(s(s(zero)))',
            'X = s(s(s(zero))), Y = s(s(zero))',
            'X = s(s(s(s(s(s(zero)))))), Y = s(zero)'
        ])

def test1_3():
    kb1 = parse.load_kb("./test_sum.pl")
    query(kb1, "prod(X,Y,zero)", ['X = zero, Y = _', 'X = s(_), Y = zero'])

def test1_4():
    kb1 = parse.load_kb("./test_sum.pl")
    query(kb1, "prime(zero)", [])

def test1_5():
    kb1 = parse.load_kb("./test_sum.pl")
    query(kb1, "prime(s(s(s(zero))))", ['yes'])

def test1_6():
    kb1 = parse.load_kb("./test_sum.pl")
    query(kb1, "prod(s(s(zero)),s(s(s(zero))),X), prime(X)", [])
    query(kb1, "prime(s(s(s(s(s(s(zero)))))))", [])

def test1_7():
    kb1 = parse.load_kb("./test_sum.pl")
    query(kb1, "sum(X,zero,X),prime(X)",
        [   'X = s(s(zero))',
            'X = s(s(s(zero)))',
            'X = s(s(s(s(s(zero)))))',
            'X = s(s(s(s(s(s(s(zero)))))))',
            'X = s(s(s(s(s(s(s(s(s(s(s(zero)))))))))))',
            'X = s(s(s(s(s(s(s(s(s(s(s(s(s(zero)))))))))))))',
        ],
        6
    )

def test2_1():
    kb2 = parse.load_kb("./test_puzzle.pl")

    query(kb2, "puzzle(Houses)",
        [   'Houses = list(house(yellow,norwegian,water_,dunhill,cat),'
            'house(blue,danish,tea,blend,horse),'
            'house(red,british,milk,pall_mall,bird),'
            'house(green,german,coffee,prince,_),'
            'house(white,swedish,beer,bluemaster,dog))'
        ])

def test3_1():
    kb3 = parse.load_kb("./test_infer.pl")
    query(kb3, "neg(love(a,b))", [])

def test3_2():
    kb3 = parse.load_kb("./test_infer.pl")
    query(kb3, "neg(love(a,c))", ['yes'])

def test3_3():
    kb3 = parse.load_kb("./test_infer.pl")
    query(kb3, "neg(love(a,c)), fail", [])

def test_ai1():
    kb = parse.load_kb("./AI.pl")
    query(kb, "wife(X,charles)", ['X = camilla_Parker_Bowles'])
    query(kb, "husband(mark_Philips, anne)", [])
    query(kb, "father(philip,anne)", ['yes'])
    query(kb, "mother(X, william)", ['X = diana'])
    query(kb, "child(X,andrew)", ['X = eugenie', 'X = beatrice'])
    query(kb, "son(X,william)", ['X = george', 'X = louis'])
    query(kb, "daughter(X,edward_Earl)", ['X = louise_Windsor'])
    query(kb, "grandparent(X,george)", ['X = diana', 'X = charles'])
    query(kb, "grandmother(diana, george)", ['yes'])
    query(kb, "grandfather(X,peter_Phillips)", ['X = philip'])
    query(kb, "grandson(X,elizabethII)", ['X = william', 'X = harry', 'X = peter_Phillips', 'X = james'])
    query(kb, "grandchild(X,diana)", ['X = george', 'X = charlotte', 'X = louis', 'X = harrison_Mountbatten_Windsor'])
    query(kb, "granddaughter(X,philip)", ['X = eugenie', 'X = beatrice', 'X = zara_Tindall', 'X = louise_Windsor'])
    query(kb, "sibling(eugenie,beatrice)", ['yes'])
    query(kb, "brother(X,harry)", ['X = william'])
    query(kb, "sister(X,peter_Phillips)", ['X = zara_Tindall'])
    query(kb, "uncle(X,zara_Tindall)", ['X = charles','X = andrew', 'X = edward_Earl'])
    query(kb, "aunt(X,james)", ['X = anne'])
    query(kb, "niece(X,edward_Earl)", ['X = eugenie', 'X = beatrice', 'X = zara_Tindall'])
    query(kb, "nephew(X,andrew)", ['X = william', 'X = harry', 'X = peter_Phillips', 'X = james'])
    query(kb, "sibling(X,Y),X@<Y", 
        [   'X = charles, Y = edward_Earl',
            'X = andrew, Y = charles',
            'X = andrew, Y = anne',
            'X = andrew, Y = edward_Earl',
            'X = anne, Y = charles',
            'X = anne, Y = edward_Earl',
            'X = harry, Y = william',
            'X = beatrice, Y = eugenie',
            'X = george, Y = louis',
            'X = charlotte, Y = george',
            'X = charlotte, Y = louis',
            'X = peter_Phillips, Y = zara_Tindall',
            'X = james, Y = louise_Windsor'
        ])    

def test_ai2():
    kb = parse.load_kb("./AI2.pl")
    query(kb, "bird(X)", ['X = eagle', 'X = sparrow'])
    query(kb, "vertebrata(X)", 
        ['X = eagle', 'X = sparrow', 'X = tiger', 
         'X = bear', 'X = frog', 'X = salamander',
         'X = turtle', 'X = crocodile', 'X = gold_fish', 'X = carp'
        ])

    query(kb, "coldBlooded(X)", ['X = frog', 'X = salamander', 'X = turtle', 'X = crocodile', 'X = gold_fish', 'X = carp'])
    query(kb, "hotBlooded(eagle)", ['yes'])
    query(kb, "molluscs(octopus)", ['yes'])
    query(kb, "invertebrates(bear)", [])
    query(kb, "liveOnland(X)", ['X = eagle', 'X = sparrow', 'X = tiger', 'X = bear', 'X = salamander'])
    query(kb, "liveUnderwater(spider)", [])
    query(kb, "plantae(bamboo)", ['yes'])
    query(kb, "gymnosperms(X)", ['X = ginkgophyta', 'X = pine', 'X = cycadophyta'])
    query(kb, "angiosperms(tomato)", ['yes'])
    query(kb, "twoCotyledons(X)", ['X = coconut', 'X = tomato', 'X = rose'])
    query(kb, "kingdom(X)", ['X = animalia', 'X = plantae', 'X = fungi', 'X = protista', 'X = monera'])
    query(kb, "thuocGioi(plantae, vertebrata)", [])
    query(kb, "hon1Bac(animalia, grainy_plantae)", ['yes'])
    query(kb, "cungBac(fungi,X)", ['X = animalia', 'X = plantae', 'X = protista', 'X = monera']) #fungi should not be here
    query(kb, "thuocNganh(vertebrata, reptilia)", ['yes'])
    query(kb, "amphibia(X)", ['X = frog', 'X = salamander'])
    query(kb, "coLongVu(X)", ['X = eagle', 'X = sparrow'])
    query(kb, "breastfeeding(X)", ['X = tiger', 'X = bear'])







    
