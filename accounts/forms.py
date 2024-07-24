import re
from PIL import Image
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import AvocatFolder, JugeFolder
from .validations import (
    clean_email, validate_image, sanitize_text, validate_national_number,
    validate_password, validate_telephone
)

User = get_user_model()


class UserUpdateForm(forms.ModelForm):
    related_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False,
        label=_("Assigned Users")
    )

    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'email', 'profile_image', 'related_users', 'is_active']

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)
        target_user = self.instance

        if self.request_user.is_administrator:
            self._setup_admin_form(target_user)
        elif self.request_user.is_lawyer() or self.request_user.is_judge():
            self._setup_lawyer_judge_form(target_user)
        elif self.request_user.is_parent:
            self._setup_parent_form(target_user)

    # les méthodes clean_ sont automatiquements appelées par Django
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
        is_active = self.cleaned_data.get('is_active')
        if 'is_active' in self.changed_data:
            if not self.request_user.is_superuser and not self.request_user.is_administrator:
                raise forms.ValidationError(_("You are not authorized to change the active status."))
        return is_active if is_active else False


    def _setup_admin_form(self, target_user):
        if target_user.role == 'parent':
            queryset = User.objects.filter(role__in=['judge', 'lawyer'])
            self.fields['related_users'].queryset = queryset
            assigned_users = User.objects.filter(
                id__in=AvocatFolder.objects.filter(parent=target_user).values_list('avocat', flat=True)
            ) | User.objects.filter(
                id__in=JugeFolder.objects.filter(parent=target_user).values_list('juge', flat=True)
            )
            self.fields['related_users'].initial = assigned_users
        elif target_user.role in ['judge', 'lawyer']:
            queryset = User.objects.filter(role='parent')
            if target_user.role == 'lawyer':
                assigned_parents = User.objects.filter(
                    id__in=AvocatFolder.objects.filter(avocat=target_user).values_list('parent', flat=True)
                )
            elif target_user.role == 'judge':
                assigned_parents = User.objects.filter(
                    id__in=JugeFolder.objects.filter(juge=target_user).values_list('parent', flat=True)
                )
            self.fields['related_users'].queryset = queryset
            self.fields['related_users'].initial = assigned_parents

    def _setup_lawyer_judge_form(self, target_user):
        if target_user == self.request_user:
            self.fields.pop('related_users', None)
        elif target_user.role == 'parent':
            assigned_users = User.objects.filter(
                id__in=AvocatFolder.objects.filter(parent=target_user).values_list('avocat', flat=True)
            ) | User.objects.filter(
                id__in=JugeFolder.objects.filter(parent=target_user).values_list('juge', flat=True)
            )
            self.fields['related_users'].queryset = assigned_users
            self.fields['related_users'].initial = assigned_users
            self.fields['related_users'].widget.attrs['disabled'] = True
        else:
            self.fields.pop('related_users', None)

    def _setup_parent_form(self, target_user):
        if target_user == self.request_user:
            assigned_users = User.objects.filter(
                id__in=AvocatFolder.objects.filter(parent=target_user).values_list('avocat', flat=True)
            ) | User.objects.filter(
                id__in=JugeFolder.objects.filter(parent=target_user).values_list('juge', flat=True)
            )
            self.fields['related_users'].queryset = assigned_users
            self.fields['related_users'].initial = assigned_users
            self.fields['related_users'].widget.attrs['disabled'] = True
        else:
            self.fields.pop('related_users', None)



    def _handle_parent_relationships(self, related_users_ids):
        related_users_ids = set(related_users_ids)

        current_lawyer_relations = set(AvocatFolder.objects.filter(parent=self.instance).values_list('avocat_id', flat=True))
        current_judge_relations = set(JugeFolder.objects.filter(parent=self.instance).values_list('juge_id', flat=True))

        relationships_to_add = related_users_ids - current_lawyer_relations - current_judge_relations
        relationships_to_remove = (current_lawyer_relations | current_judge_relations) - related_users_ids

        AvocatFolder.objects.filter(parent=self.instance, avocat_id__in=relationships_to_remove).delete()
        JugeFolder.objects.filter(parent=self.instance, juge_id__in=relationships_to_remove).delete()

        for user_id in relationships_to_add:
            user_instance = User.objects.get(pk=user_id)
            if user_instance.role == 'lawyer':
                AvocatFolder.objects.get_or_create(parent=self.instance, avocat=user_instance)
            elif user_instance.role == 'judge':
                JugeFolder.objects.get_or_create(parent=self.instance, juge=user_instance)

    def _handle_lawyer_judge_relationships(self, related_users_ids):
        related_users_ids = set(related_users_ids)

        if self.instance.role == 'lawyer':
            current_relations = set(AvocatFolder.objects.filter(avocat=self.instance).values_list('parent_id', flat=True))
            relationship_model = AvocatFolder
            own_field = 'avocat'
        elif self.instance.role == 'judge':
            current_relations = set(AvocatFolder.objects.filter(juge=self.instance).values_list('parent_id', flat=True))
            relationship_model = JugeFolder
            own_field = 'juge'

        relationships_to_add = related_users_ids - current_relations
        relationships_to_remove = current_relations - related_users_ids

        relationship_model.objects.filter(**{own_field: self.instance, 'parent_id__in': relationships_to_remove}).delete()

        for user_id in relationships_to_add:
            parent_instance = User.objects.get(pk=user_id)
            relationship_model.objects.get_or_create(**{own_field: self.instance, 'parent': parent_instance})

    # def form_valid(self, form):
    #     if not self.request_user.is_superuser and 'role' in form.changed_data:
    #         form.add_error('role', _("You are not authorized to change the role."))
    #         return super().form_invalid(form)
    #
    #     response = super().form_valid(form)
    #
    #     if 'related_users' in form.cleaned_data:
    #         related_users_ids = form.cleaned_data['related_users'].values_list('id', flat=True)
    #         related_users_ids = set(related_users_ids)
    #         if self.instance.role == 'parent':
    #             self._handle_parent_relationships(related_users_ids)
    #         elif self.instance.role in ['lawyer', 'judge']:
    #             self._handle_lawyer_judge_relationships(related_users_ids)
    #
    #     return response


class JusticeRegistrationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('judge', 'Judge'),
        ('lawyer', 'Attorney'),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Role")
    first_name = forms.CharField(max_length=30, label=_('First Name'), required=True)
    last_name = forms.CharField(max_length=150, label=_('Last Name'), required=True)
    num_telephone = forms.CharField(max_length=20, initial='+32', label=_('Telephone Number'), required=False)
    parents_assigned = forms.ModelMultipleChoiceField(queryset=User.objects.filter(role='parent'), required=False,
                                                      label=_("Assign Parents"))

    class Meta:
        model = User
        fields = ['role', 'last_name', 'first_name', 'email', 'password1', 'password2', 'num_telephone',
                  'parents_assigned']

    def __init__(self, *args, **kwargs):
        super(JusticeRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        self.fields['parents_assigned'].help_text = _("Press Control or Shift to select several Parents.")


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
            assigned_parents = self.cleaned_data['parents_assigned']
            if user.role == 'lawyer':
                for parent in assigned_parents:
                    AvocatFolder.objects.get_or_create(avocat=user, parent=parent)
            elif user.role == 'judge':
                for parent in assigned_parents:
                    JugeFolder.objects.get_or_create(juge=user, parent=parent)
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
    telephone = forms.CharField(max_length=13, required=False, label=_("Telephone"))
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
        return validate_telephone(telephone)

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1', '')
        return validate_password(password1)

    def clean_password2(self):
        # Ensure this password matches the first one entered
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError(_('The passwords do not match.'))
        return password2



class DeletionRequestForm(forms.Form):
    confirm = forms.BooleanField(label="Confirm deletion request")


class CancelDeletionForm(forms.Form):
    confirm = forms.BooleanField(label="Confirm cancellation of deletion request")
