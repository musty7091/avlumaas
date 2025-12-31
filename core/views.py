from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Q
from django.http import HttpResponse 
from .models import Personel, Puantaj, FinansalHareket, TaksitliAvans
from .forms import PuantajForm, FinansalIslemForm, TaksitliAvansForm
from datetime import datetime
import calendar
import pandas as pd
import io

def ana_sayfa(request):
    bugun = timezone.now().date()
    
    # 1. Personel Sayıları
    toplam_personel = Personel.objects.filter(aktif_mi=True).count()
    bugun_gelen = Puantaj.objects.filter(tarih=bugun, durum__in=['geldi', 'hafta_tatili']).count()
    gelmeyen = toplam_personel - bugun_gelen
    
    # 2. Bu Ay Dağıtılan Toplam Avans/Kesinti (Finansal Özet)
    bu_ay_avans = FinansalHareket.objects.filter(
        tarih__year=bugun.year,
        tarih__month=bugun.month,
        islem_tipi__in=['basit_avans', 'kasa_acigi', 'alisveris']
    ).aggregate(Sum('tutar'))['tutar__sum'] or 0

    # 3. Son 5 Finansal Hareket (Sayfa boş durmasın)
    son_hareketler = FinansalHareket.objects.select_related('personel').order_by('-id')[:5]

    return render(request, 'core/ana_sayfa.html', {
        'toplam_personel': toplam_personel,
        'bugun_gelen': bugun_gelen,
        'gelmeyen': gelmeyen,
        'bu_ay_avans': bu_ay_avans,
        'son_hareketler': son_hareketler,
        'bugun': bugun, # <-- EKLENDİ: Artık butonda tarih yazacak.
    })

def personel_listesi(request):
    personeller = Personel.objects.filter(aktif_mi=True)
    return render(request, 'core/personel_listesi.html', {'personeller': personeller})

def personel_detay(request, personel_id):
    personel = get_object_or_404(Personel, id=personel_id)
    hareketler = personel.finansal_hareketler.all().order_by('-tarih')
    avanslar = personel.taksitli_avanslar.all()
    
    if request.method == 'POST':
        if 'basit_islem' in request.POST:
            form = FinansalIslemForm(request.POST)
            if form.is_valid():
                islem = form.save(commit=False)
                islem.personel = personel
                islem.save()
                messages.success(request, 'İşlem eklendi.')
                return redirect('personel_detay', personel_id=personel.id)
    else:
        finans_form = FinansalIslemForm(initial={'personel': personel})

    return render(request, 'core/personel_detay.html', {
        'personel': personel,
        'hareketler': hareketler,
        'avanslar': avanslar,
        'finans_form': finans_form
    })

def yoklama_al(request):
    secilen_tarih_str = request.GET.get('tarih')
    if secilen_tarih_str:
        secilen_tarih = datetime.strptime(secilen_tarih_str, '%Y-%m-%d').date()
    else:
        secilen_tarih = timezone.now().date()
    
    personeller = Personel.objects.filter(aktif_mi=True)
    
    if request.method == 'POST':
        personel_id = request.POST.get('personel_id')
        durum = request.POST.get('durum')
        giris = request.POST.get('giris_saati')
        cikis = request.POST.get('cikis_saati')
        
        kayit_tarihi_str = request.POST.get('kayit_tarihi')
        kayit_tarihi = datetime.strptime(kayit_tarihi_str, '%Y-%m-%d').date()
        
        personel = get_object_or_404(Personel, id=personel_id)
        
        puantaj, created = Puantaj.objects.get_or_create(
            personel=personel, 
            tarih=kayit_tarihi
        )
        puantaj.durum = durum
        puantaj.giris_saati = giris if giris else None
        puantaj.cikis_saati = cikis if cikis else None
        puantaj.save()
        
        messages.success(request, f'{personel.ad} güncellendi.')
        return redirect(f'/yoklama/?tarih={kayit_tarihi}')

    gunun_kayitlari = {p.personel_id: p for p in Puantaj.objects.filter(tarih=secilen_tarih)}
    
    list_data = []
    for p in personeller:
        kayit = gunun_kayitlari.get(p.id)
        list_data.append({
            'personel': p,
            'kayit': kayit
        })

    return render(request, 'core/yoklama.html', {
        'list_data': list_data, 
        'secilen_tarih': secilen_tarih
    })

def toplu_puantaj(request, personel_id):
    personel = get_object_or_404(Personel, id=personel_id)
    
    bugun = timezone.now().date()
    try:
        yil = int(request.GET.get('yil', bugun.year))
        ay = int(request.GET.get('ay', bugun.month))
    except ValueError:
        yil = bugun.year
        ay = bugun.month
    
    _, son_gun = calendar.monthrange(yil, ay)
    
    if request.method == 'POST':
        for day in range(1, son_gun + 1):
            tarih_str = f"{yil}-{ay:02d}-{day:02d}"
            tarih_obj = datetime.strptime(tarih_str, '%Y-%m-%d').date()
            
            durum = request.POST.get(f'durum_{tarih_str}')
            giris = request.POST.get(f'giris_{tarih_str}')
            cikis = request.POST.get(f'cikis_{tarih_str}')
            
            if not durum: continue

            puantaj, created = Puantaj.objects.get_or_create(
                personel=personel,
                tarih=tarih_obj
            )
            puantaj.durum = durum
            puantaj.giris_saati = giris if giris else None
            puantaj.cikis_saati = cikis if cikis else None
            puantaj.save()
            
        messages.success(request, f'{personel.ad} için {ay}/{yil} kayıtları güncellendi.')
        return redirect(f'/personel/{personel.id}/toplu-puantaj/?ay={ay}&yil={yil}')

    mevcut_kayitlar = {
        p.tarih.day: p 
        for p in Puantaj.objects.filter(personel=personel, tarih__year=yil, tarih__month=ay)
    }
    
    gunler_listesi = []
    for day in range(1, son_gun + 1):
        tarih_obj = datetime(yil, ay, day).date()
        kayit = mevcut_kayitlar.get(day)
        
        gunler_listesi.append({
            'tarih': tarih_obj,
            'tarih_str': f"{yil}-{ay:02d}-{day:02d}",
            'gun_adi': tarih_obj.strftime('%A'),
            'kayit': kayit
        })

    return render(request, 'core/toplu_puantaj.html', {
        'personel': personel,
        'gunler_listesi': gunler_listesi,
        'yil': yil,
        'ay': ay,
        'ay_adi': calendar.month_name[ay]
    })

def maas_raporu(request):
    bugun = timezone.now().date()
    try:
        yil = int(request.GET.get('yil', bugun.year))
        ay = int(request.GET.get('ay', bugun.month))
    except ValueError:
        yil = bugun.year
        ay = bugun.month

    personeller = Personel.objects.filter(aktif_mi=True)
    rapor_listesi = []
    genel_toplam_odenecek = 0

    for p in personeller:
        calistigi_gun = Puantaj.objects.filter(
            personel=p, 
            tarih__year=yil, 
            tarih__month=ay, 
            durum__in=['geldi', 'hafta_tatili']
        ).count()
        
        gelmedigi_gun = Puantaj.objects.filter(
            personel=p, 
            tarih__year=yil, 
            tarih__month=ay,
            durum__in=['gelmedi', 'ucretsiz_izin']
        ).count()

        toplam_mesai = Puantaj.objects.filter(
            personel=p, 
            tarih__year=yil, 
            tarih__month=ay
        ).aggregate(Sum('hesaplanan_mesai_saati'))['hesaplanan_mesai_saati__sum'] or 0
        
        mesai_ucreti = float(toplam_mesai) * float(p.ozel_mesai_ucreti)

        ana_hakedis = 0
        maas_kesintisi = 0 
        
        if p.calisma_tipi == 'aylik':
            gunluk_maliyet = float(p.maas_tutari) / 30
            maas_kesintisi = gunluk_maliyet * gelmedigi_gun
            ana_hakedis = float(p.maas_tutari) - maas_kesintisi
        else:
            ana_hakedis = float(p.maas_tutari) * calistigi_gun

        tum_hareketler = FinansalHareket.objects.filter(
            personel=p, 
            tarih__year=yil, 
            tarih__month=ay
        )
        
        toplam_prim = tum_hareketler.filter(islem_tipi='prim').aggregate(Sum('tutar'))['tutar__sum'] or 0
        diger_kesintiler = tum_hareketler.exclude(islem_tipi='prim').aggregate(Sum('tutar'))['tutar__sum'] or 0
        
        taksit_kesintisi = TaksitliAvans.objects.filter(
            personel=p, 
            tamamlandi=False
        ).aggregate(Sum('aylik_kesinti'))['aylik_kesinti__sum'] or 0

        toplam_kesinti = float(diger_kesintiler) + float(taksit_kesintisi)

        net_maas = ana_hakedis + mesai_ucreti + float(toplam_prim) - toplam_kesinti
        genel_toplam_odenecek += net_maas

        rapor_listesi.append({
            'personel': p,
            'calistigi_gun': calistigi_gun,
            'gelmedigi_gun': gelmedigi_gun,
            'ana_hakedis': ana_hakedis,
            'toplam_mesai': toplam_mesai,
            'mesai_ucreti': mesai_ucreti,
            'toplam_prim': toplam_prim,
            'toplam_kesinti': toplam_kesinti,
            'net_maas': net_maas
        })

    return render(request, 'core/maas_raporu.html', {
        'rapor_listesi': rapor_listesi,
        'genel_toplam': genel_toplam_odenecek,
        'yil': yil,
        'ay': ay,
        'ay_adi': calendar.month_name[ay]
    })

def personel_import(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        
        try:
            # Pandas ile dosyayı oku
            df = pd.read_excel(excel_file)
            
            basarili = 0
            atlanan = 0
            
            for index, row in df.iterrows():
                try:
                    tc = str(row['TC No']).strip()
                    if Personel.objects.filter(tc_no=tc).exists():
                        atlanan += 1
                        continue # Zaten varsa atla

                    # Çalışma tipi belirle
                    c_tipi_raw = str(row['Çalışma Tipi']).lower()
                    c_tipi = 'gunluk' if 'gün' in c_tipi_raw else 'aylik'
                    
                    # Tarih formatlama
                    tarih_val = row['Giriş Tarihi']
                    if pd.isna(tarih_val):
                        tarih_obj = timezone.now().date()
                    else:
                        tarih_obj = pd.to_datetime(tarih_val).date()

                    Personel.objects.create(
                        ad=row['Ad'],
                        soyad=row['Soyad'],
                        tc_no=tc,
                        telefon=row['Telefon'],
                        calisma_tipi=c_tipi,
                        maas_tutari=row['Maaş'],
                        ozel_mesai_ucreti=row.get('Mesai Ücreti', 250),
                        iban=row.get('IBAN', ''),
                        banka_adi=row.get('Banka', ''),
                        ise_giris_tarihi=tarih_obj
                    )
                    basarili += 1
                except Exception as e:
                    print(f"Satır hatası: {e}")
                    atlanan += 1
            
            messages.success(request, f"{basarili} personel başarıyla eklendi. {atlanan} kayıt atlandı (TC çakışması veya hata).")
            return redirect('personel_listesi')

        except Exception as e:
            messages.error(request, f"Dosya okuma hatası: {e}")

    return render(request, 'core/personel_import.html')

def download_excel_template(request):
    # Boş bir DataFrame oluştur (Sadece başlıklar)
    columns = ['Ad', 'Soyad', 'TC No', 'Telefon', 'Çalışma Tipi', 'Maaş', 'Mesai Ücreti', 'Giriş Tarihi', 'IBAN', 'Banka']
    df = pd.DataFrame(columns=columns)
    
    # Excel dosyasını bellekte oluştur
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Personel Listesi')
    
    buffer.seek(0)
    
    # Dosyayı indirilebilir olarak sun
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="personel_sablon.xlsx"'
    
    return response

# --- YENİ: TOPLU MAAŞ RAPORUNU EXCEL OLARAK İNDİRME ---
def maas_raporu_indir(request):
    bugun = timezone.now().date()
    try:
        yil = int(request.GET.get('yil', bugun.year))
        ay = int(request.GET.get('ay', bugun.month))
    except ValueError:
        yil = bugun.year
        ay = bugun.month

    # Rapor verisini hazırla (maas_raporu fonksiyonundaki mantığın aynısı)
    personeller = Personel.objects.filter(aktif_mi=True)
    data = []

    for p in personeller:
        calistigi_gun = Puantaj.objects.filter(personel=p, tarih__year=yil, tarih__month=ay, durum__in=['geldi', 'hafta_tatili']).count()
        gelmedigi_gun = Puantaj.objects.filter(personel=p, tarih__year=yil, tarih__month=ay, durum__in=['gelmedi', 'ucretsiz_izin']).count()
        toplam_mesai = Puantaj.objects.filter(personel=p, tarih__year=yil, tarih__month=ay).aggregate(Sum('hesaplanan_mesai_saati'))['hesaplanan_mesai_saati__sum'] or 0
        mesai_ucreti = float(toplam_mesai) * float(p.ozel_mesai_ucreti)

        if p.calisma_tipi == 'aylik':
            gunluk_maliyet = float(p.maas_tutari) / 30
            maas_kesintisi = gunluk_maliyet * gelmedigi_gun
            ana_hakedis = float(p.maas_tutari) - maas_kesintisi
        else:
            ana_hakedis = float(p.maas_tutari) * calistigi_gun

        tum_hareketler = FinansalHareket.objects.filter(personel=p, tarih__year=yil, tarih__month=ay)
        toplam_prim = tum_hareketler.filter(islem_tipi='prim').aggregate(Sum('tutar'))['tutar__sum'] or 0
        diger_kesintiler = tum_hareketler.exclude(islem_tipi='prim').aggregate(Sum('tutar'))['tutar__sum'] or 0
        taksit_kesintisi = TaksitliAvans.objects.filter(personel=p, tamamlandi=False).aggregate(Sum('aylik_kesinti'))['aylik_kesinti__sum'] or 0
        toplam_kesinti = float(diger_kesintiler) + float(taksit_kesintisi)
        net_maas = ana_hakedis + mesai_ucreti + float(toplam_prim) - toplam_kesinti

        data.append({
            'Ad Soyad': f"{p.ad} {p.soyad}",
            'Çalışma Tipi': p.get_calisma_tipi_display(),
            'Çalıştığı Gün': calistigi_gun,
            'Gelmediği Gün': gelmedigi_gun,
            'Ana Hakediş': ana_hakedis,
            'Mesai Saati': toplam_mesai,
            'Mesai Ücreti': mesai_ucreti,
            'Primler': toplam_prim,
            'Kesintiler': toplam_kesinti,
            'NET ÖDENECEK': net_maas
        })

    # Pandas ile Excel oluştur
    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=f'{ay}-{yil} Maas Raporu')
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Maas_Raporu_{ay}_{yil}.xlsx"'
    return response

# --- YENİ: KİŞİYE ÖZEL MAAŞ PUSULASI / DETAY RAPOR ---
def personel_pusula(request, personel_id):
    personel = get_object_or_404(Personel, id=personel_id)
    bugun = timezone.now().date()
    try:
        yil = int(request.GET.get('yil', bugun.year))
        ay = int(request.GET.get('ay', bugun.month))
    except ValueError:
        yil = bugun.year
        ay = bugun.month

    # Hesaplamalar (Tek kişi için)
    calistigi_gun = Puantaj.objects.filter(personel=personel, tarih__year=yil, tarih__month=ay, durum__in=['geldi', 'hafta_tatili']).count()
    gelmedigi_gun = Puantaj.objects.filter(personel=personel, tarih__year=yil, tarih__month=ay, durum__in=['gelmedi', 'ucretsiz_izin']).count()
    toplam_mesai = Puantaj.objects.filter(personel=personel, tarih__year=yil, tarih__month=ay).aggregate(Sum('hesaplanan_mesai_saati'))['hesaplanan_mesai_saati__sum'] or 0
    mesai_ucreti = float(toplam_mesai) * float(personel.ozel_mesai_ucreti)

    if personel.calisma_tipi == 'aylik':
        gunluk_maliyet = float(personel.maas_tutari) / 30
        maas_kesintisi = gunluk_maliyet * gelmedigi_gun
        ana_hakedis = float(personel.maas_tutari) - maas_kesintisi
    else:
        ana_hakedis = float(personel.maas_tutari) * calistigi_gun

    # Hareket Detayları (Pusulada listelemek için)
    tum_hareketler = FinansalHareket.objects.filter(personel=personel, tarih__year=yil, tarih__month=ay).order_by('tarih')
    
    primler_listesi = tum_hareketler.filter(islem_tipi='prim')
    toplam_prim = primler_listesi.aggregate(Sum('tutar'))['tutar__sum'] or 0
    
    kesintiler_listesi = tum_hareketler.exclude(islem_tipi='prim')
    diger_kesintiler = kesintiler_listesi.aggregate(Sum('tutar'))['tutar__sum'] or 0
    
    # Taksitler
    taksitler = TaksitliAvans.objects.filter(personel=personel, tamamlandi=False)
    taksit_kesintisi = taksitler.aggregate(Sum('aylik_kesinti'))['aylik_kesinti__sum'] or 0

    toplam_kesinti = float(diger_kesintiler) + float(taksit_kesintisi)
    net_maas = ana_hakedis + mesai_ucreti + float(toplam_prim) - toplam_kesinti

    return render(request, 'core/personel_pusula.html', {
        'personel': personel,
        'ay': ay,
        'yil': yil,
        'ay_adi': calendar.month_name[ay],
        'calistigi_gun': calistigi_gun,
        'gelmedigi_gun': gelmedigi_gun,
        'ana_hakedis': ana_hakedis,
        'toplam_mesai': toplam_mesai,
        'mesai_ucreti': mesai_ucreti,
        'primler_listesi': primler_listesi,
        'toplam_prim': toplam_prim,
        'kesintiler_listesi': kesintiler_listesi,
        'taksitler': taksitler,
        'taksit_kesintisi': taksit_kesintisi,
        'toplam_kesinti': toplam_kesinti,
        'net_maas': net_maas
    })

# --- YENİ: AYLIK GİRİŞ-ÇIKIŞ LİSTESİ ---
# --- GÜNCELLENMİŞ: PERSONEL FİLTRELİ & VARSAYILAN BOŞ RAPOR ---
def giris_cikis_raporu(request):
    bugun = timezone.now().date()
    try:
        yil = int(request.GET.get('yil', bugun.year))
        ay = int(request.GET.get('ay', bugun.month))
    except ValueError:
        yil = bugun.year
        ay = bugun.month

    # Filtreleme için Personel Listesi
    personeller = Personel.objects.filter(aktif_mi=True)
    secilen_personel_id = request.GET.get('personel_id')

    # VARSAYILAN: BOŞ LİSTE (Puantaj.objects.none())
    # Kullanıcı seçim yapmazsa liste boş gelir.
    kayitlar = Puantaj.objects.none()

    # Eğer bir personel seçildiyse (ve boş değilse) sorguyu çalıştır
    if secilen_personel_id:
        kayitlar = Puantaj.objects.filter(
            tarih__year=yil,
            tarih__month=ay,
            personel_id=secilen_personel_id
        ).select_related('personel').order_by('tarih')
        
        # Template'de 'selected' yapabilmek için ID'yi int'e çeviriyoruz
        try:
            secilen_personel_id = int(secilen_personel_id)
        except ValueError:
            secilen_personel_id = None

    return render(request, 'core/giris_cikis_raporu.html', {
        'kayitlar': kayitlar,
        'yil': yil,
        'ay': ay,
        'ay_adi': calendar.month_name[ay],
        'personeller': personeller,
        'secilen_personel_id': secilen_personel_id
    })

def giris_cikis_raporu_indir(request):
    bugun = timezone.now().date()
    try:
        yil = int(request.GET.get('yil', bugun.year))
        ay = int(request.GET.get('ay', bugun.month))
    except ValueError:
        yil = bugun.year
        ay = bugun.month

    secilen_personel_id = request.GET.get('personel_id')
    
    # Varsayılan boş (Eğer personel seçilmediyse boş Excel döner veya hepsi gelmez)
    kayitlar = Puantaj.objects.none()

    if secilen_personel_id:
        kayitlar = Puantaj.objects.filter(
            tarih__year=yil,
            tarih__month=ay,
            personel_id=secilen_personel_id
        ).select_related('personel').order_by('tarih')
    
    data = []
    for k in kayitlar:
        giris = k.giris_saati.strftime('%H:%M') if k.giris_saati else '-'
        cikis = k.cikis_saati.strftime('%H:%M') if k.cikis_saati else '-'
        
        data.append({
            'Tarih': k.tarih.strftime('%d.%m.%Y'),
            'Gün': k.tarih.strftime('%A'),
            'Personel': f"{k.personel.ad} {k.personel.soyad}",
            'Durum': k.get_durum_display(),
            'Giriş Saati': giris,
            'Çıkış Saati': cikis,
            'Mesai (Saat)': k.hesaplanan_mesai_saati
        })

    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        sheet_name = f'Giris_Cikis_{ay}_{yil}'
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Giris_Cikis_Raporu_{ay}_{yil}.xlsx"'
    return response