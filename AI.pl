female(elizabethII).
female(diana).
female(camilla_Parker_Bowles).
female(sarah_Ferguson).
female(kate_Middleton).
female(meghan_Markie).
female(eugenie).
female(beatrice).
female(charlotte).
female(anne).
female(sophie_Rhys_Jones).
female(autumn_Phillips).
female(zara_Tindall).
female(louise_Windsor).


male(philip).
male(charles).
male(andrew).
male(william).
male(harry).
male(george).
male(louis).
male(mark_Phillips).
male(timothy_Laurence).
male(edward_Earl).
male(peter_Phillips).
male(mike_Tindall).
male(james).
male(harrison_Mountbatten_Windsor).


married(elizabethII,philip).
married(philip,elizabethII).

married(diana,charles).
married(charles,diana).

married(charles,camilla_Parker_Bowles).
married(camilla_Parker_Bowles,charles).

married(andrew,sarah_Ferguson).
married(sarah_Ferguson,andrew).

married(kate_Middleton,william).
married(william,kate_Middleton).

married(harry,meghan_Markle).
married(meghan_Markle,harry).

married(mark_Phillips,anne).
married(anne,mark_Phillips).

married(anne,timothy_Laurence).
married(timothy_Laurence,anne).

married(edward_Earl,sophie_Rhys_Jones).
married(sophie_Rhys_Jones,edward_Earl).

married(peter_Phillips,autumn_Phillips).
married(autumn_Phillips,peter_Phillips).

married(zara_Tindall,mike_Tindall).
married(mike_Tindall,zara_Tindall).

divorced(diana,charles).
divorced(charles,diana).

divorced(mark_Phillips,anne).
divorced(anne,mark_Phillips).


parent(elizabethII,charles).
parent(elizabethII,andrew).
parent(elizabethII,anne).
parent(elizabethII,edward_Earl).
parent(philip,charles).
parent(philip,andrew).
parent(philip,anne).
parent(philip,edward_Earl).

parent(diana,william).
parent(diana,harry).
parent(charles,william).
parent(charles,harry).

parent(andrew,eugenie).
parent(andrew,beatrice).
parent(sarah_Ferguson,eugenie).
parent(sarah_Ferguson,beatrice).

parent(william,george).
parent(william,charlotte).
parent(william,louis).
parent(kate_Middleton,george).
parent(kate_Middleton,charlotte).
parent(kate_Middleton,louis).

parent(harry,harrison_Mountbatten_Windsor).
parent(meghan_Markle,harrison_Mountbatten_Windsor).

parent(mark_Phillips,peter_Phillips).
parent(mark_Phillips,zara_Tindall).
parent(anne,peter_Phillips).
parent(anne,zara_Tindall).

parent(edward_Earl,louise_Windsor).
parent(edward_Earl,james).
parent(sophie_Rhys_Jones,louise_Windsor).
parent(sophie_Rhys_Jones,james).




husband(Person,Wife):-male(Person),female(Wife),married(Person,Wife),\+divorced(Person,Wife).
wife(Person,Husband):-male(Husband),female(Person),married(Person,Husband),\+divorced(Person,Husband).
father(Parent,Child):-parent(Parent,Child),male(Parent).
mother(Parent,Child):-parent(Parent,Child),female(Parent).
child(Child,Parent):-parent(Parent,Child).
son(Child,Parent):-parent(Parent,Child),male(Child).
daughter(Child,Parent):-parent(Parent,Child),female(Child).

grandparent(GP,GC):-parent(GP,X),parent(X,GC).
grandmother(GM,GC):-grandparent(GM,GC),female(GM).
grandfather(GF,GC):-grandparent(GF,GC),male(GF).
grandchild(GC,GP):-grandparent(GP,GC).
grandson(GS,GP):-grandchild(GS,GP),male(GS).
granddaughter(GD,GP):-grandchild(GD,GP),female(GD).

sibling(Person1,Person2):-father(X,Person1),father(X,Person2),dif(Person1,Person2).
brother(Person,Sibling):-sibling(Person,Sibling),male(Person).
sister(Person,Sibling):-sibling(Person,Sibling),female(Person).
aunt(Person,NieceNephew):-sister(Person,X),parent(X,NieceNephew).
uncle(Person,NieceNephew):-brother(Person,X),parent(X,NieceNephew).
niece(Person,AuntUncle):-female(Person),(aunt(AuntUncle,Person);uncle(AuntUncle,Person)).
nephew(Person,AuntUncle):-male(Person),(aunt(AuntUncle,Person);uncle(AuntUncle,Person)).



