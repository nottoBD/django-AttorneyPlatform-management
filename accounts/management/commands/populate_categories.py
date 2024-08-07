from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _

#  $ python manage.py populate_categories
#BUG:
from accounts.models import Category, SubCategory


# la traduction ne fonctionne pas de cette manière
class Command(BaseCommand):
    help = _('Prepopulates the database with predefined categories and sub-categories.')


    def handle(self, *args, **kwargs):
        categories = {
            _("Medical and paramedical expenses"): [
                _("Treatments by medical specialists and the medications, specialized examinations and care they prescribe"),
                _("Costs of surgical and hospitalization procedures and the specific treatments resulting therefrom"),
                _("Medical and paramedical expenses and devices, including orthodontics, speech therapy, ophthalmology, etc."),
                _("Annual premium for hospitalization insurance or other supplementary insurance"),
            ],
            _("Costs relating to school training"): [
                _("School activities of several days, like snow classes, sea classes, green classes"),
                _("Necessary, specialized and costly school materials and/or clothing"),
                _("Tuition fees and courses for higher education and special training"),
                _("Purchase of computer hardware and printers with necessary software"),
                _("Private lessons for school year success"),
                _("Cost of renting a student room"),
                _("Additional specific costs related to study abroad program"),
            ],
            _("Expenses related to the development of the personality and development of the child"): [
                _("Child care expenses from 0 to 3 years included"),
                _("Dues, basic supplies, and fees for camps and internships in cultural, sporting, or artistic activities"),
                _("Registration fee for driving courses and theoretical and practical examinations of the driving licence"),
            ],
        }

        for category_name, subcats in categories.items():
            category, created = Category.objects.get_or_create(name=category_name)
            for subcat_name in subcats:
                SubCategory.objects.get_or_create(category=category, name=subcat_name)

        self.stdout.write(self.style.SUCCESS('SUCCES: insertion Catégories de frais.'))
