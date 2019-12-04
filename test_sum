eq(zero,zero).
eq(s(X),s(X)).

dif(zero, s(_)).
dif(s(_), zero).
dif(s(X),s(Y)):-dif(X,Y).

sum(zero, M, M).
sum(s(N), M, s(K)) :- sum(N, M, K).
prod(zero, _, zero).
prod(s(N), M, P) :- sum(M, K, P), prod(M, N, K).

less(zero, s(_)).
less(s(X), s(Y)) :- less(X,Y).

composite(X) :- prod(A,B,X), dif(A,s(zero)), dif(B,s(zero)).
prime(X) :- less(s(zero),X), not(composite(X)).


