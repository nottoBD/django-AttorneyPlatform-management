from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from payments.models import Case
from .models import AvocatCase, JugeCase
from .validations import (
    clean_email, validate_image, sanitize_text, validate_national_number,
    validate_password, validate_telephone
)

User = get_user_model()


class UserUpdateForm(forms.ModelForm):
    current_cases = forms.ModelMultipleChoiceField(
        queryset=Case.objects.none(),
        required=False,
        label=_("Current Cases")
    )

    assigned_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False,
        label=_("Assigned Users")
    )

    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'email', 'profile_image', 'current_cases', 'assigned_users', 'is_active']

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)
        target_user = self.instance

        if self.request_user.is_administrator or self.request_user.is_superuser:
            self._setup_admin_superuser_form(target_user)
        elif self.request_user.is_lawyer() or self.request_user.is_judge():
            self._setup_lawyer_judge_form(target_user)
        elif self.request_user.is_parent:
            self._setup_parent_form(target_user)

    def clean_email(self):
        return clean_email(self.cleaned_data.get('email'))

    def clean_first_name(self):
        return sanitize_text(self.cleaned_data.get('first_name'))

    def clean_last_name(self):
        return sanitize_text(self.cleaned_data.get('last_name'))

    def clean_profile_image(self):
        profile_image = self.cleaned_data.get('profile_image')
        return validate_image(profile_image) if profile_image else None

    def clean_is_active(self):
        is_active = self.cleaned_data.get('is_active', self.instance.is_active)
        if 'is_active' in self.changed_data:
            if not self.request_user.is_superuser and not self.request_user.is_administrator:
                raise forms.ValidationError(_("You are not authorized to change the active status."))
        return is_active


    def _setup_admin_superuser_form(self, target_user):
        # Admin viewing their own profile
        if self.request_user == target_user:
            self.fields.pop('current_cases', None)
            self.fields.pop('assigned_users', None)
            self.fields.pop('is_active', None)
        # Admin viewing a parent profile
        elif target_user.role == 'parent':
            assigned_users = User.objects.filter(
                id__in=AvocatCase.objects.filter(case__in=Case.objects.filter(parent1=target_user) | Case.objects.filter(parent2=target_user)).values_list('avocat', flat=True)
            ) | User.objects.filter(
                id__in=JugeCase.objects.filter(case__in=Case.objects.filter(parent1=target_user) | Case.objects.filter(parent2=target_user)).values_list('juge', flat=True)
            )
            self.fields['assigned_users'].queryset = assigned_users
            self.fields.pop('current_cases', None)
        # Admin viewing a judge or lawyer profile
        elif target_user.role in ['judge', 'lawyer']:
            self.fields['current_cases'].queryset = self._get_current_cases(target_user)
            self.fields.pop('assigned_users', None)
        else:
            self.fields.pop('current_cases', None)
            self.fields.pop('assigned_users', None)
    
    def _setup_lawyer_judge_form(self, target_user):
        # Lawyer or Judge viewing their own profile
        if self.request_user == target_user:
            self.fields['current_cases'].queryset = self._get_current_cases(target_user)
            self.fields.pop('assigned_users', None)
        # Lawyer or Judge viewing a parent profile they are assigned to
        elif target_user.role == 'parent' and self._user_assigned_to_case(target_user):
            assigned_users = User.objects.filter(
                id__in=AvocatCase.objects.filter(case__in=Case.objects.filter(parent1=target_user) | Case.objects.filter(parent2=target_user)).values_list('avocat', flat=True)
            ) | User.objects.filter(
                id__in=JugeCase.objects.filter(case__in=Case.objects.filter(parent1=target_user) | Case.objects.filter(parent2=target_user)).values_list('juge', flat=True)
            )
            self.fields['assigned_users'].queryset = assigned_users
            self.fields.pop('current_cases', None)
        else:
            self.fields.pop('current_cases', None)
            self.fields.pop('assigned_users', None)

    def _setup_parent_form(self, target_user):
        # Parent viewing their own profile
        if self.request_user == target_user:
            assigned_users = User.objects.filter(
                id__in=AvocatCase.objects.filter(case__in=Case.objects.filter(parent1=target_user) | Case.objects.filter(parent2=target_user)).values_list('avocat', flat=True)
            ) | User.objects.filter(
                id__in=JugeCase.objects.filter(case__in=Case.objects.filter(parent1=target_user) | Case.objects.filter(parent2=target_user)).values_list('juge', flat=True)
            )
            self.fields['assigned_users'].queryset = assigned_users
            self.fields.pop('current_cases', None)
        else:
            self.fields.pop('current_cases', None)
            self.fields.pop('assigned_users', None)

    def _get_current_cases(self, user):
        if user.role == 'lawyer':
            return Case.objects.filter(assigned_lawyers__avocat=user)
        elif user.role == 'judge':
            return Case.objects.filter(assigned_judges__juge=user)
        return Case.objects.none()

    def _user_assigned_to_case(self, user):
        if self.request_user.role == 'lawyer':
            return AvocatCase.objects.filter(avocat=self.request_user, case__in=self._parent_cases(user)).exists()
        elif self.request_user.role == 'judge':
            return JugeCase.objects.filter(juge=self.request_user, case__in=self._parent_cases(user)).exists()
        return False

    def _parent_cases(self, user):
        return Case.objects.filter(parent1=user) | Case.objects.filter(parent2=user)


class JusticeRegistrationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('judge', 'Judge'),
        ('lawyer', 'Attorney'),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Role")
    first_name = forms.CharField(max_length=30, label=_('First Name'), required=True)
    last_name = forms.CharField(max_length=150, label=_('Last Name'), required=True)
    num_telephone = forms.CharField(max_length=20, initial='+32', label=_('Telephone Number'), required=False)

    class Meta:
        model = User
        fields = ['role', 'last_name', 'first_name', 'email', 'password1', 'password2', 'num_telephone']

    def __init__(self, *args, **kwargs):
        super(JusticeRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        return sanitize_text(first_name)

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        return sanitize_text(last_name)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        return clean_email(email)

    def clean_num_telephone(self):
        telephone = self.cleaned_data.get('num_telephone', '')
        if telephone == '+32':
            return ''
        return validate_telephone(telephone)

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        return validate_password(password1)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.telephone = self.cleaned_data['num_telephone']
        user.is_staff = True
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
            self.save_m2m()
        return user

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["national_number", "last_name", "first_name", "email", "date_of_birth", "address",
                  "telephone", "password1", "password2"]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'})
        }

    national_number = forms.CharField(max_length=15, required=False, label=_("National Number"))
    last_name = forms.CharField(max_length=35, required=True, label=_("Last Name"))
    first_name = forms.CharField(max_length=25, required=True, label=_("First Name"))
    telephone = forms.CharField(max_length=13, required=False, label=_("Telephone"), initial='+32')
    address = forms.CharField(widget=forms.TextInput, required=False, label=_("Address"), max_length=70)

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['date_of_birth'].widget.format = '%d/%m/%Y'
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

    def clean_national_number(self):
        national_number = self.cleaned_data.get('national_number', '')
        unformatted_number = ''.join(filter(str.isdigit, national_number))
        return validate_national_number(unformatted_number)

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '')
        return sanitize_text(first_name)

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '')
        return sanitize_text(last_name)

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        return clean_email(email)

    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone', '')
        if telephone == '+32':
            return ''
        return validate_telephone(telephone)

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1', '')
        return validate_password(password1)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError(_('The passwords do not match.'))
        return password2


class DeletionRequestForm(forms.Form):
    confirm = forms.BooleanField(label="Confirm deletion request")


class CancelDeletionForm(forms.Form):
    confirm = forms.BooleanField(label="Confirm cancellation of deletion request")
