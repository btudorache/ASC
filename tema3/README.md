# Tema 3 Arhitectura Sistemelor de Calcul

334CA Tudorache Bogdan Mihai

Tema contine implementarea algoritmului *Accessible Population* pe **GPU** folosind **CUDA**. 

# Implementare

Tema contine urmatoarele etape:

* Alocarile principale si lucrul pe **CPU**

* Implementarea algoritmului pe **GPU**

* Explicatia rezultatelor

## Alocarile principale si lucrul pe **CPU**

In aceasta parte, in functia principala doar citesc toate datele problemei 
(latitudinile, longitudinele, populatiile oraselor etc...), informatii pe care
le stochez in mod dinamic si aloc datele pe GPU. La final, dupa rularea kernelului
si afisarea rezultatelor, dealoc toata memoria folosita.

## Pornirea kernelului pe **GPU**

Folosesc un singur kernel pentru implementarea algoritmului. Implementarea lui
este urmatoarea:

Pornesc atatea thread-uri cate orase primesc la input, impartite in block-uri cu 
block size cat mai mare (1024 in cazul meu). Fiecare thread calculeaza populatia accesibila
pentru index-ul asociat, dar actualizeaza si orasele contra carora face verificarea de 
populatie accesibila. Aceste 2 operatii se actualizeaza in mod atomic, pentru ca nu se stie
exact ce thread-uri vor accesa resursele comune in acelasi timp.

Pentru a evita accesuri inutile la GPU, memorez in variabile locale datele asociate
index-ului curent intr-un thread.

O alta optimizare a accesului la memorie este utilizarea memoriei shared. In fiecare
block pornit, stochez latitudinea, longitudinea si populatiea oraselor asociate thread-urilor
din blocul curent. Cand un thread ia la rand orasele pentru a verifica conditia de
populatie accesibila, verifica mai intai daca datele necesare sunt existente in memoria shared,
pentru a evita daca se poate un acces la memoria de pe GPU.

## Explicatia rezultatelor

Nu am reusit sa fac programul sa se incadreze in TIMEOUT-urile asociate 
cand se ruleaza si testul H1, asa ca am pus o conditie prin
care dau skip daca testele sunt mai mari decat o dimensiune anume.
Codul se incadreaza fara probleme pe primele 4 teste, pe oricare 
dintre cele 3 placi video pe care ruleaza pe fep. Uneori trecea
si testul H1, insa doar pe placa A100.

Tin sa mentionez ca am incercat destul de multe variante de optimizare,
printre care: 

* folosirea mai ampla a memoriei shared (nu s-a putut pentru
ca dimensiunea acestei memorii este destul de mica) 

* pornirea a N^2 thread-uri, unde N este numarul de orase in grid-uri
 bidimensionale (codul mergea foarte prost pe testul H1 in acest caz,
 sau chiar nu executa deloc testul pentru ca era prea mare numarul
 de thread-uri pornite),

* pornirea a N * (N + 1) / 2 thread-uri (a esuat din motive asemanatoare
cu cele de mai sus)

* impartirea "muncii" intre thread-uri cat mai echitabila, cu indici de 
tipul start-end

* caching-ul valorilor sinus si cosinus pentru a evita repetitia
 unor astfel de calcule costisitoare

* combinatii intre toate cele de mai sus

Cu toate astea, variantele de mai sus mergeau de obicei mai prost decat variata
pe care am implementat-o in cadrul temei.


