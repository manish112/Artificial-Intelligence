initBoard(N,Q):-N1 is N+1,init(N1,1,Q).

init(N,N,[]).
init(N,N2,[Q1|Q]) :-Q1 is N2,N2=<N,N1 is N2+1,init(N,N1,Q).

del(X,[X|LIST1],LIST1).
del(X,[Y|LIST1],[Y|LIST2]):-del(X,LIST1,LIST2).

l_perm([],[]).
l_perm(L,[X|P]):-del(X,L,L1),l_perm(L1,P).

l_mem(A,[A|_]).
l_mem(A,[_|T]):-l_mem(A,T).


calcDiag([],[],[],[]).
calcDiag([Row|Rows],[Col|Cols],[RD|Rds],[LD|Lds]) :-
     RD is Row + Col,
     LD is Row - Col,
     calcDiag(Rows,Cols,Rds,Lds).


checkDiag([_]).
checkDiag([D1|D]) :-  \+l_mem(D1,D), checkDiag(D).


nqueens(N,Col) :-
	 initBoard(N,Row),
     l_perm(Row,Col),
     calcDiag(Row,Col,Rds,Lds),
     checkDiag(Rds),
     checkDiag(Lds).

