# Ses Dosyası Transkript Uygulaması

Bu konsol uygulaması, .opus ve .mp3 formatındaki ses dosyalarını metne (transkript) çevirir. OpenAI Whisper API kullanılarak geliştirilmiştir.

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

4. OpenAI API anahtarınızı ayarlayın:
   - Ortam değişkeni olarak: `set OPENAI_API_KEY=your_api_key_here` (Windows) veya `export OPENAI_API_KEY=your_api_key_here` (Linux/macOS)
   - Veya komut satırında `--api-key` parametresi ile

## Kullanım

### Temel Kullanım

```bash
python main.py dosya.mp3
```

### Çıkış Dosyası Belirtme

```bash
python main.py dosya.opus --output transkript.txt
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

- .mp3
- .opus
- .wav
- .m4a
- .flac

## Özellikler

- Otomatik ses formatı dönüştürme (WAV formatına)
- Türkçe dil desteği
- Konsol çıktısı ve dosyaya kaydetme seçenekleri
- Geçici dosyaların otomatik temizlenmesi

## Notlar

- OpenAI API kullanımı ücretlidir. Kullanım maliyetleri için [OpenAI Fiyatlandırma](https://openai.com/pricing) sayfasını kontrol edin.
- Büyük ses dosyaları için işlem süresi uzayabilir.

