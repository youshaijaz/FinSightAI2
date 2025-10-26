from django import forms
from django.core.validators import MinValueValidator
from .models import UploadedFile


class FileUploadForm(forms.Form):
    file = forms.FileField(label='Upload Financial File', help_text='Supports CSV, TXT, XLSX, LOG')


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file']
        widgets = {'file': forms.FileInput(attrs={'class': 'form-control'})}

class TaxForm(forms.Form):
    STATES = [
        ('CA', 'California'), ('NY', 'New York'), ('TX', 'Texas'), ('FL', 'Florida'), ('WA', 'Washington'),
        ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('CO', 'Colorado'),
        ('CT', 'Connecticut'), ('DE', 'Delaware'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'),
        ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'), ('KY', 'Kentucky'),
        ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'), ('MA', 'Massachusetts'), ('MI', 'Michigan'),
        ('MN', 'Minnesota'), ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'),
        ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NC', 'North Carolina'),
        ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'),
        ('RI', 'Rhode Island'), ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'),
        ('UT', 'Utah'), ('VT', 'Vermont'), ('VA', 'Virginia'), ('WV', 'West Virginia'), ('WI', 'Wisconsin'),
        ('WY', 'Wyoming'), ('DC', 'District of Columbia'),
    ]
    gross_income = forms.FloatField(
        label='Gross Annual Income ($)', validators=[MinValueValidator(0)],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 80000'}),
        help_text='Your total taxable income before deductions.'
    )
    filing_status = forms.ChoiceField(
        choices=[('single', 'Single'), ('married', 'Married Filing Jointly')],
        label='Filing Status', widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Choose your IRS filing status.'
    )
    state = forms.ChoiceField(
        choices=STATES, label='State', widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Your state of residence (affects state tax).'
    )
    deductions = forms.FloatField(
        label='Itemized Deductions ($)', required=False, validators=[MinValueValidator(0)], initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 5000 (or 0 for standard)'}),
        help_text='Itemized deductions. Leave 0 to use standard deduction ($15,750 single / $31,500 married).'
    )