# olej_to_wszystko
odstresowujący lecz trudny jak główny bohater klon asteroids

## sterowanie
* **góra** - przyspieszenie
* **lewo, prawo** - obrót
* **spacja** - strzał
* **r** - restart gry

## instalacja
### windows
* uruchom olej.exe w katalogu olej_windows
### ubuntu
* sudo apt install python3 python3-pip
* pip3 install -r requirements.txt
* python3 olej.py
### os x 
* xcode-select --install
* brew install python3 python3-pip sdl2* git
* pip3 install -r requirements.txt
* pip3 uninstall pygame
* git clone -b 1.9.6 https://github.com/pygame/pygame.git --single-branch
* cd pygame
* python3 setup.py -config -auto -sdl2
* python setup.py install
* python3 olej.py
