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
    class Meta:
        model = Case
        fields = ['parent1', 'parent2']

    def __init__(self, *args, **kwargs):
        super(CaseForm, self).__init__(*args, **kwargs)
        self.fields['parent1'].queryset = User.objects.filter(role='parent')
        self.fields['parent2'].queryset = User.objects.filter(role='parent')
        if self.instance and self.instance.draft:
            self.fields['parent2'].required = False

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