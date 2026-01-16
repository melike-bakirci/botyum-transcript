# Ses Dosyası ve Video URL Transkript Uygulaması

Bu konsol uygulaması, .opus ve .mp3 formatındaki ses dosyalarını veya YouTube, TikTok gibi platformlardan video URL'lerini metne (transkript) çevirir. OpenAI Whisper API kullanılarak geliştirilmiştir.

## Kurulum

1. Python 3.8 veya üzeri sürümün yüklü olduğundan emin olun.

2. Gerekli kütüphaneleri yükleyin:
```bash
pip install -r requirements.txt
```

3. FFmpeg'i yükleyin (ses dosyası dönüştürme için gerekli):
   - **Windows**: [FFmpeg İndirme Sayfası](https://ffmpeg.org/download.html) veya `choco install ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt-get install ffmpeg` (Ubuntu/Debian) veya `sudo yum install ffmpeg` (CentOS/RHEL)

4. OpenAI API anahtarınızı ayarlayın (otomatik yükleme için):
   - Proje kök dizininde `.env` dosyası oluşturun ve içine şunu yazın:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```
   - Veya ortam değişkeni olarak: `set OPENAI_API_KEY=your_api_key_here` (Windows) veya `export OPENAI_API_KEY=your_api_key_here` (Linux/macOS)
   - Veya komut satırında `--api-key` parametresi ile

## Kullanım

### Temel Kullanım (Ses Dosyası)

```bash
python main.py dosya.mp3
```

### Video URL ile Kullanım

```bash
# YouTube
python main.py https://youtu.be/VIDEO_ID
python main.py https://www.youtube.com/watch?v=VIDEO_ID

# TikTok
python main.py https://www.tiktok.com/@kullanici/video/123456789

# Diğer desteklenen platformlar
python main.py https://www.instagram.com/reel/VIDEO_ID
python main.py https://vimeo.com/VIDEO_ID
```

### Çıkış Dosyası Belirtme

```bash
python main.py dosya.opus --output transkript.txt
python main.py https://youtu.be/VIDEO_ID --output transkript.txt
```

### API Anahtarı ile

```bash
python main.py dosya.mp3 --api-key YOUR_API_KEY
```

### Sadece Konsola Yazdırma (Dosyaya Kaydetme)

```bash
python main.py dosya.mp3 --no-save
```

## Desteklenen Formatlar

### Ses Dosyaları
- .mp3
- .opus
- .wav
- .m4a
- .flac
- .ogg
- .mp4

### Video Platformları
- YouTube (youtube.com, youtu.be)
- TikTok
- Instagram
- Facebook
- Twitter/X
- Vimeo
- Dailymotion
- Ve yt-dlp tarafından desteklenen diğer platformlar

## Özellikler

- Otomatik ses formatı dönüştürme (WAV formatına)
- **Video URL desteği** (YouTube, TikTok vb.)
- Otomatik dil algılama
- Konsol çıktısı ve dosyaya kaydetme seçenekleri
- Büyük dosyalar için otomatik parçalama
- Paralel transkript işleme
- Geçici dosyaların otomatik temizlenmesi

## Notlar

- OpenAI API kullanımı ücretlidir. Kullanım maliyetleri için [OpenAI Fiyatlandırma](https://openai.com/pricing) sayfasını kontrol edin.
- Büyük ses dosyaları için işlem süresi uzayabilir.
- Video indirme için FFmpeg gereklidir.
- yt-dlp kütüphanesi video indirme için kullanılır ve düzenli olarak güncellenmesi önerilir: `pip install -U yt-dlp`

