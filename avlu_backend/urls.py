from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.ana_sayfa, name='ana_sayfa'),
    path('personeller/', views.personel_listesi, name='personel_listesi'),
    path('personel-ekle-excel/', views.personel_import, name='personel_import'),
    path('sablon-indir/', views.download_excel_template, name='download_excel_template'),
    path('personel/<int:personel_id>/', views.personel_detay, name='personel_detay'),
    path('yoklama/', views.yoklama_al, name='yoklama_al'),
    path('personel/<int:personel_id>/toplu-puantaj/', views.toplu_puantaj, name='toplu_puantaj'),
    
    # Maaş Raporları
    path('maas-raporu/', views.maas_raporu, name='maas_raporu'),
    path('maas-raporu-indir/', views.maas_raporu_indir, name='maas_raporu_indir'),
    path('personel/<int:personel_id>/pusula/', views.personel_pusula, name='personel_pusula'),

    # YENİ: GİRİŞ ÇIKIŞ RAPORU
    path('giris-cikis-raporu/', views.giris_cikis_raporu, name='giris_cikis_raporu'),
    path('giris-cikis-raporu-indir/', views.giris_cikis_raporu_indir, name='giris_cikis_raporu_indir'),
]