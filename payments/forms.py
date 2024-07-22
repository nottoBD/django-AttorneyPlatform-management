from django import forms

from accounts.views import User
from .models import Document, Folder, Category


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


class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['judge', 'parent1', 'parent2']

    def __init__(self, *args, **kwargs):
        super(FolderForm, self).__init__(*args, **kwargs)
        self.fields['judge'].queryset = User.objects.filter(role='judge')
        self.fields['parent1'].queryset = User.objects.filter(role='parent')
        self.fields['parent2'].queryset = User.objects.filter(role='parent')


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
