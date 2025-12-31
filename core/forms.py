from django import forms
from .models import Personel, Puantaj, FinansalHareket, TaksitliAvans

class PuantajForm(forms.ModelForm):
    class Meta:
        model = Puantaj
        fields = ['personel', 'durum', 'giris_saati', 'cikis_saati']
        widgets = {
            'giris_saati': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'cikis_saati': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'durum': forms.Select(attrs={'class': 'form-select'}),
            'personel': forms.Select(attrs={'class': 'form-select'}),
        }

class FinansalIslemForm(forms.ModelForm):
    class Meta:
        model = FinansalHareket
        fields = ['personel', 'islem_tipi', 'tutar', 'aciklama']
        widgets = {
            'personel': forms.Select(attrs={'class': 'form-select'}),
            'islem_tipi': forms.Select(attrs={'class': 'form-select'}),
            'tutar': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'aciklama': forms.TextInput(attrs={'class': 'form-control'}),
        }

class TaksitliAvansForm(forms.ModelForm):
    class Meta:
        model = TaksitliAvans
        fields = ['personel', 'toplam_tutar', 'taksit_sayisi', 'aciklama']
        widgets = {
            'personel': forms.Select(attrs={'class': 'form-select'}),
            'toplam_tutar': forms.NumberInput(attrs={'class': 'form-control'}),
            'taksit_sayisi': forms.NumberInput(attrs={'class': 'form-control'}),
            'aciklama': forms.TextInput(attrs={'class': 'form-control'}),
        }