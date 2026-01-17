# 🎙️ Botyum Transcript

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI_Whisper-412991?style=for-the-badge&logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-PolyForm_NC-blue?style=for-the-badge)

**Ses dosyalarını ve video URL'lerini metne dönüştüren güçlü bir transkript uygulaması**

[Özellikler](#-özellikler) • [Kurulum](#-kurulum) • [Kullanım](#-kullanım) • [Desteklenen Formatlar](#-desteklenen-formatlar) • [Desteklenen Platformlar](#-desteklenen-platformlar)

</div>

---
**Botyum Transcript**, yerel ses/video dosyalarınızı veya popüler sosyal medya platformlarındaki (YouTube, TikTok, Instagram, Facebook, Twitter/X vb.) videoları OpenAI Whisper teknolojisi ile hızlı, hassas ve otomatik bir şekilde metne dönüştüren profesyonel bir transkript aracıdır.

## ✨ Özellikler

### 🎯 Temel Özellikler
- **Otomatik Dil Algılama** - Whisper API ses dosyasındaki dili otomatik olarak algılar ve o dilde transkript eder
- **Çoklu Kaynak Desteği** - Hem yerel ses dosyalarını hem de video URL'lerini işleyebilir
- **Otomatik Format Dönüştürme** - Desteklenen tüm ses formatlarını WAV formatına otomatik dönüştürür

### ⚡ Performans Özellikleri
- **Büyük Dosyalar İçin Parçalama** - Büyük ses dosyalarını otomatik olarak parçalara böler
- **Paralel İşleme** - Parçaları eşzamanlı olarak işleyerek transkript süresini kısaltır
- **Akıllı Boyut Yönetimi** - OpenAI 25MB limitini aşmamak için dinamik parça boyutu ayarlaması
- **Retry Mekanizması** - Bağlantı hatalarında otomatik yeniden deneme

### 🛡️ Güvenlik ve Kullanım
- **Güvenli Ortam Değişkenleri** - API anahtarını `.env` dosyasında saklama
- **Çoklu Encoding Desteği** - `.env` dosyası için farklı encoding formatlarını otomatik algılama
- **Geçici Dosya Temizleme** - İndirilen ve oluşturulan geçici dosyaları otomatik temizleme
- **Python 3.13+ Uyumluluğu** - audioop modülü için workaround desteği

---

## 📦 Kurulum

### Gereksinimler

- **Python 3.8** veya üzeri
- **FFmpeg** (ses dosyası dönüştürme ve video indirme için gerekli)

### 1. Depoyu Klonlayın

```bash
git clone https://github.com/kullanici/botyum-transcript.git
cd botyum-transcript
```

### 2. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### 3. FFmpeg Kurulumu

| İşletim Sistemi | Kurulum Komutu |
|-----------------|----------------|
| **Windows** | [FFmpeg İndirme Sayfası](https://ffmpeg.org/download.html) veya `choco install ffmpeg` |
| **macOS** | `brew install ffmpeg` |
| **Ubuntu/Debian** | `sudo apt-get install ffmpeg` |
| **CentOS/RHEL** | `sudo yum install ffmpeg` |

### 4. API Anahtarı Yapılandırması

OpenAI API anahtarınızı aşağıdaki yöntemlerden biriyle ayarlayın:

#### Yöntem 1: `.env` Dosyası (Önerilen)

```bash
# .env.example dosyasını kopyalayın
cp .env.example .env

# .env dosyasını düzenleyin ve API anahtarınızı girin
OPENAI_API_KEY=sk-your_api_key_here
```

#### Yöntem 2: Ortam Değişkeni

```bash
# Windows (PowerShell)
$env:OPENAI_API_KEY="sk-your_api_key_here"

# Windows (CMD)
set OPENAI_API_KEY=sk-your_api_key_here

# Linux/macOS
export OPENAI_API_KEY=sk-your_api_key_here
```

#### Yöntem 3: Komut Satırı Parametresi

```bash
python main.py dosya.mp3 --api-key sk-your_api_key_here
```

> 📌 **Not:** API anahtarınızı [OpenAI Platform](https://platform.openai.com/api-keys) adresinden alabilirsiniz.

---

## 🚀 Kullanım

### İnteraktif Mod

Dosya yolu veya URL belirtmeden uygulamayı çalıştırın:

```bash
python main.py
```

Uygulama sizden dosya yolu veya URL isteyecektir:

```
Ses dosyasının yolunu veya video URL'sini girin:
(Örnek: C:\Videos\dosya.mp3 veya https://youtu.be/VIDEO_ID)
```

### Komut Satırı Kullanımı

#### Ses Dosyası ile

```bash
# Temel kullanım
python main.py dosya.mp3

# Belirli çıktı dosyasına kaydet
python main.py dosya.opus --output transkript.txt

# API anahtarı ile
python main.py dosya.mp3 --api-key YOUR_API_KEY

# Sadece konsola yazdır (dosyaya kaydetme)
python main.py dosya.mp3 --no-save
```

#### Video URL ile

```bash
# YouTube
python main.py https://youtu.be/VIDEO_ID
python main.py https://www.youtube.com/watch?v=VIDEO_ID
python main.py https://www.youtube.com/shorts/VIDEO_ID

# TikTok
python main.py https://www.tiktok.com/@kullanici/video/123456789

# Instagram
python main.py https://www.instagram.com/reel/VIDEO_ID

# Diğer platformlar
python main.py https://vimeo.com/VIDEO_ID
python main.py https://www.dailymotion.com/video/VIDEO_ID
```

### Gelişmiş Seçenekler

```bash
# Parça uzunluğunu ayarla (dakika cinsinden, varsayılan: 5)
python main.py dosya.mp3 --chunk-length 10

# Paralel işlem sayısını ayarla (varsayılan: 3)
python main.py dosya.mp3 --max-workers 5

# Maksimum parça boyutunu ayarla (MB, varsayılan: 20)
python main.py dosya.mp3 --max-chunk-size 15
```

---

## 📁 Desteklenen Formatlar

### Ses Dosyaları

| Format | Uzantı | Açıklama |
|--------|--------|----------|
| **MP3** | `.mp3` | En yaygın ses formatı |
| **OPUS** | `.opus` | Yüksek sıkıştırma oranlı modern format |
| **WAV** | `.wav` | Sıkıştırılmamış ses formatı |
| **M4A** | `.m4a` | Apple MPEG-4 ses formatı |
| **FLAC** | `.flac` | Kayıpsız sıkıştırma formatı |
| **OGG** | `.ogg` | Açık kaynak ses formatı |
| **MP4** | `.mp4` | Video formatı (ses çıkarılır) |

---

## 🌐 Desteklenen Platformlar

Uygulama, yt-dlp kütüphanesi sayesinde aşağıdaki video platformlarından ses indirip transkript edebilir:

### Birincil Platformlar

| Platform | URL Formatları | Durum |
|----------|----------------|-------|
| **YouTube** | `youtube.com/watch?v=`, `youtu.be/`, `youtube.com/shorts/` | ✅ Tam Destek |
| **TikTok** | `tiktok.com/@user/video/` | ✅ Tam Destek |
| **Instagram** | `instagram.com/p/`, `instagram.com/reel/` | ✅ Tam Destek |
| **Facebook** | `facebook.com/.../videos/` | ✅ Tam Destek |
| **Twitter/X** | `twitter.com/.../status/`, `x.com/.../status/` | ✅ Tam Destek |
| **Vimeo** | `vimeo.com/` | ✅ Tam Destek |
| **Dailymotion** | `dailymotion.com/video/` | ✅ Tam Destek |

### Diğer Desteklenen Platformlar

yt-dlp kütüphanesi 1000'den fazla video platformunu destekler. Desteklenen tüm platformların listesi için:

```bash
yt-dlp --list-extractors
```

> ⚠️ **Not:** Bazı platformlar coğrafi kısıtlamalar veya oturum gereksinimleri nedeniyle çalışmayabilir.

---

## 🌍 Desteklenen Diller

OpenAI Whisper API, **98+ dili** otomatik olarak algılar ve transkript eder:

<details>
<summary><strong>Tam Dil Listesi (Tıklayın)</strong></summary>

| Dil | Kod | Dil | Kod |
|-----|-----|-----|-----|
| Türkçe | tr | English | en |
| Deutsch | de | Français | fr |
| Español | es | Italiano | it |
| Português | pt | Nederlands | nl |
| Русский | ru | 日本語 | ja |
| 中文 | zh | 한국어 | ko |
| العربية | ar | हिन्दी | hi |
| Ελληνικά | el | Polski | pl |
| Svenska | sv | Norsk | no |
| Dansk | da | Suomi | fi |
| Čeština | cs | Magyar | hu |
| Română | ro | Български | bg |
| Українська | uk | עברית | he |
| ไทย | th | Tiếng Việt | vi |
| Bahasa Indonesia | id | Bahasa Melayu | ms |
| Afrikaans | af | Català | ca |

*Ve daha fazlası...*

</details>

> 📌 **Not:** Uygulama dili otomatik algılar. Dil belirtmenize gerek yoktur!

---

## ⚙️ Komut Satırı Parametreleri

| Parametre | Kısa | Açıklama | Varsayılan |
|-----------|------|----------|------------|
| `input_file` | - | Ses dosyası yolu veya video URL'si | İnteraktif |
| `--output` | `-o` | Çıkış dosyası yolu | `[dosya_adı]_transkript.txt` |
| `--api-key` | - | OpenAI API anahtarı | `.env` veya ortam değişkeni |
| `--no-save` | - | Sadece konsola yazdır | `False` |
| `--chunk-length` | - | Parça uzunluğu (dakika) | `5` |
| `--max-workers` | - | Paralel işlem sayısı | `3` |
| `--max-chunk-size` | - | Maksimum parça boyutu (MB) | `20` |

---

## 📊 Örnek Çıktı

```
TikTok URL'si algılandı!
TikTok videosundan ses indiriliyor...
Ses dosyası indirildi: Örnek Video Başlığı
Ses dosyası WAV formatına dönüştürülüyor...
Ses dosyası süresi: 3.45 dakika
Parça 1/1 işleniyor...
Parça 1/1 tamamlandı.

==================================================
TRANSKRİPT: Örnek Video Başlığı
==================================================
Merhaba arkadaşlar, bugün sizlerle harika bir
konuyu paylaşacağım...
==================================================

Transkripti dosyaya kaydetmek istiyor musunuz? (E/H): E
Dosya yolunu girin (örnek: C:\Users\botyum\Desktop):
```

---

## 📋 Bağımlılıklar

| Paket | Versiyon | Açıklama |
|-------|----------|----------|
| `openai` | ≥1.12.0 | OpenAI Whisper API istemcisi |
| `pydub` | ≥0.25.1 | Ses dosyası işleme |
| `python-dotenv` | ≥1.0.0 | Ortam değişkenleri yönetimi |
| `yt-dlp` | ≥2024.1.0 | Video indirme kütüphanesi |

> 📌 **yt-dlp Güncellemesi:** URL desteği için yt-dlp'yi güncel tutun: `pip install -U yt-dlp`

---

## ⚠️ Önemli Notlar

### Maliyet
- OpenAI Whisper API kullanımı **ücretlidir**
- Güncel fiyatlandırma: [OpenAI Pricing](https://openai.com/pricing)
- Whisper API: **$0.006 / dakika**

### Kısıtlamalar
- OpenAI API dosya boyutu limiti: **25 MB** (otomatik parçalama ile aşılır)
- Büyük dosyalar için işlem süresi uzayabilir
- Bazı video platformları coğrafi kısıtlamalar uygulayabilir

### Güvenlik
- API anahtarınızı asla paylaşmayın veya Git'e commit etmeyin
- `.env` dosyası `.gitignore` içinde tanımlıdır

---

## 📄 Lisans

Bu proje **PolyForm Noncommercial License 1.0.0** altında lisanslanmıştır.

- ✅ Kişisel kullanım
- ✅ Eğitim amaçlı kullanım
- ✅ Araştırma ve deney
- ❌ Ticari kullanım (izin gerektirir)

Detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

## 👥 Katkıda Bulunma

1. Bu depoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request açın

---
## ⚠️ Yasal Bilgilendirme

> "Bu proje, **Prodyum Teknoloji LTD.** şirketi bünyesinde çalıştığım süre içerisinde geliştirdiğim bir çalışmadır. Şirketin onayı ve rızası dahilinde portfolyo ve açık kaynak paylaşımı amacıyla yayınlanmıştır. Ticari amaçla kullanımı, kopyalanması veya ticari bir ürüne entegre edilmesi için şirket ile iletişime geçilmesi gerekmektedir."

## 📞 İletişim

**PRODYUM BİLİŞİM YAZILIM TEKNOLOJİLERİ VE SANAT ÜRÜNLERİ  
DANIŞMANLIK EĞİTİM SANAYİ TİCARET LİMİTED ŞİRKETİ**

📧 E-posta: [info@prodyum.com](mailto:info@prodyum.com)

---

<div align="center">

**Made with ❤️ by Prodyum**

</div>
