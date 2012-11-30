Instalacja:

1. python bootstrap.py --distribute

2. bin/buildout -c devel.cfg

3. zalozyc baze danych (domyslnie sqlite, ktory tworzony jest automatycznie) lub np. postgres o parametrach (user/nazwa) okreslonych w pliku: project/settings.py

4. uruchomic:
   bin/django syncdb
   bin/django migrate

5. Uruchamiac aplikacje przez:
   bin/django runserver
   
   
Wyjasnienie:
1. Projekt uzywa buildouta do instalacji (opis lekko nieaktualny, ale obrazujacy zasade dzialania: http://restlessbeing.pl/blog/2009/12/27/o-buildoucie-i-django/ )
2. Bazowa konfiguracja buildouta (czyli uzywane moduly/zaleznosci, plik settings projektu) znajduje sie w pliku buildout.cfg
3. Zaleznie od srodowiska w ktorym uruchamiamy projekt mamy jeszcze np.: devel.cfg, test.cfg i production.cfg ktore to konfigi 
   rozszerzaja bazowy buildout.cfg ustawiajac np. inne settings dla poszczegolnych srodowisk
4. W folderze project mamy bazowy plik ustawien: settings.py i pliki specyficzne dla srodowisk: development.py, test.py i production.py
   Jesli przy uruchamianiu buildouta wybierzemy np.: bin/buildout -c test.cfg wowczas w wygenerowanych plikach (bin/django) bedzie ustawione
   iz projekt ma korzystac z ustawien w pliku project/test.py
5. Polecenie bin/django to odpowiednik python manage.py i jest ono generowane przez buildoutowy recipe dla django. Polecenie
   to ustawia sciezki do modulow uzywanych przez projekt
