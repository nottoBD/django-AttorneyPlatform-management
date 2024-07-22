from datetime import datetime
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Sum, Q, F
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.text import capfirst
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from xhtml2pdf import pisa

from .forms import PaymentDocumentForm, FolderForm, PaymentDocumentFormLawyer, IndexPaymentForm
from .models import Document, Folder, Category, CategoryType, IndexHistory

User = get_user_model()


# EVERYONE
#----------------------------------------------------------------------------------------------------------------------
class FolderListView(LoginRequiredMixin, ListView):
    model = Folder
    template_name = 'payments/list_folder.html'
    context_object_name = 'folders'

    def get_queryset(self):
        user = self.request.user

        if user.role == 'parent':
            # Filter cases by user logged in as a parent
            return Folder.objects.filter(Q(parent1=user) | Q(parent2=user))
        elif user.role in ['judge', 'lawyer']:
            # Filter cases by user logged in as judge or lawyer
            return Folder.objects.filter(Q(judge=user) | Q(lawyer=user))
        else:
            # Default to an empty queryset if user's role is undefined
            return Folder.objects.none()


class PaymentHistoryView(LoginRequiredMixin, ListView):
    model = Document
    template_name = 'payments/folder_payment_history.html'
    context_object_name = 'payments'

    def dispatch(self, request, *args, **kwargs):
        folder_id = kwargs.get('folder_id')

        if folder_id:
            # Vérifiez que le dossier avec cet ID existe
            self.folder = get_object_or_404(Folder, pk=folder_id)
        else:
            # Si folder_id est requis mais non fourni, gérer le cas ici
            return self.handle_no_folder_id()

        # Assurez-vous que l'utilisateur a accès au dossier
        if not self.user_has_access_to_folder(request.user, self.folder):
            return self.handle_no_access()

        # Appeler la méthode dispatch parent pour continuer le traitement
        return super().dispatch(request, *args, **kwargs)

    def handle_no_folder_id(self):
        # Gérer le cas où folder_id est requis mais non fourni
        return HttpResponseNotFound("Folder ID is required but was not provided.")

    def handle_no_access(self):
        # Gérer le cas où l'utilisateur n'a pas accès au dossier
        return HttpResponseForbidden("You do not have permission to access this folder.")

    def user_has_access_to_folder(self, user, folder):
        # Exemple de vérification des permissions, à ajuster selon vos besoins
        return folder.parent1 == user or folder.parent2 == user or user.role == "lawyer" or user.role == "judge"

    def get_queryset(self):
        queryset = Document.objects.filter(folder=self.folder)
        selected_year = self.request.GET.get('year')
        selected_quarter = self.request.GET.get('quarter')

        if selected_year and selected_quarter:
            try:
                selected_year = int(selected_year)
                selected_quarter = int(selected_quarter)

                start_month = (selected_quarter - 1) * 3 + 1
                end_month = start_month + 2

                start_date = datetime(selected_year, start_month, 1)
                end_date = datetime(selected_year, end_month + 1, 1) if end_month < 12 else datetime(selected_year + 1, 1, 1)

                queryset = queryset.filter(date__gte=start_date, date__lt=end_date)
            except (TypeError, ValueError):
                queryset = Document.objects.filter(folder=self.folder)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['folder_id'] = self.folder.id
        context['categories'] = Category.objects.all()
        folder = self.folder
        parent1 = folder.parent1
        parent2 = folder.parent2
        user = self.request.user

        selected_year = self.request.GET.get('year')
        selected_quarter = self.request.GET.get('quarter')

        if selected_year and selected_quarter:
            try:
                parent1_valid_payments = Document.objects.filter(
                    folder=folder, user=parent1, category__type__isnull=False, status='validated', date__year=selected_year,
                    date__quarter=selected_quarter
                ).values('category__type', 'category').annotate(total_amount=Sum('amount'))
                parent2_valid_payments = Document.objects.filter(
                    folder=folder, user=parent2, category__type__isnull=False, status='validated', date__year=selected_year,
                    date__quarter=selected_quarter
                ).values('category__type', 'category').annotate(total_amount=Sum('amount'))

                parent1_pending_payments = Document.objects.filter(
                    folder=folder, user=parent1, category__type__isnull=False, status='pending', date__year=selected_year,
                    date__quarter=selected_quarter
                ).values('category__type', 'category').annotate(total_amount=Sum('amount'))
                parent2_pending_payments = Document.objects.filter(
                    folder=folder, user=parent2, category__type__isnull=False, status='pending', date__year=selected_year,
                    date__quarter=selected_quarter
                ).values('category__type', 'category').annotate(total_amount=Sum('amount'))
            except (TypeError, ValueError):
                parent1_valid_payments = []
                parent2_valid_payments = []
                parent1_pending_payments = []
                parent2_pending_payments = []
        else:
            parent1_valid_payments = Document.objects.filter(
                folder=folder, user=parent1, category__type__isnull=False, status='validated'
            ).values('category__type', 'category').annotate(total_amount=Sum('amount'))
            parent2_valid_payments = Document.objects.filter(
                folder=folder, user=parent2, category__type__isnull=False, status='validated'
            ).values('category__type', 'category').annotate(total_amount=Sum('amount'))

            parent1_pending_payments = Document.objects.filter(
                folder=folder, user=parent1, category__type__isnull=False, status='pending'
            ).values('category__type', 'category').annotate(total_amount=Sum('amount'))
            parent2_pending_payments = Document.objects.filter(
                folder=folder, user=parent2, category__type__isnull=False, status='pending'
            ).values('category__type', 'category').annotate(total_amount=Sum('amount'))

        parent1_valid_payments_dict = {(payment['category__type'], payment['category']): payment['total_amount'] for
                                       payment in parent1_valid_payments}
        parent2_valid_payments_dict = {(payment['category__type'], payment['category']): payment['total_amount'] for
                                       payment in parent2_valid_payments}
        parent1_pending_dict = {(payment['category__type'], payment['category']): payment['total_amount'] for payment in
                                parent1_pending_payments}
        parent2_pending_dict = {(payment['category__type'], payment['category']): payment['total_amount'] for payment in
                                parent2_pending_payments}

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

        payment_years = Document.objects.filter(folder=self.folder).dates('date', 'year')
        years = [year.year for year in payment_years]

        context.update({
            'folder': folder,
            'parent1_user': parent1,
            'parent2_user': parent2,
            'categories_by_type': categories_by_type,
            'parent1_total': parent1_total,
            'parent2_total': parent2_total,
            'total_amount': parent1_total + parent2_total,
            'difference': difference,
            'in_favor_of': in_favor_of,
            'years': years,
            'selected_year': selected_year,
            'selected_quarter': selected_quarter,
            'category_ids': category_ids,
        })

        payments_with_permissions = [
            {
                'payment': payment,
                'can_delete': payment.user_can_delete(user)
            } for payment in self.get_queryset()
        ]
        context['payments_with_permissions'] = payments_with_permissions

        return context


class CategoryPaymentsView(LoginRequiredMixin, ListView):
    model = Document
    template_name = 'payments/folder_category_history.html'
    context_object_name = 'payments'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs.get('category_id')
        folder_id = self.kwargs.get('folder_id')

        # Vérifier et récupérer la catégorie
        category = get_object_or_404(Category, id=category_id)
        context['category'] = category

        # Obtenir le dossier basé sur le folder_id et les droits d'accès
        folder = get_object_or_404(Folder, id=folder_id)
        context['folder'] = folder

        # Récupérer les paiements pour les parents
        parent1_payments = Document.objects.filter(folder=folder, category_id=category_id, user=folder.parent1)
        parent2_payments = Document.objects.filter(folder=folder, category_id=category_id, user=folder.parent2)

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
        context['parent1_name'] = folder.parent1.get_full_name()
        context['parent2_name'] = folder.parent2.get_full_name()

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
    def get(self, request, folder_id=None, *args, **kwargs):
        user = self.request.user

        # Vérifier si folder_id est fourni
        if folder_id is None:
            return HttpResponse("No folder_id provided.", status=400)

        folder = get_object_or_404(Folder, id=folder_id)

        # Obtenir les paramètres de la requête GET ou les définir à None si non présents
        selected_year = request.GET.get('year')
        selected_quarter = request.GET.get('quarter')

        if selected_year and selected_year != "None":
            selected_year = int(selected_year)
        else:
            selected_year = None

        if selected_quarter and selected_quarter != "None":
            selected_quarter = int(selected_quarter)
        else:
            selected_quarter = None

        payment_history_view = PaymentHistoryView()
        payment_history_view.request = request
        payment_history_view.kwargs = {'folder_id': folder_id}  # Passer folder_id comme kwargs

        # Définir self.folder pour payment_history_view avant d'appeler get_queryset
        payment_history_view.folder = folder

        # Appeler dispatch pour initialiser la vue correctement
        payment_history_view.dispatch(request, *args, **kwargs)

        # Obtenir object_list en appelant get_queryset()
        payment_history_view.object_list = payment_history_view.get_queryset()

        # Obtenir le contexte de la vue PaymentHistoryView
        context = payment_history_view.get_context_data()

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


# PARENT
#----------------------------------------------------------------------------------------------------------------------
@login_required
@transaction.atomic
def submit_payment_document(request, folder_id):
    user = request.user
    folder = Folder.objects.filter(Q(parent1=user) | Q(parent2=user))

    # Vérifiez si le dossier demandé existe
    folder = get_object_or_404(folder, id=folder_id)

    categories = Category.objects.order_by('type_id', 'name')
    grouped_categories = {}
    for category in categories:
        if category.type not in grouped_categories:
            grouped_categories[category.type] = []
        grouped_categories[category.type].append(category)

    if request.method == 'POST':
        form = PaymentDocumentForm(request.POST, request.FILES)
        new_category_name = request.POST.get('new_category', '').strip()

        if form.is_valid():
            payment_document = form.save(commit=False)
            payment_document.user = user
            payment_document.folder = folder
            payment_document.status = 'pending'

            if new_category_name:
                other_type, created = CategoryType.objects.get_or_create(name='Autre')
                new_category, created = Category.objects.get_or_create(
                    name=new_category_name,
                    defaults={'type': other_type}
                )
                payment_document.category = new_category

            payment_document.save()
            return redirect('payments:payment-history', folder_id=folder_id)
    else:
        form = PaymentDocumentForm()

    context = {
        'form': form,
        'grouped_categories': grouped_categories,
        'folder': folder,
    }

    return render(request, 'payments/submit_payment_document.html', context)


# MAGISTRATE
#----------------------------------------------------------------------------------------------------------------------
@login_required
@transaction.atomic
def submit_payment_document_lawyer(request, folder_id):
    folder = get_object_or_404(Folder, pk=folder_id)
    categories = Category.objects.order_by('type_id', 'name')

    grouped_categories = {}
    for category in categories:
        if category.type not in grouped_categories:
            grouped_categories[category.type] = []
        grouped_categories[category.type].append(category)

    if request.method == 'POST':
        form = PaymentDocumentFormLawyer(request.POST, request.FILES, parent_choices=get_parent_choices(folder))

        if form.is_valid():
            payment_document = form.save(commit=False)
            payment_document.folder = folder
            parent_user_id = form.cleaned_data['parent']
            payment_document.status = 'validated'  # Assurez-vous de définir le bon statut ici
            payment_document.user = get_user_model().objects.get(id=parent_user_id)
            payment_document.save()
            return redirect(reverse('payments:payment-history', kwargs={'folder_id': folder_id}))
    else:
        form = PaymentDocumentFormLawyer(parent_choices=get_parent_choices(folder))

    return render(request, 'payments/submit_payment_document_lawyer.html', {
        'form': form,
        'folder': folder,
        'grouped_categories': grouped_categories,
    })


def get_parent_choices(folder):
    # Retrieve parent IDs from the folder in question
    parent1_id = folder.parent1_id
    parent2_id = folder.parent2_id

    # Retrieve parents' full names using IDs
    parent1 = get_user_model().objects.get(id=parent1_id)
    parent2 = get_user_model().objects.get(id=parent2_id)

    # Create a wish list using parents' full names
    choices = [
        (parent1.id, f"{parent1.first_name} {parent1.last_name}"),
        (parent2.id, f"{parent2.first_name} {parent2.last_name}")
    ]
    return choices


@login_required
def create_folder(request):
    if not request.user.is_authenticated or request.user.role != 'lawyer':
        # Redirect to login page if user is not a logged in lawyer
        return redirect('login')

    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            parent1 = form.cleaned_data['parent1']
            parent2 = form.cleaned_data['parent2']
            # Check if a folder with the same parent1 and parent2 already exists
            existing_folder = Folder.objects.filter(parent1=parent1, parent2=parent2).exists() or Folder.objects.filter(parent1=parent2, parent2=parent1).exists()
            if existing_folder:
                messages.error(request, "Un dossier avec ces deux parents existe déjà.")
            else:
                folder = form.save(commit=False)
                folder.lawyer = request.user
                folder.save()
                # Redirect to a list of folders or other success page
                return redirect('payments:list_folder')
    else:
        form = FolderForm(initial={'parent1': request.user})  # Initialiser avec l'utilisateur connecté par défaut
        form.fields['parent1'].queryset = form.fields['parent1'].queryset
        form.fields['parent2'].queryset = form.fields['parent2'].queryset

    return render(request, 'payments/create_folder.html', {'form': form})


@login_required
def pending_payments(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)
    payments = Document.objects.filter(folder=folder, status='pending')

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

        return redirect('payments:pending-payments', folder_id=folder_id)

    context = {
        'folder': folder,
        'payments': payments,
    }
    return render(request, 'payments/pending_payments.html', context)


# ADMINISTRATOR
#----------------------------------------------------------------------------------------------------------------------
@login_required
def index_payments(request):
    if request.user.role != 'administrator':
        return redirect('home')  # Redirect to an appropriate page if the user is not an administrator

    current_year = timezone.now().year
    indexations = IndexHistory.objects.all()

    if request.method == 'POST':
        form = IndexPaymentForm(request.POST)
        if form.is_valid():
            percentage = form.cleaned_data['percentage']
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
                multiplier = 1 + (percentage / 100)
                Document.objects.all().update(amount=F('amount') * multiplier)

                # Create a new entry in IndexHistory for the current year
                IndexHistory.objects.create(year=current_year, percentage=percentage)

                messages.success(request, f"All payments have been indexed by {percentage}%.")
                return redirect('payments:index_payments')
    else:
        form = IndexPaymentForm()

    confirm_required = IndexHistory.objects.filter(year=current_year).exists()

    return render(request, 'payments/index_payments.html',
                  {'form': form, 'indexations': indexations, 'confirm_required': confirm_required})


@login_required
def delete_indexation(request, index_id):
    if request.user.role != 'administrator':
        return redirect('home')  # Redirect to an appropriate page if the user is not an administrator

    indexation = get_object_or_404(IndexHistory, id=index_id)
    current_year = timezone.now().year
    percentage = indexation.percentage

    if request.method == 'POST':
        # Reverser l'indexation
        multiplier = 1 / (1 + (percentage / 100))
        Document.objects.all().update(amount=F('amount') * multiplier)

        # Supprimer l'indexation
        indexation.delete()
        messages.success(request, f"Indexation for the year {indexation.year} has been deleted.")
        return redirect('payments:index_payments')

    return render(request, 'payments/delete_indexation_confirm.html', {'indexation': indexation})
