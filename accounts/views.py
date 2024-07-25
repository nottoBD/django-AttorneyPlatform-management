from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
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

from payments.models import Case
from .forms import JusticeRegistrationForm, UserRegisterForm, UserUpdateForm, CancelDeletionForm, DeletionRequestForm
from .models import User, AvocatCase, JugeCase

User = get_user_model()

logger = logging.getLogger(__name__)


class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    template_name = 'accounts/user_update.html'
    form_class = UserUpdateForm
    success_url = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        if not self.request.user.is_superuser and 'role' in form.changed_data:
            form.add_error('role', _("You are not authorized to change the role."))
            return self.form_invalid(form)

        user = form.save(commit=False)
        user.is_active = form.cleaned_data.get('is_active', False)
        user.save()

        if 'related_users' in form.cleaned_data:
            related_users_ids = form.cleaned_data['related_users'].values_list('id', flat=True)
            related_users_ids = set(related_users_ids)
            if self.object.role == 'parent':
                form._handle_parent_relationships(related_users_ids)
            elif self.object.role in ['lawyer', 'judge']:
                form._handle_lawyer_judge_relationships(related_users_ids)

        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        if 'deassign' in request.POST:
            return self.deassign_user()
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request_user'] = self.request.user
        return kwargs

    def test_func(self):
        user_to_update = self.get_object()
        if self.request.user == user_to_update:
            return True
        if self.request.user.is_superuser:
            return True
        if self.request.user.role == 'lawyer':
            return AvocatCase.objects.filter(avocat=self.request.user, case__parent1=user_to_update).exists() or \
                AvocatCase.objects.filter(avocat=self.request.user, case__parent2=user_to_update).exists()
        if self.request.user.role == 'judge':
            return JugeCase.objects.filter(juge=self.request.user, case__parent1=user_to_update).exists() or \
                JugeCase.objects.filter(juge=self.request.user, case__parent2=user_to_update).exists()
        if self.request.user.is_administrator:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.role == 'parent':
            parent_cases = Case.objects.filter(parent1=self.request.user) | Case.objects.filter(parent2=self.request.user)
            lawyer_ids = AvocatCase.objects.filter(case__in=parent_cases).values_list('avocat_id', flat=True)
            judge_ids = JugeCase.objects.filter(case__in=parent_cases).values_list('juge_id', flat=True)
            context['assigned_users'] = User.objects.filter(id__in=set(lawyer_ids).union(set(judge_ids)))
        return context

    def deassign_user(self):
        user_to_update = self.get_object()
        if self.request.user.role == 'lawyer':
            relationships = AvocatCase.objects.filter(avocat=self.request.user, case__parent1=user_to_update) | AvocatCase.objects.filter(avocat=self.request.user, case__parent2=user_to_update)
        elif self.request.user.role == 'judge':
            relationships = JugeCase.objects.filter(juge=self.request.user, case__parent1=user_to_update) | JugeCase.objects.filter(juge=self.request.user, case__parent2=user_to_update)
        elif self.request.user.is_administrator:
            relationships = AvocatCase.objects.filter(case__parent1=user_to_update) | AvocatCase.objects.filter(case__parent2=user_to_update) | \
                            JugeCase.objects.filter(case__parent1=user_to_update) | JugeCase.objects.filter(case__parent2=user_to_update)
        else:
            messages.error(self.request, _("You are not authorized to deassign this user."))
            return redirect('accounts:user_update', pk=user_to_update.pk)

        if relationships.exists():
            relationships.delete()
            messages.success(self.request, _("You have been deassigned from this case."))
            return redirect('accounts:user_list')
        else:
            messages.error(self.request, _("You are not assigned to this case."))
            return redirect('accounts:user_update', pk=user_to_update.pk)


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
            parents_query = User.objects.filter(role='parent').prefetch_related('avocats_assigned__avocat',
                                                                                'juges_assigned__juge')

            if is_active is not None:
                magistrates_query = magistrates_query.filter(is_active=is_active)
                parents_query = parents_query.filter(is_active=is_active)

            context['magistrates'] = magistrates_query.annotate(
                parents_count=Count('assigned_parents') + Count('assigned_parents_judge'))

            if self.request.user.role == 'lawyer':
                context['parents_filtered'] = parents_query.filter(
                    avocats_assigned__avocat=self.request.user).distinct()
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


@login_required
@permission_required('accounts.add_user', raise_exception=True)
@user_passes_test(lambda u: u.is_superuser, login_url='/login/')
def register_magistrate(request):
    if request.method == 'POST':
        form = JusticeRegistrationForm(request.POST)
        if form.is_valid():
            magistrate = form.save()
            messages.success(request, _('Attorney registered successfully.' % magistrate.email))
            return redirect(reverse('accounts:user_list'))
    else:
        form = JusticeRegistrationForm()
    return render(request, 'registration/register_magistrate.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'parent'
            user.national_number_raw = form.cleaned_data['national_number'].replace('.', '').replace('-', '')
            user.save()

            if request.user.is_authenticated:
                if request.user.role == 'lawyer':
                    AvocatCase.objects.create(avocat=request.user, parent=user)
                elif request.user.role == 'judge':
                    JugeCase.objects.create(juge=request.user, parent=user)

            messages.success(request, _("The parent account has been successfully created."))
            return redirect('/accounts/list/')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})


class UserOrSuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (user == self.request.user or user.is_superuser)


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'registration/password_reset.html'
    email_template_name = 'registration/password_reset_mail.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_message = _("We've emailed you instructions for setting your password, if an account exists with the "
                        "email you entered. You should receive them shortly. If you don't receive an email, "
                        "please make sure you've entered the address you registered with, and check your spam case.")
    success_url = reverse_lazy('home')


class PasswordResetConfirmationView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirmation.html'
    post_reset_login = False
    success_url = reverse_lazy('accounts:login')


@login_required
def request_deletion(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.user != user or user.is_superuser:
        if user.is_superuser:
            messages.error(request, _('You are not authorized to delete this account.'))
            return redirect('accounts:user_update', pk=user.pk)

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
    if request.user != user and not request.user.is_superuser:
        messages.error(request, _('You are not authorized to cancel the deletion of this account.'))
        return redirect('user_update', pk=user.pk)
    if user.is_superuser:
        messages.error(request, _('You cannot cancel deletion for an administrator account.'))
        return redirect('accounts:user_update', pk=user.pk)

    if request.method == 'POST':
        form = CancelDeletionForm(request.POST)
        if form.is_valid():
            user.cancel_deletion()
            messages.success(request, _('Account deletion request cancelled successfully.'))
            return redirect('home')
    else:
        form = CancelDeletionForm()
    return render(request, 'accounts/cancel_deletion.html', {'form': form})


@login_required
@user_passes_test(lambda u: u.is_superuser, login_url='/login/')
def delete_user(request, pk):
    if request.user.is_administrator:
        user_to_delete = get_object_or_404(User, pk=pk)
        user_to_delete.delete()
        messages.success(request, _("The user has been deleted successfully."))
    else:
        messages.error(request, _("You are not authorized to delete this user."))
    return redirect('accounts:user_list')
