from django import forms

from accounts.views import User
from .models import Document, Case, Category


class PaymentDocumentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.order_by('type', 'name')
        self.fields['category'].required = True

    class Meta:
        model = Document
        fields = ['amount', 'category', 'date', 'document']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }


class PaymentDocumentFormLawyer(forms.ModelForm):
    parent = forms.ChoiceField(choices=())

    class Meta:
        model = Document
        fields = ['amount', 'category', 'date', 'document', 'parent']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        parent_choices = kwargs.pop('parent_choices', None)
        super().__init__(*args, **kwargs)
        if parent_choices:
            self.fields['parent'].choices = parent_choices


class CaseForm(forms.ModelForm):
    lawyer = forms.ModelChoiceField(queryset=User.objects.filter(role='lawyer'), required=False)

    class Meta:
        model = Case
        fields = ['parent1', 'parent2']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CaseForm, self).__init__(*args, **kwargs)
        self.fields['parent1'].queryset = User.objects.filter(role='parent')
        self.fields['parent2'].queryset = User.objects.filter(role='parent')
        if self.instance and self.instance.draft:
            self.fields['parent2'].required = False
        if self.user and self.user.role == 'administrator':
            self.fields['lawyer'].required = True
        else:
            self.fields.pop('lawyer')


class ConvertDraftCaseForm(forms.ModelForm):
    parent2 = forms.ModelChoiceField(
        queryset=User.objects.filter(role='parent'),
        label="Select Second Parent"
    )

    class Meta:
        model = Case
        fields = ['parent2']

    def __init__(self, *args, **kwargs):
        super(ConvertDraftCaseForm, self).__init__(*args, **kwargs)
        case = kwargs.get('instance')
        if case:
            self.fields['parent2'].queryset = User.objects.filter(role='parent').exclude(id=case.parent1.id)
            self.fields['parent2'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"

class CombineDraftsForm(forms.Form):
    draft1 = forms.ModelChoiceField(queryset=Case.objects.filter(draft=True), label="Select First Draft")
    draft2 = forms.ModelChoiceField(queryset=Case.objects.filter(draft=True), label="Select Second Draft")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        initial_draft1 = kwargs.pop('initial_draft1', None)
        super(CombineDraftsForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['draft1'].queryset = Case.objects.filter(draft=True, parent1=user)
            self.fields['draft2'].queryset = Case.objects.filter(draft=True).exclude(parent1=user)

            self.fields['draft1'].label_from_instance = self.label_from_instance
            self.fields['draft2'].label_from_instance = self.label_from_instance

            if initial_draft1:
                self.fields['draft1'].initial = initial_draft1
                self.fields['draft1'].queryset = Case.objects.filter(id=initial_draft1.id)
                self.fields['draft2'].queryset = self.fields['draft2'].queryset.exclude(parent1=initial_draft1.parent1)

    def label_from_instance(self, obj):
        parent = obj.parent1
        created_at = obj.created_at.strftime("%Y-%m-%d %H:%M")
        updated_at = obj.updated_at.strftime("%Y-%m-%d %H:%M")
        return f"{parent.last_name} {parent.first_name[0]}. | Created: {created_at} | Updated: {updated_at}"


class ValidatePaymentsForm(forms.Form):
    PAYMENTS_CHOICES = (
        ('validate', 'Validate'),
        ('reject', 'Reject'),
    )
    action = forms.ChoiceField(choices=PAYMENTS_CHOICES)
    payments = forms.ModelMultipleChoiceField(queryset=Document.objects.filter(status='pending'), widget=forms.CheckboxSelectMultiple)


class IndexPaymentForm(forms.Form):
    percentage = forms.DecimalField(label='Percentage (%)', min_value=0, max_value=100)
    confirm_indexation = forms.CharField(widget=forms.HiddenInput(), required=False, initial='false')


class AddJugeAvocatForm(forms.Form):
    juges = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),  # Initialement vide
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    avocats = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),  # Initialement vide
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    case = forms.ModelChoiceField(
        queryset=Case.objects.all(),
        widget=forms.HiddenInput(),
        required=True
    )

    def set_juges_queryset(self, queryset):
        self.fields['juges'].queryset = queryset

    def set_avocats_queryset(self, queryset):
        self.fields['avocats'].queryset = queryset