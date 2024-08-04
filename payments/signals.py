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

from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Category, CategoryType

TYPE_MAPPING = {
    1: "Médicale",
    2: "Scolarité",
    3: "Développement de l'enfant",
    4: "Autre",
}


@receiver(post_migrate)
def create_default_payment_categories(sender, **kwargs):
    if sender.name == 'payments':
        categories = {
            1: [
                {"name": "Traitement médecin/médicament",
                 "description": "Traitement par des médecins spécialistes et les médications, examens spécialisés et soins qu'ils prescrivent"},
                {"name": "Intervention chirurgicale",
                 "description": "Interventions chirurgicales et d'hospitalisation ainsi que les traitements spécifiques qui en résultent"},
                {"name": "Orthodontie", "description": "Orthodontie"},
                {"name": "Logopédie", "description": "Logopédie"},
                {"name": "Ophtalmologie", "description": "Ophtalmologie"},
                {"name": "Psychiatre/Psychologue", "description": "Psychiatre/Psychologue"},
                {"name": "Kinésithérapie", "description": "Kinésithérapie"},
                {"name": "Revalidation", "description": "Revalidation"},
                {"name": "Prothèses/appareils", "description": "Prothèses/appareils"},
                {"name": "Lunettes de vue", "description": "Lunettes de vue"},
                {"name": "Appareil orthodontique", "description": "Appareil orthodontique"},
                {"name": "Lentilles de contact", "description": "Lentilles de contact"},
                {"name": "Semelles/chaussures orthopédiques", "description": "Semelles/chaussures orthopédiques"},
                {"name": "Appareils auditifs", "description": "Appareils auditifs"},
                {"name": "fauteuil roulant", "description": "fauteuil roulant"},
                {"name": "Assurance hospitalisation",
                 "description": "Prime annuelle d'une assurance hospitalisation ou d'une autre assurance complémentaire"},
            ],
            2: [
                {"name": "Sortie scolaire (plusieurs jours)",
                 "description": "Activités scolaires de plusieurs jours, organisées pendant l'année scolaire, comme les classes de neige, classes de mer, voyages scolaires ou d'études ou de stages"},
                {"name": "Matériel/Habillement dû à l'école",
                 "description": "Matériel et/ou habillement scolaire nécessaire, spécialisé et coûteux, liés à des tâches particulières, qui sont mentionnées dans une liste fournie par l'établissement d'enseignement"},
                {"name": "Inscription",
                 "description": "frais d'inscription et les cours pour des études supérieures et des formations particulières ainsi que l'enseignement non subventionné"},
                {"name": "Matériel informatique",
                 "description": "Achat de matériel informatique et d'imprimantes avec les logiciels nécessaire pour les études"},
                {"name": "Cours particulier",
                 "description": "Cours particuliers que l'enfant doit suivre pour réussir son année scolaire"},
                {"name": "Chambre d'étudiant", "description": "Frais liés à la location d'une chambre d'étudiant"},
                {"name": "Études à l'étranger",
                 "description": "Frais spécifique supplémentaires liés à un programme d'études à l'étranger; Après déduction d'allocations d'études et autres bourses d'études"},
            ],
            3: [
                {"name": "Garderie (0 à 3 ans)", "description": "Frais de garde d'enfants de 0 à 3 ans inclus"},
                {"name": "Camps/Stage",
                 "description": "Cotisations, fournitures de base et frais pour des camps et des stages dans le cadre des activités culturelles, sportives ou artistiques"},
                {"name": "Permis de conduire",
                 "description": "Frais d'inscription aux cours de conduite et aux examens théoriques et pratiques du permis de conduire, pour autant que le permis de conduire ne puisse pas être obtenu gratuitement par l'intermédiaire de l'école"},
            ],
            4: [
                {"name": "Autre",
                 "description": "Tous les autres frais qui rentrent dans les frais extraordinaires de commun accord des parents ou ainsi qualifié par le juge"},
            ],
        }

        for type_id, type_name in TYPE_MAPPING.items():
            category_type, created = CategoryType.objects.get_or_create(name=type_name)

            for category_data in categories[type_id]:
                Category.objects.get_or_create(
                    name=category_data["name"],
                    type_id=category_type.id,  # .id pour régler TypeError
                    defaults={"description": category_data["description"]}
                )
