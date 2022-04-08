# Tema 1 Arhitectura Sistemelor de Calcul - Marketplace

334CA Tudorache Bogdan Mihai

Tema contine implementarea unei probleme de concurenta de tipul
**multiple producer - multiple consumer** in **Python**. 

# Implementare

Cele mai importante parti ale implementarii sunt metodele direct implicate 
in flow-ul simularii si structura datelor din cadrul clasei Marketplace:

* Structura clasei Marketplace

* implementarea functiei ```publish```

* implementarea functiei ```add_to_cart```

* implementarea functiei ```remove_from_cart```

* implementarea functiei ```place_order```

## Structura clasei Marketplace

Fiecare metoda este sincronizata cu ajutorul unui loc ```market_lock```.

Dimensiunea cozilor fiecarui producator este stocata prin intermediul unui
dictionar care mapeaza numele producatorului si numarul de obiecte pe care 
le are in coada ```producer_items_count```. 

Produsele puse la dispozitie 
consumatorilor sunt stocate in campul ```products```, care are o structura
de dictionare imbricate. Acest camp are drept chei numele producatorilor,
iar valorile sunt niste dictionare care semnifica cantitatea si rezervarea
fiecarui aliment in parte care a fost produs de un anumit producator.
Astfel, ```products['nume_producator']``` e un dictionar de alimente,
iar ```products['nume_producator']['nume_aliment']``` este un tuplu de 
tipul ```(nr_alimente_produse, nr_alimente rezervate)```.

Carucioarele consumatorilor sunt stocate in campul ```carts```, care are
de asemenea o structura de dictionare imbricate. Pentru fiecare cart in parte,
se mapeaza atat alimentele care sunt in acel cart, cat si producatorii
acelor alimente si numarul in care se gasesc. Astfel, ```carts['nume_cart']``` 
este un dictionar foarte asemanator cu structura campului ```products```. 
```carts['nume_cart']['nume_aliment']``` un dictionar de producatori, si 
in final ```carts['nume_cart']['nume_aliment']['nume_producator']``` specifica
in ce cantitate se afla un aliment creat de un anumit producator intr-un anumit cos.

Campul ```all_products``` stocheaza toate informatiile despre alimentele produse
pe masura ce sunt adaugate.

## implementarea functiei ```publish```

Daca coada unui anumit producator nu este plina, se incearca adaugarea
produsului in campul ```products```, sau incrementarea cantitatii lui 
daca deja exista.

## implementarea functiei ```add_to_cart```

Daca produsul ce se vrea adaugat in cos exista si daca nu sunt rezervate
toate, se adauga in cos alaturi de numele producatorului care a produs 
acel aliment, si se actualizeaza numarul de produse rezervate.

## implementarea functiei ```remove_from_cart```

Functia se executa in oglinda fata de ```add_to_cart``` si se pleaca de la
presupunerea ca nu se va scoate din cos un obiect care nu exista deja in cos.
Daca se scoate un obiect din cos, se scoate din lista de produse rezervate 
si se scoate si din cosul propriu zis.

## implementarea functiei ```place_order```

Cand se plaseaza o comanda, se construieste lista de obiecte plasate,
si se actualizeaza si dictionarul de obiecte rezervate, pentru a da
ocazia producatorilor sa produca in continuare.
