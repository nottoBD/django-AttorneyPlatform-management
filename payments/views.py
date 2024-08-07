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

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Sum, Q, F
from django.db.models.functions import ExtractQuarter, ExtractYear
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound, HttpResponseForbidden, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.text import capfirst
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from xhtml2pdf import pisa


from accounts.models import JugeCase, AvocatCase, ParentCase
from .forms import PaymentDocumentForm, CaseForm, IndexPaymentForm, AddJugeAvocatForm, \
    ConvertDraftCaseForm, CombineDraftsForm, ChildForm
from .models import Document, Case, Category, CategoryType, IndexHistory, Child

User = get_user_model()


# EVERYONE
# ----------------------------------------------------------------------------------------------------------------------
class CaseListView(LoginRequiredMixin, ListView):
    model = Case
    template_name = 'payments/list_case.html'
    context_object_name = 'cases'

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        case_id = self.kwargs.get('pk')
        if case_id:
            case = get_object_or_404(Case, pk=case_id)
            if not self.has_access_to_case(request.user, case):
                raise Http404("You do not have permission to access this case.")

        return response

    def get_queryset(self):
        user = self.request.user

        parent_cases = Case.objects.filter(parent_cases__parent=user)
        avocat_cases = Case.objects.filter(id__in=AvocatCase.objects.filter(avocat=user).values('case_id'))
        juge_cases = Case.objects.filter(id__in=JugeCase.objects.filter(juge=user).values('case_id'))

        queryset = parent_cases | avocat_cases | juge_cases

        return queryset.distinct()

    def has_access_to_case(self, user, case):
        return ParentCase.objects.filter(parent=user, case=case).exists() or \
               AvocatCase.objects.filter(avocat=user, case=case).exists() or \
               JugeCase.objects.filter(juge=user, case=case).exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['can_create_draft'] = not Case.objects.filter(parent_cases__parent=user, draft=False).exists()

        return context


class PaymentHistoryView(LoginRequiredMixin, ListView):
    model = Document
    template_name = 'payments/case_payment_history.html'
    context_object_name = 'payments'

    def dispatch(self, request, *args, **kwargs):
        case_id = kwargs.get('case_id')

        if case_id:
            self.case = get_object_or_404(Case, pk=case_id)
        else:
            return self.handle_no_case_id()

        if not self.user_has_access_to_case(request.user, self.case):
            return self.handle_no_access()

        return super().dispatch(request, *args, **kwargs)

    def handle_no_case_id(self):
        return HttpResponseNotFound("Case ID is required but was not provided.")

    def handle_no_access(self):
        return HttpResponseForbidden("You do not have permission to access this case.")

    def user_has_access_to_case(self, user, case):
        return case.parent1 == user or case.parent2 == user or user.role in ["lawyer", "judge", "administrator"] or (case.draft and case.parent1 == user)

    def get_queryset(self):
        queryset = Document.objects.filter(case=self.case)
        selected_year = self.request.GET.get('year')
        selected_quarter = self.request.GET.get('quarter')

        if selected_year and selected_quarter:
            try:
                selected_year = int(selected_year)
                selected_quarter = int(selected_quarter)

                start_month = (selected_quarter - 1) * 3 + 1
                end_month = start_month + 2

                start_date = timezone.datetime(selected_year, start_month, 1)
                end_date = timezone.datetime(selected_year, end_month + 1, 1) if end_month < 12 else timezone.datetime(selected_year + 1, 1, 1)

                queryset = queryset.filter(date__gte=start_date, date__lt=end_date)
            except (TypeError, ValueError):
                queryset = Document.objects.filter(case=self.case)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        case = self.case
        parent1 = case.parent1
        parent2 = case.parent2
        user = self.request.user

        selected_year = self.request.GET.get('year')
        selected_quarter = self.request.GET.get('quarter')

        latest_index_history = IndexHistory.objects.order_by('-created_at').first()
        contribution_amount = 0
        if latest_index_history:
            contribution_amount = latest_index_history.amount * case.number_of_children

        if selected_year and selected_quarter:
            try:
                parent1_valid_payments = self.get_payments(case, parent1, 'validated', selected_year, selected_quarter)
                parent2_valid_payments = self.get_payments(case, parent2, 'validated', selected_year, selected_quarter)
                parent1_pending_payments = self.get_payments(case, parent1, 'pending', selected_year, selected_quarter)
                parent2_pending_payments = self.get_payments(case, parent2, 'pending', selected_year, selected_quarter)
            except (TypeError, ValueError):
                parent1_valid_payments = []
                parent2_valid_payments = []
                parent1_pending_payments = []
                parent2_pending_payments = []
        else:
            parent1_valid_payments = self.get_payments(case, parent1, 'validated')
            parent2_valid_payments = self.get_payments(case, parent2, 'validated')
            parent1_pending_payments = self.get_payments(case, parent1, 'pending')
            parent2_pending_payments = self.get_payments(case, parent2, 'pending')

        context.update(self.build_context(case, parent1, parent2, parent1_valid_payments, parent2_valid_payments, parent1_pending_payments, parent2_pending_payments, contribution_amount))

        payments_with_permissions = [{'payment': payment, 'can_delete': payment.user_can_delete(user)} for payment in self.get_queryset()]
        context['payments_with_permissions'] = payments_with_permissions

        return context

    def get_payments(self, case, parent, status, year=None, quarter=None):
        queryset = Document.objects.filter(case=case, user=parent, category__type__isnull=False, status=status)
        if year and quarter:
            queryset = queryset.filter(date__year=year, date__quarter=quarter)
        return queryset.values('category__type', 'category').annotate(total_amount=Sum('amount'))

    def build_context(self, case, parent1, parent2, parent1_valid_payments, parent2_valid_payments, parent1_pending_payments, parent2_pending_payments, contribution_amount):
        parent1_valid_payments_dict = {(payment['category__type'], payment['category']): payment['total_amount'] for payment in parent1_valid_payments}
        parent2_valid_payments_dict = {(payment['category__type'], payment['category']): payment['total_amount'] for payment in parent2_valid_payments}
        parent1_pending_dict = {(payment['category__type'], payment['category']): payment['total_amount'] for payment in parent1_pending_payments}
        parent2_pending_dict = {(payment['category__type'], payment['category']): payment['total_amount'] for payment in parent2_pending_payments}

        # Calculer les pourcentages à partir des ParentCase
        parent_cases = case.parent_cases.all()
        parent1_percentage = parent_cases.filter(parent=case.parent1).first().percentage if case.parent1 else 0
        parent2_percentage = parent_cases.filter(parent=case.parent2).first().percentage if case.parent2 else 0

        categories = Category.objects.filter(type__isnull=False)
        categories_by_type = {}
        category_ids = []

        for category in categories:
            category_type_id = category.type_id
            parent1_amount = parent1_valid_payments_dict.get((category_type_id, category.id), 0)
            parent2_amount = parent2_valid_payments_dict.get((category_type_id, category.id), 0)
            parent1_pending_amount = parent1_pending_dict.get((category_type_id, category.id), 0)
            parent2_pending_amount = parent2_pending_dict.get((category_type_id, category.id), 0)

            if parent1_amount == 0 and parent2_amount == 0 and parent1_pending_amount == 0 and parent2_pending_amount == 0:
                continue

            category_ids.append(category.id)

            if category_type_id not in categories_by_type:
                categories_by_type[category_type_id] = {
                    'type_name': category.type.name,
                    'categories': [],
                }
            categories_by_type[category_type_id]['categories'].append({
                'category_id': category.id,
                'category_name': category.name,
                'parent1_amount': parent1_amount,
                'parent2_amount': parent2_amount,
                'parent1_pending_amount': parent1_pending_amount,
                'parent2_pending_amount': parent2_pending_amount,
            })

        parent1_total = sum(parent1_valid_payments_dict.values())
        parent2_total = sum(parent2_valid_payments_dict.values())
        difference = abs(parent1_total - parent2_total)
        in_favor_of = parent1 if parent1_total > parent2_total else parent2

        payment_years = Document.objects.filter(case=case).dates('date', 'year')
        years = [year.year for year in payment_years]

        active_quarters = Document.objects.annotate(
            quarter=ExtractQuarter('date'),
            year=ExtractYear('date')
        ).filter(case=case).values_list('year', 'quarter').distinct()

        active_quarters_per_year = {year: set() for year in years}
        for year, quarter in active_quarters:
            active_quarters_per_year[year].add(quarter)

        return {
            'case': case,
            'parent1_user': parent1,
            'parent2_user': parent2,
            'categories_by_type': categories_by_type,
            'parent1_total': parent1_total,
            'parent2_total': parent2_total,
            'total_amount': parent1_total + parent2_total,
            'difference': difference,
            'in_favor_of': in_favor_of,
            'years': years,
            'category_ids': category_ids,
            'is_draft': case.draft,
            'contribution_amount': contribution_amount,
            'parent1_percentage': parent1_percentage,
            'parent2_percentage': parent2_percentage,
            'active_quarters_per_year': active_quarters_per_year,
        }


class CategoryPaymentsView(LoginRequiredMixin, ListView):
    model = Document
    template_name = 'payments/case_category_history.html'
    context_object_name = 'payments'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs.get('category_id')
        case_id = self.kwargs.get('case_id')

        # Vérifier et récupérer la catégorie
        category = get_object_or_404(Category, id=category_id)
        context['category'] = category

        # Obtenir le dossier basé sur le case_id et les droits d'accès
        case = get_object_or_404(Case, id=case_id)
        context['case'] = case

        # Récupérer les paiements pour les parents
        parent1_payments = Document.objects.filter(case=case, category_id=category_id, user=case.parent1)
        parent2_payments = Document.objects.filter(case=case, category_id=category_id, user=case.parent2)

        # Appliquer les filtres pour l'année et le trimestre
        year = self.request.GET.get('year')
        quarter = self.request.GET.get('quarter')
        if year and quarter:
            try:
                start_date, end_date = self.get_quarter_dates(year, quarter)
                parent1_payments = parent1_payments.filter(date__range=(start_date, end_date))
                parent2_payments = parent2_payments.filter(date__range=(start_date, end_date))
            except ValueError as e:
                print(f"Error in date range calculation: {e}")

        context['parent1_payments'] = parent1_payments
        context['parent2_payments'] = parent2_payments
        context['parent1_name'] = case.parent1.get_full_name()
        context['parent2_name'] = case.parent2.get_full_name()

        # Ajouter les paramètres année et trimestre au contexte
        context['selected_year'] = year
        context['selected_quarter'] = quarter

        return context

    def get_quarter_dates(self, year, quarter):
        year = int(year)
        quarter = int(quarter)
        start_month = (quarter - 1) * 3 + 1
        end_month = start_month + 2

        start_date = datetime(year, start_month, 1)
        if end_month < 12:
            end_date = datetime(year, end_month + 1, 1)
        else:
            end_date = datetime(year + 1, 1, 1)
        return start_date, end_date


class PaymentHistoryPDFView(LoginRequiredMixin, View):
    def get(self, request, case_id=None, *args, **kwargs):
        user = self.request.user

        # Vérifier si case_id est fourni
        if case_id is None:
            return HttpResponse("No case_id provided.", status=400)

        case = get_object_or_404(Case, id=case_id)

        # Obtenir les paramètres de la requête GET
        selected_year = request.GET.get('year', None)
        selected_quarter = request.GET.get('quarter', None)

        # Vérifier et convertir les paramètres en entiers si valides
        if selected_year and selected_year.isdigit():
            selected_year = int(selected_year)
        else:
            selected_year = None

        if selected_quarter and selected_quarter.isdigit():
            selected_quarter = int(selected_quarter)
        else:
            selected_quarter = None

        # Créer une instance de PaymentHistoryView pour obtenir les données
        payment_history_view = PaymentHistoryView()
        payment_history_view.request = request
        payment_history_view.kwargs = {'case_id': case_id}  # Passer case_id comme kwargs
        payment_history_view.case = case

        # Appeler dispatch pour initialiser la vue correctement
        payment_history_view.dispatch(request, *args, **kwargs)

        # Obtenir object_list en appelant get_queryset()
        payment_history_view.object_list = payment_history_view.get_queryset()

        # Obtenir le contexte de la vue PaymentHistoryView
        context = payment_history_view.get_context_data()

        # Déterminer le nom du fichier PDF
        if selected_year is None or selected_quarter is None:
            context['selected_year'] = datetime.now().year
            context['selected_quarter'] = None
            filename = f'PaymentHistory_{context["selected_year"]}.pdf'
        else:
            context['selected_year'] = selected_year
            context['selected_quarter'] = selected_quarter
            filename = f'PaymentHistory_{context["selected_year"]}_Q{context["selected_quarter"]}.pdf'

        # Rendre le template avec les données de contexte
        html_string = render_to_string('payments/pdf_template.html', context)

        # Générer le PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        pisa_status = pisa.CreatePDF(html_string, dest=response)

        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html_string + '</pre>')

        return response


@require_POST
def add_category(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        new_category_name = request.POST.get('new_category_name')
        new_category_description = request.POST.get('new_category_description')

        if new_category_name:
            # Capitalize the first letter of the category name
            new_category_name = capfirst(new_category_name.strip())
            new_category_description = capfirst(new_category_description.strip())

            # Check if the category already exists
            existing_category = Category.objects.filter(name=new_category_name).exists()

            if existing_category:
                return JsonResponse({'success': False, 'error': 'Category already exists.'})

            # Get or create the "Autre" category type
            category_type_autre, created = CategoryType.objects.get_or_create(name="Autre")

            # Create the new category
            new_category = Category.objects.create(
                name=new_category_name,
                description=new_category_description,
                type=category_type_autre
            )

            return JsonResponse({
                'success': True,
                'category_id': new_category.pk,
                'category_name': new_category.name,
            })

        return JsonResponse({'success': False, 'error': 'Category name is required.'})

    return JsonResponse({'success': False, 'error': 'Invalid request.'})


def get_quarter_dates(year, quarter):
    try:
        quarter = int(quarter)  # Assurez-vous que quarter est un entier
    except ValueError:
        raise ValueError("Quarter should be an integer between 1 and 4")

    if quarter == 1:
        start_date = timezone.datetime(int(year), 1, 1).date()
        end_date = timezone.datetime(int(year), 3, 31).date()
    elif quarter == 2:
        start_date = timezone.datetime(int(year), 4, 1).date()
        end_date = timezone.datetime(int(year), 6, 30).date()
    elif quarter == 3:
        start_date = timezone.datetime(int(year), 7, 1).date()
        end_date = timezone.datetime(int(year), 9, 30).date()
    elif quarter == 4:
        start_date = timezone.datetime(int(year), 10, 1).date()
        end_date = timezone.datetime(int(year), 12, 31).date()
    else:
        raise ValueError("Invalid quarter value. Must be between 1 and 4.")

    return start_date, end_date


@login_required
def add_child(request, case_id):
    case = get_object_or_404(Case, id=case_id)

    if request.method == 'POST':
        form = ChildForm(request.POST, case_id=case_id)
        if form.is_valid():
            child = form.save(commit=False)
            child.case = case
            child.save()

            return redirect('payments:child', case_id=case_id)
        else:
            print(form.errors)
    else:
        form = ChildForm(case_id=case_id)

    children = case.children.all()

    return render(request, 'payments/child.html', {'form': form, 'case': case_id, 'children': children})


@login_required
def delete_child(request, case_id, child_id):
    child = get_object_or_404(Child, id=child_id, case_id=case_id)
    child.delete()
    return redirect('payments:child', case_id=case_id)


@login_required
@transaction.atomic
def submit_payment_document(request, case_id):
    user = request.user
    case = get_object_or_404(Case, id=case_id)

    # Determine if the user is a parent
    is_parent = case.parent_cases.filter(parent=user).exists()

    categories = Category.objects.order_by('type', 'name')
    grouped_categories = {}
    for category in categories:
        if category.type not in grouped_categories:
            grouped_categories[category.type] = []
        grouped_categories[category.type].append(category)

    if request.method == 'POST':
        if is_parent:
            form = PaymentDocumentForm(request.POST, request.FILES)
        else:
            form = PaymentDocumentForm(request.POST, request.FILES, parent_choices=get_parent_choices(case))

        new_category_name = request.POST.get('new_category_name', '').strip()

        if form.is_valid():
            payment_document = form.save(commit=False)
            payment_document.case = case
            payment_document.status = 'validated'

            if is_parent:
                payment_document.user = user
            else:
                parent_user_id = form.cleaned_data.get('parent')
                if parent_user_id:
                    payment_document.user = get_user_model().objects.get(id=parent_user_id)
                else:
                    # Handle case where parent_user_id is not provided or invalid
                    payment_document.user = None

            if new_category_name:
                other_type, created = CategoryType.objects.get_or_create(name='Autre')
                new_category, created = Category.objects.get_or_create(
                    name=new_category_name,
                    defaults={'type': other_type}
                )
                payment_document.category = new_category

            payment_document.save()
            return redirect('payments:payment-history', case_id=case_id)
    else:
        if is_parent:
            form = PaymentDocumentForm()
        else:
            form = PaymentDocumentForm(parent_choices=get_parent_choices(case))

    context = {
        'form': form,
        'grouped_categories': grouped_categories,
        'case': case,
    }

    return render(request, 'payments/submit_payment_document.html', context)


@login_required
def delete_payment(request, payment_id, case_id, category_id):
    payment = get_object_or_404(Document, id=payment_id)
    case = get_object_or_404(Case, id=case_id)

    if request.user == case.parent1 or request.user == case.parent2:
        if request.user != payment.user:
            raise PermissionDenied
    elif not request.user.is_staff:
        raise PermissionDenied

    payment.delete()
    return redirect('payments:category-payments', case_id=case_id, category_id=category_id)


# PARENT
# ----------------------------------------------------------------------------------------------------------------------

@login_required
def create_draft_case(request):
    if request.user.role != 'parent':
        return redirect('accounts:login')

    existing_drafts_count = Case.objects.filter(parent1=request.user, draft=True).count()
    if existing_drafts_count >= 3:
        messages.error(request, "You can only have up to 3 draft cases.")
        return redirect('payments:list_case')

    draft_case = Case.objects.create(parent1=request.user, draft=True)

    return redirect('payments:payment-history', case_id=draft_case.id)


@login_required
def combine_drafts(request):
    if request.user.role not in ['administrator', 'lawyer']:
        return redirect('login')

    draft1_id = request.GET.get('draft1')
    draft1 = None
    if draft1_id:
        draft1 = get_object_or_404(Case, id=draft1_id, draft=True)

    if request.method == 'POST':
        form = CombineDraftsForm(request.POST, user=request.user, initial_draft1=draft1)
        if form.is_valid():
            draft1 = form.cleaned_data['draft1']
            draft2 = form.cleaned_data['draft2']

            if draft1.parent1 == draft2.parent1:
                messages.error(request, "Cannot combine drafts of the same parent.")
                return redirect('combine_drafts')

            draft1.parent2 = draft2.parent1
            draft1.draft = False
            draft1.save()

            for document in draft2.payment_documents.all():
                document.case = draft1
                document.save()

            draft2.delete()

            messages.success(request, "Drafts have been combined successfully.")
            return redirect('payments:payment-history', case_id=draft1.id)
    else:
        form = CombineDraftsForm(user=request.user, initial_draft1=draft1)
        form.fields['draft1'].initial = draft1
        form.fields['draft1'].queryset = Case.objects.filter(id=draft1.id)

    return render(request, 'payments/combine_drafts.html', {'form': form})


# MAGISTRATE
# ----------------------------------------------------------------------------------------------------------------------
def get_parent_choices(case):
    # Retrieve parent cases from the case in question
    parent_cases = case.parent_cases.all()

    # Initialize an empty list for choices
    choices = []

    # Retrieve parent details and prepare choices
    for parent_case in parent_cases:
        parent = parent_case.parent
        choices.append((parent.id, f"{parent.first_name} {parent.last_name}"))

    return choices


@login_required
def create_case(request):
    if not request.user.is_authenticated or (request.user.role != 'lawyer' and request.user.role != 'administrator'):
        # Redirect to login page if user is not logged in or is not a lawyer or administrator
        return redirect('accounts:login')

    if request.method == 'POST':
        form = CaseForm(request.POST, user=request.user)
        if form.is_valid():
            parent1 = form.cleaned_data['parent1']
            parent2 = form.cleaned_data['parent2']
            # Check if a case with the same parent1 and parent2 already exists
            existing_case = Case.objects.filter(
                parent_cases__parent=parent1
            ).filter(
                parent_cases__parent=parent2
            ).exists() or Case.objects.filter(
                parent_cases__parent=parent2
            ).filter(
                parent_cases__parent=parent1
            ).exists()

            if parent1 == parent2:
                messages.error(request, "Impossible de créer un dossier avec le même parent.")
            elif existing_case:
                messages.error(request, "Un dossier avec ces deux parents existe déjà.")
            else:
                case = form.save(commit=False)
                if request.user.role == 'administrator':
                    case.lawyer = form.cleaned_data['lawyer']
                else:
                    case.lawyer = request.user
                case.save()

                # Create AvocatCase entry
                AvocatCase.objects.create(
                    avocat=case.lawyer,
                    case=case
                )

                # Create ParentCase entries
                ParentCase.objects.create(case=case, parent=parent1, percentage=50)
                if parent2:
                    ParentCase.objects.create(case=case, parent=parent2, percentage=50)

                # Redirect to a list of cases or other success page
                return redirect('payments:list_case')
    else:
        form = CaseForm(initial={'parent1': request.user}, user=request.user)  # Initialiser avec l'utilisateur connecté par défaut

    return render(request, 'payments/create_case.html', {'form': form})


@login_required
def pending_payments(request, case_id):
    case = get_object_or_404(Case, id=case_id)
    payments = Document.objects.filter(case=case, status='pending')

    if request.method == 'POST':
        action = request.POST.get('action')
        payment_ids_string = request.POST.get('payments')  # Récupérer la chaîne des IDs de paiements
        payment_ids = payment_ids_string.split(',')  # Séparer la chaîne en une liste d'IDs

        for payment_id in payment_ids:
            payment_id = payment_id.strip()  # Enlever les espaces autour de chaque ID
            if payment_id:
                payment = get_object_or_404(Document, id=int(payment_id))
                if action == 'validate':
                    payment.status = 'validated'
                elif action == 'reject':
                    payment.status = 'rejected'
                payment.save()

        return redirect('payments:pending-payments', case_id=case_id)

    context = {
        'case': case,
        'payments': payments,
    }
    return render(request, 'payments/pending_payments.html', context)


@login_required
def add_juge_avocat(request, case_id):
    case = get_object_or_404(Case, id=case_id)

    # Obtenez les utilisateurs déjà liés au dossier
    existing_judges = JugeCase.objects.filter(case=case).select_related('juge')
    existing_lawyers = AvocatCase.objects.filter(case=case).select_related('avocat')

    # Obtenez les IDs des utilisateurs déjà liés au dossier
    existing_judge_ids = existing_judges.values_list('juge_id', flat=True)
    existing_lawyer_ids = existing_lawyers.values_list('avocat_id', flat=True)

    # Exclure les utilisateurs déjà associés et l'utilisateur actuel
    available_judges = User.objects.filter(role='judge').exclude(
        id__in=existing_judge_ids
    ).exclude(id=request.user.id)

    available_lawyers = User.objects.filter(role='lawyer').exclude(
        id__in=existing_lawyer_ids
    ).exclude(id=request.user.id)

    if request.method == 'POST':
        form = AddJugeAvocatForm(request.POST)
        form.set_juges_queryset(available_judges)
        form.set_avocats_queryset(available_lawyers)
        if form.is_valid():
            juges = form.cleaned_data.get('juges')
            avocats = form.cleaned_data.get('avocats')

            # Ajouter les juges sélectionnés
            for juge in juges:
                JugeCase.objects.get_or_create(
                    juge=juge,
                    case=case
                )

            # Ajouter les avocats sélectionnés
            for avocat in avocats:
                AvocatCase.objects.get_or_create(
                    avocat=avocat,
                    case=case
                )

            return redirect('payments:add-juge-avocat', case_id=case.id)
    else:
        form = AddJugeAvocatForm(initial={'case': case.id})
        form.set_juges_queryset(available_judges)
        form.set_avocats_queryset(available_lawyers)

    context = {
        'form': form,
        'case': case,
        'existing_judges': [j.juge for j in existing_judges],
        'existing_lawyers': [a.avocat for a in existing_lawyers],
    }

    return render(request, 'payments/add_juge_avocat.html', context)


def remove_juge(request, case_id, juge_id):
    case = get_object_or_404(Case, id=case_id)
    juge = get_object_or_404(User, id=juge_id, role='judge')
    JugeCase.objects.filter(case=case, juge=juge).delete()
    return redirect('payments:add-juge-avocat', case_id=case.id)


def remove_avocat(request, case_id, avocat_id):
    case = get_object_or_404(Case, id=case_id)
    avocat = get_object_or_404(User, id=avocat_id, role='lawyer')
    AvocatCase.objects.filter(case=case, avocat=avocat).delete()
    return redirect('payments:add-juge-avocat', case_id=case.id)


@method_decorator(login_required, name='dispatch')
class DraftCaseListView(ListView):
    model = Case
    template_name = 'payments/list_draft_case.html'
    context_object_name = 'draft_cases'

    def get_queryset(self):
        user = self.request.user
        if user.role in ['administrator', 'lawyer']:
            return Case.objects.filter(draft=True).order_by('parent_cases__parent__email')
        else:
            return Case.objects.none()


    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in ['administrator', 'lawyer']:
            return HttpResponseForbidden("You do not have permission to access this view.")
        return super().dispatch(request, *args, **kwargs)


@login_required
def convert_draft_case(request, case_id):
    case = get_object_or_404(Case, pk=case_id)

    if request.user.role not in ['administrator', 'lawyer']:
        return HttpResponseForbidden("You do not have permission to access this case.")

    if request.method == 'POST':
        form = ConvertDraftCaseForm(request.POST, instance=case)
        if form.is_valid():
            case = form.save(commit=False)
            case.draft = False
            case.save()
            messages.success(request, "Draft case has been converted to a regular case.")
            return redirect('payments:payment-history', case_id=case.id)
    else:
        form = ConvertDraftCaseForm(instance=case)

    return render(request, 'payments/convert_draft_case.html', {'form': form, 'case': case})


@require_POST
def update_percentages(request, case_id):
    case = get_object_or_404(Case, pk=case_id)

    # Mettez à jour les pourcentages des parents
    parent1_percentage = float(request.POST.get('parent1_percentage', 0))
    parent2_percentage = float(request.POST.get('parent2_percentage', 0))

    # Mettez à jour les objets ParentCase associés
    parent_cases = case.parent_cases.all().order_by('id')
    if len(parent_cases) > 0:
        parent_cases[0].percentage = parent1_percentage
        parent_cases[0].save()
    if len(parent_cases) > 1:
        parent_cases[1].percentage = parent2_percentage
        parent_cases[1].save()

    return redirect('payments:payment-history', case_id=case_id)


# ADMINISTRATOR
# ----------------------------------------------------------------------------------------------------------------------
@login_required
def index_payments(request):
    if request.user.role != 'administrator':
        return redirect('home')  # Redirect to an appropriate page if the user is not an administrator

    current_year = timezone.now().year
    indexations = IndexHistory.objects.all()

    if request.method == 'POST':
        form = IndexPaymentForm(request.POST)
        if form.is_valid():
            indices = form.cleaned_data['indices']
            confirm_indexation_list = request.POST.getlist('confirm_indexation')
            confirm_indexation = confirm_indexation_list[0] == 'true' if confirm_indexation_list else False

            existing_index = IndexHistory.objects.filter(year=current_year).exists()

            if existing_index and not confirm_indexation:
                return render(request, 'payments/index_payments.html', {
                    'form': form,
                    'indexations': indexations,
                    'confirm_required': True
                })
            else:
                # Récupère le dernier montant et indice de l'entrée la plus récente
                last_index = IndexHistory.objects.order_by('-created_at').first()

                if last_index:
                    previous_indice = Decimal(last_index.indices)
                    previous_amount = Decimal(last_index.amount)
                    multiplier = Decimal(indices) / previous_indice
                    new_amount = (previous_amount * multiplier).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                else:
                    new_amount = Decimal('0.00')

                # Crée une nouvelle entrée dans IndexHistory pour l'année en cours
                IndexHistory.objects.create(year=current_year, indices=indices, amount=new_amount)

                messages.success(request, f"Les contributions alimentaires ont été indexées par {indices}%.")
                return redirect('payments:index_payments')
    else:
        form = IndexPaymentForm()

    confirm_required = IndexHistory.objects.filter(year=current_year).exists()

    return render(request, 'payments/index_payments.html', {
        'form': form,
        'indexations': indexations,
        'confirm_required': confirm_required
    })


@login_required
def delete_indexation(request, index_id):
    if request.user.role != 'administrator':
        return redirect('home')  # Redirect to an appropriate page if the user is not an administrator

    indexation = get_object_or_404(IndexHistory, id=index_id)
    current_year = timezone.now().year
    percentage = indexation.indices

    if request.method == 'POST':
        # Reverser l'indexation
        multiplier = 1 / (1 + (percentage / 100))
        Document.objects.all().update(amount=F('amount') * multiplier)

        # Supprimer l'indexation
        indexation.delete()
        messages.success(request, f"Indexation for the year {indexation.year} has been deleted.")
        return redirect('payments:index_payments')

    return render(request, 'payments/delete_indexation_confirm.html', {'indexation': indexation})
