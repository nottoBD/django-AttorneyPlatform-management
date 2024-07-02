from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import ListView, UpdateView
from pip._internal.utils import logging

from .forms import MagistrateRegistrationForm, UserRegisterForm, UserUpdateForm, CancelDeletionForm, DeletionRequestForm
from .models import User, AvocatParent, JugeParent

User = get_user_model()

logger = logging.getLogger(__name__)

class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'accounts/user_list.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseRedirect(reverse('home'))
        return super().dispatch(request, *args, **kwargs)

    def get_active_status_filter(self):
        is_active_str = self.request.GET.get('is_active')
        if is_active_str is not None:
            return is_active_str.lower() in ['true', '1', 't']
        return None

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                magistrates_list = [{
                    'id': mag.id,
                    'profile_image_url': self.get_image_url(mag),
                    'first_name': mag.first_name,
                    'last_name': mag.last_name,
                    'email': mag.email,
                    'role': mag.role,
                    'parents_count': mag.assigned_parents.count() + mag.assigned_parents_judge.count()
                } for mag in context['magistrates']]

                parents_list = [{
                    'id': parent.id,
                    'profile_image_url': self.get_image_url(parent),
                    'first_name': parent.first_name,
                    'last_name': parent.last_name,
                    'email': parent.email,
                    'avocats_assigned': [
                        avocat.avocat.last_name for avocat in parent.avocats_assigned.all()
                        if avocat.avocat.is_active or not parent.is_active
                    ],
                    'juges_assigned': [
                        juge.juge.last_name for juge in parent.juges_assigned.all()
                        if juge.juge.is_active or not parent.is_active
                    ]
                } for parent in context['parents_filtered']]

                return JsonResponse({'magistrates': magistrates_list, 'parents': parents_list})
            except Exception as e:
                logger.error(f"Error in AJAX response: {e}")
                return JsonResponse({'error': str(e)}, status=500)
        else:
            return super().render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_active = self.get_active_status_filter()

        try:
            magistrates_query = User.objects.filter(
                Q(is_staff=True) | Q(is_superuser=True) | Q(role='administrator') | Q(role='lawyer') | Q(role='judge')
            )
            parents_query = User.objects.filter(role='parent').prefetch_related('avocats_assigned__avocat', 'juges_assigned__juge')

            if is_active is not None:
                magistrates_query = magistrates_query.filter(is_active=is_active)
                parents_query = parents_query.filter(is_active=is_active)

            context['magistrates'] = magistrates_query.annotate(parents_count=Count('assigned_parents') + Count('assigned_parents_judge'))

            if self.request.user.role == 'lawyer':
                context['parents_filtered'] = parents_query.filter(avocats_assigned__avocat=self.request.user).distinct()
            elif self.request.user.role == 'judge':
                context['parents_filtered'] = parents_query.filter(juges_assigned__juge=self.request.user).distinct()
            else:
                context['parents_filtered'] = parents_query

        except Exception as e:
            logger.error(f"Error in context data: {e}")
            context['magistrates'] = []
            context['parents_filtered'] = []

        return context

    def get_image_url(self, user):
        if user.profile_image and hasattr(user.profile_image, 'url'):
            return self.request.build_absolute_uri(user.profile_image.url)
        else:
            return self.request.build_absolute_uri(settings.MEDIA_URL + 'profile_images/default.jpg')


class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    template_name = 'accounts/user_update.html'
    form_class = UserUpdateForm
    success_url = reverse_lazy('accounts:user_list')

    def test_func(self):
        user_to_update = self.get_object()

        if self.request.user == user_to_update:
            return True
        if self.request.user.is_superuser:
            return True
        if self.request.user.role == 'lawyer':
            return AvocatParent.objects.filter(avocat=self.request.user, parent=user_to_update).exists()
        if self.request.user.role == 'judge':
            return JugeParent.objects.filter(juge=self.request.user, parent=user_to_update).exists()
        return False

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request_user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            if 'role' in form.changed_data:
                form.add_error('role', _("You are not authorized to change the role."))
                return self.form_invalid(form)

        response = super().form_valid(form)
        related_users_ids = set(form.cleaned_data.get('related_users').values_list('id', flat=True))

        if self.object.role == 'lawyer':
            relationship_field = 'parent'
            own_field = 'avocat'
            relationship_model = AvocatParent
        elif self.object.role == 'judge':
            relationship_field = 'parent'
            own_field = 'juge'
            relationship_model = JugeParent
        elif self.object.role == 'parent':
            relationship_field = 'juge'
            own_field = 'parent'
            relationship_model = JugeParent
        else:
            return response

        current_relations = set(relationship_model.objects.filter(**{own_field: self.object}).values_list(
            relationship_field + '_id', flat=True))

        relationships_to_add = related_users_ids - current_relations
        relationships_to_remove = current_relations - related_users_ids

        relationship_model.objects.filter(
            **{own_field: self.object, relationship_field + '_id__in': relationships_to_remove}).delete()

        for user_id in relationships_to_add:
            user_instance = User.objects.get(pk=user_id)
            relationship_model.objects.get_or_create(**{
                own_field: self.object,
                relationship_field: user_instance
            })
        return response

    def post(self, request, *args, **kwargs):
        if 'deassign' in request.POST:
            return self.deassign_user()
        return super().post(request, *args, **kwargs)

    def deassign_user(self):
        user_to_update = self.get_object()
        if self.request.user.role == 'lawyer':
            relationship = AvocatParent.objects.filter(avocat=self.request.user, parent=user_to_update)
        elif self.request.user.role == 'judge':
            relationship = JugeParent.objects.filter(juge=self.request.user, parent=user_to_update)
        else:
            messages.error(self.request, _("You are not authorized to deassign this user."))
            return redirect('accounts:user_update', pk=user_to_update.pk)

        if relationship.exists():
            relationship.delete()
            messages.success(self.request, _("You have been deassigned from this parent."))
            return redirect('accounts:user_list')
        else:
            messages.error(self.request, _("You are not assigned to this parent."))
            return redirect('accounts:user_update', pk=user_to_update.pk)

@login_required
@permission_required('accounts.add_user', raise_exception=True)
@user_passes_test(lambda u: u.is_superuser, login_url='/login/')
def register_magistrate(request):
    if request.method == 'POST':
        form = MagistrateRegistrationForm(request.POST)
        if form.is_valid():
            magistrate = form.save()
            messages.success(request, _('Lawyer "%s" registered successfully.' % magistrate.email))
            return redirect(reverse('accounts:user_list'))
    else:
        form = MagistrateRegistrationForm()
    return render(request, 'registration/register_magistrate.html', {'form': form})


@login_required
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'parent'
            user.national_number_raw = form.cleaned_data['national_number']
            formatted_number = (
                    form.cleaned_data['national_number'][:2] + '.' +
                    form.cleaned_data['national_number'][2:4] + '.' +
                    form.cleaned_data['national_number'][4:6] + '-' +
                    form.cleaned_data['national_number'][6:9] + '.' +
                    form.cleaned_data['national_number'][9:]
            )
            user.national_number = formatted_number
            user.save()

            # assigne  parent au lawyer ou judge qui l'inscrit (liste user ne leur montre que les parents dont ils ont le dossier en charge)
            if request.user.role == 'lawyer':
                AvocatParent.objects.create(avocat=request.user, parent=user)
            elif request.user.role == 'judge':
                JugeParent.objects.create(juge=request.user, parent=user)

            messages.success(request, _("The parent account has been successfully created."))
            return redirect('/accounts/list/')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'registration/password_reset.html'
    email_template_name = 'registration/password_reset_mail.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly. " \
                      "If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('home')


class PasswordResetConfirmationView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirmation.html'
    post_reset_login = False
    success_url = reverse_lazy('accounts:login')


@login_required
def request_deletion(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.user != user or user.is_superuser:
        messages.error(request, _('You are not authorized to delete this account.'))
        return redirect('user_update', pk=user.pk)

    if request.method == 'POST':
        form = DeletionRequestForm(request.POST)
        if form.is_valid():
            user.request_deletion()
            messages.success(request, _('Account deletion requested successfully.'))
            return redirect('home')
    else:
        form = DeletionRequestForm()
    return render(request, 'accounts/request_deletion.html', {'form': form})

@login_required
def cancel_deletion(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.user != user:
        messages.error(request, _('You are not authorized to cancel the deletion of this account.'))
        return redirect('user_update', pk=user.pk)

    if request.method == 'POST':
        form = CancelDeletionForm(request.POST)
        if form.is_valid():
            user.cancel_deletion()
            messages.success(request, _('Account deletion request cancelled successfully.'))
            return redirect('home')
    else:
        form = CancelDeletionForm()
    return render(request, 'accounts/cancel_deletion.html', {'form': form})