"""
Neok-Budget: A Django-based web application for budgeting.
Copyright (C) 2024  David Botton, Arnaud Mahieu

Developed for Jurinet and its branch Neok-Budget.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import re
from PIL import Image
from django.core.exceptions import ValidationError
from django.core.validators import validate_email as django_validate_email, RegexValidator
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _


"""
Django échappe automatiquement les entrées pour les requêtes SQL et utilise l'ORM (Object-Relational Mapping) qui prépare les requêtes de manière sécurisée, limitant ainsi les risques d'injection SQL (SQLi).
"""

def validate_image(file, max_size=5242880, max_width=4000, max_height=4000):
    """
    Valide le type, la taille et les dimensions de l'image.
    Accepte seulement les formats JPEG, PNG, et GIF. Vérifie que l'image ne dépasse pas
    la taille maximale et les dimensions maximales spécifiées.

    Args:
    file (File): Le fichier image à valider.
    max_size (int): Taille maximale du fichier en octets.
    max_width (int): Largeur maximale de l'image en pixels.
    max_height (int): Hauteur maximale de l'image en pixels.

    Raises:
    ValidationError: Si le fichier ne répond pas aux critères spécifiés.
    """
    valid_formats = ['JPEG', 'PNG', 'GIF']
    try:
        image = Image.open(file)
        image_format = image.format
        if image_format not in valid_formats:
            raise ValidationError(_('Unsupported file type. Please upload a JPEG, PNG, or GIF image.'))
        if file.size > max_size:
            raise ValidationError(_('Image file too large (>{0} MB).').format(max_size / 1048576))
        if image.width > max_width or image.height > max_height:
            raise ValidationError(_('Image dimensions exceed the maximum allowed: {0}x{1} pixels.').format(max_width, max_height))
    except Exception as e:
        raise ValidationError(_('Invalid image file. Error: {0}').format(e))
    file.seek(0)

def clean_email(email):
    """
    Valide le format de l'adresse email en utilisant la fonctionnalité intégrée de Django.

    Args:
    email (str): L'adresse email à valider.

    Returns:
    str: L'adresse email validée.

    Raises:
    ValidationError: Si l'adresse email n'est pas valide.
    """
    try:
        django_validate_email(email)
    except ValidationError:
        raise ValidationError(_('Invalid email address.'))
    return email

def sanitize_text(text):
    """
    Assainit le texte en supprimant les balises HTML et en éliminant les chiffres et symboles, tout en conservant les espaces.
    Ceci est utilisé pour empêcher les attaques XSS et pour nettoyer les entrées de texte en préservant la lisibilité.

    Args:
    text (str): La chaîne de caractères à assainir.

    Returns:
    str: La chaîne de caractères assainie.
    """
    text = strip_tags(text)
    text = re.sub(r'[^a-zA-Z\s]+', '', text)
    return text

def validate_national_number(national_number):
    """
    Valide le format du numéro national en éliminant les points et les tirets,
    et en s'assurant que le nombre de chiffres est exactement de 11. Cette fonction
    vérifie également que les troisième et quatrième chiffres constituent un mois valide (01-12)
    et que les cinquième et sixième chiffres forment un jour valide (01-31).

    Args:
    national_number (str): Le numéro national à valider.

    Returns:
    str: Le numéro national nettoyé.

    Raises:
    ValidationError: Si le numéro ne consiste pas exactement de 11 chiffres, ou si le mois et le jour ne sont pas valides.
    """
    clean_number = national_number.replace('.', '').replace('-', '')
    if len(clean_number) != 11:
        raise ValidationError(_('National number must be exactly 11 digits long.'))

    month = int(clean_number[2:4])
    day = int(clean_number[4:6])

    if not (1 <= month <= 12):
        raise ValidationError(_('The month must be between 01 and 12.'))
    if not (1 <= day <= 31):
        raise ValidationError(_('The day must be between 01 and 31.'))
    return clean_number

def validate_password(password):
    """
    Assure la force du mot de passe en vérifiant que le mot de passe contient au moins
    8 caractères, incluant des minuscules, des majuscules et des chiffres.

    Args:
    password (str): Le mot de passe à valider.

    Returns:
    str: Le mot de passe validé.

    Raises:
    ValidationError: Si le mot de passe ne répond pas aux exigences.
    """
    if len(password) < 8:
        raise ValidationError(_('The password must be at least 8 characters long.'))
    if not (re.search(r'[a-z]', password) and re.search(r'[A-Z]', password) and re.search(r'[0-9]', password)):
        raise ValidationError(_('Password must include lowercase, uppercase, and numbers.'))
    return password

def validate_telephone(telephone):
    """
    Valide le numéro de téléphone en utilisant des expressions régulières pour s'assurer que
    le format est correct (+999999999 jusqu'à 13 chiffres autorisés).

    Args:
    telephone (str): Le numéro de téléphone à valider.

    Returns:
    str: Le numéro de téléphone validé.

    Raises:
    ValidationError: Si le format du numéro de téléphone est invalide.
    """
    if not telephone or telephone == '+32':
        return ''

    phone_regex = RegexValidator(regex=r'^\+?1?\d{7,13}$', message='Phone number must be entered in the format: "+999999999". Up to 13 digits allowed.')
    try:
        phone_regex(telephone)
    except ValidationError:
        raise ValidationError(_('Invalid phone number format.'))
    return telephone
