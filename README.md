# Installation locale
## Pré-requis
- Invite de commande windows en Administrateur
- Python installé (3.11.8)
- Git installé
- postgresql configuré et **lancé**
- copier le lien du repo: **https://github.com/nottoBD/projetTFE.git**
- n'importe quel dossier dans lequel placer le repository
  
## PostgreSQL
Option 1: remplacer dans fExtra/settings.py les coordonnées postgresql par les votres (NAME, USER, PASSWORD) 


**Option 2:** respecter les coordonnées par défaut (configurer ton postgresql selon l'image suivante)

![318116503-c8f9592d-bd67-4c6a-a732-dc1d587f1ff3](https://github.com/nottoBD/projetTFE/assets/94763728/0d526b67-3377-4f8c-abda-466990ca8a86)

## Video d'installation (Linux)

https://github.com/nottoBD/projetTFE/assets/94763728/5c32c0d4-c302-4f28-b5c0-8451c0da0eb1


## Commandes (Windows)

``` 
git clone -b David https://github.com/nottoBD/projetTFE.git
cd projetTFE\fExtra
python -m venv ..\env
..\env\Scripts\activate
pip install --upgrade pip
pip install -r ..\requirements.txt
python manage.py makemigrations accounts
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata testdata.json 
python manage.py createsuperuser

python manage.py runserver

``` 
