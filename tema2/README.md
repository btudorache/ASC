# Tema 2 Arhitectura Sistemelor de Calcul

334CA Tudorache Bogdan Mihai

Tema contine implementarea si eficientizarea unor operatii pe matrici in limbajul **C**. 

# Implementare

Tema contine urmatoarele etape:

* blas - implementarea operatiei folosind biblioteca **BLAS Atlas**

* neopt - implementarea "de mana", varianta neoptimizata

* opt - imbunatatirea variantei neopt

* Explicarea statisticilor de utilizare a cache-ului in urma rularii cu cachegrind

* Analiza comparativa folosind grafice

## implementarea operatiei folosind biblioteca **BLAS Atlas**

In implementarea folosind biblioteca BLAS Atlas am folosit functiile:

* ```DGEMM``` care permite inmultirea unor matrici normale dar si 
adunarea lor in cadrul aceleasi operatii

* ```DTRMM``` care permite inmultirea unor matrici triunghiulare (atat superior triunghiulare cat si inferior)

Practic, operatiile se rezuma la inmultirea unei matrice simple de 
2 ori cu o matrice triunghiulara (odata superior triunghiulara, iar
apoi transpusa ei devine inferior triunghiulara) si la o operatie
combinata de inmultire a unor matrici normale si adunarea acestei
inmultiri cu rezultatul anterior obtinut. 

Pentru aceste calcule apelam *DTRMM* pentru a calcula R1 = B * A, apoi, din nou *DTRMM* pentru a calcula R2 = R1 * A^T, iar apoi apelam *DGEMM* pentru operatia R = R2 + B * B^T. Pentru modul
in care este construit API-ul oferit de biblioteca, este necesar
sa ne pastram si o copie a matricei B.

## implementarea "de mana", varianta neoptimizata

La varianta neoptimizata, am facut calcule simple: transpunerea, adunarea si
inmultirea matricilor. Este de mentionat ca am optimizat inmultirea matricilor
triunghiulare prin evitarea inmultirii elementelor de pe pozitiile in care matricea
triunghiulara are valoarea 0.

## imbunatatirea variantei neopt

In implementarea optimizata, am implementat urmatoarele optimizari:

- am folosit directiva ```inline``` pentru functii pentru a evita creearea
unui nou frame de functie la fiecare apelare

- am marcat variabilele care nu isi schimba valoarea des sau deloc cu directiva 
```register``` pentru a incerca cache-uirea acelor variabile in registri

- am detectat constantele din bucle si am pastrat valoare lor intr-o 
variabila marcata cu ```register```

- am optimizat accesul la memorie prin schimbarea ordinii buclelor de la i-j-k
 la i-k-j in ideea de a genera cat mai putine cache miss-uri printr-o accesare
 a elementelor cat mai 'secvential' posibila.

- am optimizat accesul la vectori in functiile de transpunere, adunare, si 
inmultire a matricilor (doar pentru inmultirea a 2 matrici non-triunghiulare).
De mentionat ca la inmultirea matricilor, implementarea imbunatatirii accesului
la variabile a fost inspirata din rezolvarea laboratorului 5, taskul 3.

- am folosit loop-unrolling in fuctia de inmultire a 2 matrici non triunghiulare
pentru a evita branch-uri si a genera cat mai putine branch miss-uri gratie evitarii verificarii
clauzelor conditionale.

- m-am folosit de proprietatea inmultarii unei matrici cu transpusa ei, prin
 care practic e nevoie numai de parea superioara/inferioara fata de diagonala
principala pentru ca celelalte calcule sunt simetrice.

## Explicarea statisticilor de utilizare a cache-ului in urma rularii cu cachegrind

Se pot trage concluzii despre toate cele 3 variante de implementare in urma rularii 
cu cachegrind pe partitia nehalem:

* pentru varianta **BLAS**, codul scris este de departe cel mai eficient dintre toate
variantele, numarul de referiri la memorie si referiri la date este chiar si cu 2 ordine
de marime mai mic decat celelalte 2 variante

* varianta **neoptimizata** este cea mai slaba, avand numarul de referinte la memorie
 si la date de ordinul miliardelor, si chiar si o rata de D1 cache miss rate destul de
  mare (3.8%)

* varianta **optimizata** este semnificativ mai buna ca cea optimizata, cu un numar de referinte la date si la instructiuni injumatatit, cu numarul de referinte la ultimul nivel
de cache de 10 ori mai mic si numarul de branch-uri injumatatit.

Se poate identifica care dintre optimizari a avut efect asupra unei anumite parti din 
statistica oferita de cachegrind:

- Optimizarile de acces la vectori si de folosire a directivei ```register``` au redus 
semnificativ numarul de referiri la date

- Loop-unrolling a redus numarul de branch-uri verificate

- Evitarea unor calcule gratie proprietatii de inmultire unei matrice cu transpusa ei
a avut mare rol in reducerea referintelor la date si la instructiuni

- Folosirea directivei ```register``` si schimbarea ordinii buclelor au redus numarul de D1 misses.

## Analiza comparativa folosind grafice

Am realizat niste grafice de viteza a rularii in functie de dimensiunea
problemei pentru toate cele 3 programe si 7 input-uri 
(dimensiunile 200, 400, 600, 800, 1000, 1200, 1400) folosind bilbioteca
de python matplotlib (rularile au fost facute pe masina mea personala, 
cu un procesor Intel(R) Core(TM) i7-4600U CPU @ 2.10GHz si 12GB memorie RAM si folosind WSL2). 
Statisticile obtinute sunt cum ne-am asteptat: 

* varianta **BLAS** este detasat cea mai eficienta, cu un timp de rulare
chiar si pentru N=1400 de 1 secunda

* varianta **neopt** este cea mai slaba, deja de la N=800 exponentiala 
creste semnificativ

* varianta **opt_m** este mai rapida ca cea anterioara, cu timpi
acceptabili chiar si pentru valori mari ale lui N