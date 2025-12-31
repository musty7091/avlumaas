from django.contrib import admin
from .models import Personel, TaksitliAvans, FinansalHareket, Puantaj

@admin.register(Personel)
class PersonelAdmin(admin.ModelAdmin):
    list_display = ('ad', 'soyad', 'telefon', 'calisma_tipi', 'aktif_mi')
    search_fields = ('ad', 'soyad', 'tc_no')
    list_filter = ('calisma_tipi', 'aktif_mi')

@admin.register(Puantaj)
class PuantajAdmin(admin.ModelAdmin):
    list_display = ('personel', 'tarih', 'durum', 'giris_saati', 'cikis_saati', 'hesaplanan_mesai_saati')
    list_filter = ('tarih', 'durum')
    date_hierarchy = 'tarih'

@admin.register(FinansalHareket)
class FinansalHareketAdmin(admin.ModelAdmin):
    list_display = ('personel', 'islem_tipi', 'tutar', 'tarih')
    list_filter = ('islem_tipi', 'tarih')

@admin.register(TaksitliAvans)
class TaksitliAvansAdmin(admin.ModelAdmin):
    list_display = ('personel', 'toplam_tutar', 'taksit_sayisi', 'tamamlandi')