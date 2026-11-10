# Visa Centrum XBA — sayt (Django)

Kompaniyaning to'liq veb-sayti: bosh sahifa (hero, xizmatlar, biz haqimizda,
jarayon, aloqa formasi) + vakansiyalar bo'limi, 4 tilda (o'zbek, nemis, ingliz,
rus). Vakansiyalarni va aloqa formasidan kelgan murojaatlarni admin panel
orqali boshqarasiz.

Bu loyiha `~/visa-centrum-bot` (Telegram bot + arizalar admin paneli, port
8000) loyihasidan **mustaqil** — u nomzodlarning arizalarini boshqaradi, bu esa
saytning o'zini, undagi vakansiyalar ro'yxatini va saytdan kelgan
murojaatlarni. Ikkalasi bir vaqtda ishlashi mumkin, portlari kesishmaydi (bu
loyiha 8001-portda ishlaydi).

## Talab qilinadigan narsalar

- Python 3.11+ (loyiha 3.13'da yaratilgan va sinovdan o'tgan)
- Terminal / buyruqlar qatori

Boshqa hech narsa shart emas — ma'lumotlar bazasi sifatida SQLite ishlatiladi,
alohida server o'rnatish kerak emas.

## O'rnatish (noldan)

```bash
cd ~/visa-centrum-web

# 1) Virtual environment yaratish va faollashtirish
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate

# 2) Kutubxonalarni o'rnatish
pip install -r requirements.txt

# 3) Muhit sozlamalari
cp .env.example .env                 # ichidagi qiymatlarni production uchun almashtirasiz

# 4) Ma'lumotlar bazasini tayyorlash
python manage.py migrate

# 5) Admin panelga kirish uchun superuser yaratish
python manage.py createsuperuser

# 6) Serverni ishga tushirish
python manage.py runserver 8001
```

Agar `.venv` allaqachon mavjud bo'lsa (masalan, loyiha shu holatda
ko'chirilgan bo'lsa), 1-2-qadamlarni takrorlash shart emas — shunchaki
`source .venv/bin/activate` qiling va 4-6-qadamlarga o'ting.

Ochiladigan manzillar:

- **Sayt:** http://127.0.0.1:8001
- **Admin panel:** http://127.0.0.1:8001/admin/ — 5-qadamda o'rnatgan
  login/parolingiz bilan kiring.

Serverni to'xtatish uchun terminalda `Ctrl+C` bosing.

## Docker orqali ishga tushirish

Docker Desktop o'rnatilgan bo'lsa, loyiha ildiz katalogida quyidagilarni
ishlating:

```bash
cd ~/visa-centrum-web
docker compose up --build
```

Docker konteyneri migratsiyalarni avtomatik qo'llaydi va saytni
`http://127.0.0.1:8001` manzilida ishga tushiradi. Admin panel:
`http://127.0.0.1:8001/admin/`.

Admin foydalanuvchisi yaratish uchun boshqa terminalda:

```bash
docker compose exec web python manage.py createsuperuser
```

Konteynerni to'xtatish:

```bash
docker compose down
```

SQLite ma'lumotlar bazasi `./db.sqlite3` orqali konteynerdan tashqarida
saqlanadi, shuning uchun konteyner qayta yaratilganda ma'lumotlar yo'qolmaydi.

## Loyiha tuzilishi

```
visa-centrum-web/
├── manage.py
├── requirements.txt
├── .env / .env.example
├── db.sqlite3                    # SQLite ma'lumotlar bazasi (avtomatik yaratiladi)
├── visa_centrum/                 # loyiha sozlamalari (settings, urls)
├── core/                         # bosh sahifa + tarjimalar + aloqa formasi
│   ├── models.py                 #   ContactMessage — aloqa formasidan kelgan murojaatlar
│   ├── forms.py                  #   ContactForm — F.I.Sh./email/telefon/xabar validatsiyasi
│   ├── translations.py           #   saytning barcha statik matnlari, 4 tilda
│   ├── context_processors.py     #   joriy tilni har bir shablonga uzatadi
│   ├── static/core/               #   CSS, logotip rasmlari
│   └── templates/                #   base.html (header/footer/menyu) + core/home.html
└── vacancies/                    # vakansiyalar
    ├── models.py                 #   Vacancy — har bir maydon 4 tilda
    ├── admin.py                  #   admin panel sozlamalari
    └── templates/vacancies/      #   ro'yxat (list.html) va batafsil (detail.html) sahifalar
```

## Saytning imkoniyatlari

- **4 til:** header'dagi til tanlovchisi (UZ/DE/EN/RU) orqali almashtiriladi,
  tanlov cookie/sessiyada saqlanadi. URL'lar `/de/`, `/en/`, `/ru/`
  prefiksi bilan (o'zbekcha — prefikssiz, `/`). Sayt matnlari
  `core/translations.py`dagi lug'atdan olinadi — Django'ning gettext/`.po`
  tizimi ishlatilmaydi, shuning uchun compile qilish shart emas.
- **Mobil moslashuv:** ≤980px ekranlarda yon menyu gamburger tugmasiga
  yig'iladi.
- **Bosh sahifa:** hero (asosiy taklif + "Bepul konsultatsiya" va
  "Vakansiyalarni ko'rish" tugmalari), xizmatlar, biz haqimizda (HOFF
  consulting hamkorlik logotipi bilan), jarayon bosqichlari, aloqa formasi.
- **Aloqa formasi** (`#contact`) — F.I.Sh., email, telefon, xabar maydonlari.
  Yuborilgan ma'lumot `ContactMessage` jadvaliga saqlanadi, foydalanuvchiga
  "Rahmat!" xabari ko'rsatiladi. Manzil (Xurmontepa 27, Toshkent), telefon
  (+998 78 333 97 97) va email (visa.centrum.uz@gmail.com) forma yonida
  ko'rsatiladi.
- **Vakansiyalar** — `/vacancies/` sahifasida ro'yxat, har biri uchun
  alohida batafsil sahifa (`/vacancies/<slug>/`).

## Admin panelda ishlash

### Vakansiya qo'shish / tahrirlash

1. `/admin/` ga kiring → **Vakansiyalar** → **Vakansiya qo'shish**.
2. "Umumiy" bo'limida o'rinlar sonini va "Chop etilgan" belgisini
   qo'ying (belgi olib tashlansa, vakansiya saytda ko'rinmay qoladi, lekin
   o'chirilmaydi).
3. Har bir til bo'limida (O'zbekcha / Deutsch / English / Русский):
   - **Sarlavha** — vakansiya nomi (masalan, "Fahrer / Postdienst").
   - **Manzil / yo'nalish** — qisqa qator, ro'yxatda sarlavha ostida
     ko'rinadi (masalan, "Germaniya · Haydovchi / Pochta xizmati").
   - **To'liq ma'lumot** — batafsil sahifada to'liq ko'rinadigan matn:
     talablar, sharoitlar, maosh va hokazolarni shu yerga yozing. Qatorlar
     saytda xuddi shunday saqlanib qoladi (bo'sh qator — yangi abzats).
4. Kamida o'zbekcha maydonlarni to'ldirish shart — boshqa til bo'sh
   qolsa, o'sha til tanlangan tashrifchiga o'zbekcha matn ko'rsatiladi
   (bo'sh sahifa chiqmaydi).
5. Saqlang — havola (`slug`) sarlavhadan avtomatik hosil bo'ladi.

### Aloqa formasidan kelgan murojaatlar

1. `/admin/` → **Murojaatlar** — barcha yuborilgan formalar ro'yxati
   (F.I.Sh., email, telefon, sana bo'yicha saralanadi/qidiriladi).
2. Murojaat matnini (F.I.Sh./email/telefon/xabar) admin panelda o'zgartirib
   bo'lmaydi — bular faqat o'qish uchun, foydalanuvchi yozgan holicha
   saqlanadi.
3. **Holat** ustuni — faqat administrator uchun ichki belgi (Yangi /
   Ko'rib chiqilmoqda / Yakunlandi), saytda hech qachon ko'rinmaydi. Ro'yxat
   sahifasida to'g'ridan-to'g'ri o'zgartirib, "Saqlash" tugmasini bosishingiz
   mumkin.

## Ishlab chiqarishga (production) chiqarishdan oldin

- `.env`da `DJANGO_SECRET_KEY`ni uzun tasodifiy qiymatga almashtiring:
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
- `DJANGO_DEBUG=False` qiling va `DJANGO_ALLOWED_HOSTS`ga haqiqiy
  domeningizni qo'shing.
- `python manage.py collectstatic` ishga tushiring va statik fayllarni
  Nginx orqali bering (yoki `whitenoise` kutubxonasini qo'shing).
- SQLite kichik trafik uchun yetarli; katta yuklama kutilsa, `DATABASES`
  sozlamasini Postgres'ga o'zgartiring (bot loyihasidagi kabi).
- Saytni haqiqiy pochta serveri bilan bog'lashni xohlasangiz (masalan, yangi
  murojaat kelganda administratorga email yuborish), `EMAIL_*` sozlamalarini
  `settings.py`ga qo'shib, `core/views.py`dagi `home()` funksiyasida
  `form.save()`dan keyin xabar yuborish kodini qo'shing — hozircha bu
  ulanmagan, murojaatlar faqat admin panelda ko'rinadi.
