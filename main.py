#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ses Dosyası ve Video URL Transkript Uygulaması
.opus ve .mp3 formatındaki ses dosyalarını veya YouTube/TikTok gibi platformlardan
video URL'lerini metne çevirir.
"""

import argparse
import os
import re
import sys
import tempfile
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Python 3.13+ için audioop workaround
try:
    import audioop
except ImportError:
    # audioop modülü Python 3.13'te kaldırıldı
    # pydub için mock modül oluştur
    import types
    
    def _audioop_passthrough(fragment, width):
        """Basit passthrough fonksiyonu - veriyi olduğu gibi döndürür"""
        return fragment
    
    def _audioop_mul(fragment, width, factor):
        """Ses seviyesini çarpar - basit implementasyon"""
        return fragment
    
    def _audioop_add(fragment1, fragment2, width):
        """İki ses parçasını toplar - basit implementasyon"""
        return fragment1
    
    def _audioop_tomono(fragment, width, lfactor, rfactor):
        """Stereo'dan mono'ya dönüştürür"""
        return fragment
    
    def _audioop_tostereo(fragment, width, lfactor, rfactor):
        """Mono'dan stereo'ya dönüştürür"""
        return fragment + fragment
    
    def _audioop_bias(fragment, width, bias):
        """Bias ekler"""
        return fragment
    
    def _audioop_reverse(fragment, width):
        """Ses parçasını ters çevirir"""
        return fragment[::-1]
    
    def _audioop_byteswap(fragment, width):
        """Byte sırasını değiştirir"""
        return fragment
    
    def _audioop_lin2lin(fragment, width, newwidth):
        """Farklı genişlikler arasında dönüştürür"""
        return fragment
    
    def _audioop_ratecv(fragment, width, nchannels, inrate, outrate, state, weightA, weightB):
        """Örnekleme hızını değiştirir"""
        return fragment, state
    
    def _audioop_lin2ulaw(fragment, width):
        """Linear'dan u-law'a dönüştürür"""
        return fragment
    
    def _audioop_ulaw2lin(fragment, width):
        """u-law'dan linear'a dönüştürür"""
        return fragment
    
    def _audioop_lin2alaw(fragment, width):
        """Linear'dan A-law'a dönüştürür"""
        return fragment
    
    def _audioop_alaw2lin(fragment, width):
        """A-law'dan linear'a dönüştürür"""
        return fragment
    
    def _audioop_lin2adpcm(fragment, width, state):
        """Linear'dan ADPCM'e dönüştürür"""
        return fragment, state
    
    def _audioop_adpcm2lin(fragment, width, state):
        """ADPCM'den linear'a dönüştürür"""
        return fragment, state
    
    # Mock modülü oluştur
    audioop = types.ModuleType('audioop')
    audioop.mul = _audioop_mul
    audioop.add = _audioop_add
    audioop.tomono = _audioop_tomono
    audioop.tostereo = _audioop_tostereo
    audioop.bias = _audioop_bias
    audioop.reverse = _audioop_reverse
    audioop.byteswap = _audioop_byteswap
    audioop.lin2lin = _audioop_lin2lin
    audioop.ratecv = _audioop_ratecv
    audioop.lin2ulaw = _audioop_lin2ulaw
    audioop.ulaw2lin = _audioop_ulaw2lin
    audioop.lin2alaw = _audioop_lin2alaw
    audioop.alaw2lin = _audioop_alaw2lin
    audioop.lin2adpcm = _audioop_lin2adpcm
    audioop.adpcm2lin = _audioop_adpcm2lin
    sys.modules['audioop'] = audioop

try:
    from openai import OpenAI
    import pydub
    from dotenv import load_dotenv
except ImportError as e:
    print(f"HATA: Gerekli kütüphane eksik: {e}")
    print("Lütfen 'pip install -r requirements.txt' komutunu çalıştırın.")
    sys.exit(1)

# .env dosyasından ortam değişkenlerini yükle
def load_env_safe():
    """Güvenli bir şekilde .env dosyasını yükler, farklı encoding'leri dener."""
    if not os.path.exists('.env'):
        return False
    
    encodings = ['utf-8', 'utf-8-sig', 'utf-16', 'utf-16-le', 'utf-16-be', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open('.env', 'r', encoding=encoding) as f:
                for line in f:
                    line = line.strip()
                    # Boş satırları ve yorumları atla
                    if not line or line.startswith('#'):
                        continue
                    # KEY=VALUE formatını parse et
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # Tırnak işaretlerini temizle
                        if (value.startswith('"') and value.endswith('"')) or \
                           (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]
                        # Ortam değişkenine ekle (sadece henüz tanımlı değilse)
                        if key and key not in os.environ:
                            os.environ[key] = value
                return True
        except UnicodeDecodeError:
            continue
        except Exception:
            # Diğer hatalar için bir sonraki encoding'i dene
            continue
    
    # Hiçbir encoding çalışmadıysa
    return False

# Önce standart load_dotenv'i dene
try:
    load_dotenv()
except (UnicodeDecodeError, FileNotFoundError):
    # Hata durumunda güvenli yükleme fonksiyonunu kullan
    load_env_safe()

# yt-dlp kütüphanesini opsiyonel olarak yükle
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False
    print("UYARI: yt-dlp kütüphanesi yüklü değil. URL desteği devre dışı.")
    print("Yüklemek için: pip install yt-dlp")


def is_url(input_string: str) -> bool:
    """
    Verilen string'in bir URL olup olmadığını kontrol eder.
    
    Args:
        input_string: Kontrol edilecek string
    
    Returns:
        URL ise True, değilse False
    """
    # URL pattern'leri
    url_patterns = [
        r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'https?://youtu\.be/[\w-]+',
        r'https?://(?:www\.)?tiktok\.com/@[\w.-]+/video/\d+',
        r'https?://(?:www\.)?instagram\.com/(?:p|reel)/[\w-]+',
        r'https?://(?:www\.)?facebook\.com/[\w.-]+/videos/\d+',
        r'https?://(?:www\.)?twitter\.com/[\w]+/status/\d+',
        r'https?://(?:www\.)?x\.com/[\w]+/status/\d+',
        r'https?://(?:www\.)?vimeo\.com/\d+',
        r'https?://(?:www\.)?dailymotion\.com/video/[\w]+',
        r'https?://[\w.-]+\.[\w]{2,}(?:/[\w./?%&=-]*)?',  # Genel URL pattern
    ]
    
    input_string = input_string.strip()
    
    for pattern in url_patterns:
        if re.match(pattern, input_string, re.IGNORECASE):
            return True
    
    # Basit URL kontrolü
    if input_string.startswith(('http://', 'https://')):
        return True
    
    return False


def get_platform_name(url: str) -> str:
    """
    URL'den platform adını çıkarır.
    
    Args:
        url: Video URL'si
    
    Returns:
        Platform adı (örn. 'YouTube', 'TikTok')
    """
    url_lower = url.lower()
    
    if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'YouTube'
    elif 'tiktok.com' in url_lower:
        return 'TikTok'
    elif 'instagram.com' in url_lower:
        return 'Instagram'
    elif 'facebook.com' in url_lower:
        return 'Facebook'
    elif 'twitter.com' in url_lower or 'x.com' in url_lower:
        return 'Twitter/X'
    elif 'vimeo.com' in url_lower:
        return 'Vimeo'
    elif 'dailymotion.com' in url_lower:
        return 'Dailymotion'
    else:
        return 'Video'


def download_audio_from_url(url: str, output_dir: str = None) -> tuple:
    """
    Verilen URL'den sesi indirir.
    
    Args:
        url: Video URL'si
        output_dir: İndirme dizini (opsiyonel, varsayılan: temp dizin)
    
    Returns:
        (audio_path, video_title) tuple
    """
    if not YT_DLP_AVAILABLE:
        print("HATA: yt-dlp kütüphanesi yüklü değil.")
        print("Yüklemek için: pip install yt-dlp")
        sys.exit(1)
    
    if output_dir is None:
        output_dir = tempfile.gettempdir()
    
    platform = get_platform_name(url)
    print(f"{platform} videosundan ses indiriliyor...")
    
    # İndirmeden önce temp dizinindeki mevcut dosyaları listele
    existing_files = set(os.listdir(output_dir)) if os.path.exists(output_dir) else set()
    
    # Benzersiz bir ID oluştur (dosya adı çakışmalarını önlemek için)
    unique_id = str(int(time.time() * 1000))
    
    # yt-dlp ayarları
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, f'audio_{unique_id}_%(id)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'verbose': False,
        'ignoreerrors': False,
        'noprogress': True,
        'logger': None,  # Tüm log mesajlarını devre dışı bırak
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Video bilgilerini al ve indir
            info = ydl.extract_info(url, download=True)
            
            video_title = info.get('title', 'video')
            video_id = info.get('id', 'unknown')
            
            # İndirilen dosyayı bul - yt-dlp'den dönen bilgiyi kullan
            expected_filename = f"audio_{unique_id}_{video_id}.mp3"
            audio_path = os.path.join(output_dir, expected_filename)
            
            # Dosya var mı kontrol et
            if os.path.exists(audio_path):
                print(f"Ses dosyası indirildi: {video_title}")
                return audio_path, video_title
            
            # Yoksa temp dizininde yeni eklenen dosyaları bul
            current_files = set(os.listdir(output_dir))
            new_files = current_files - existing_files
            
            # Yeni dosyalar arasından ses dosyasını bul
            audio_extensions = ['.mp3', '.m4a', '.webm', '.opus', '.wav', '.ogg']
            for new_file in new_files:
                file_lower = new_file.lower()
                if any(file_lower.endswith(ext) for ext in audio_extensions):
                    if unique_id in new_file or video_id in new_file:
                        audio_path = os.path.join(output_dir, new_file)
                        if os.path.exists(audio_path):
                            print(f"Ses dosyası indirildi: {video_title}")
                            return audio_path, video_title
            
            # Hala bulunamadıysa, glob ile ara
            import glob
            patterns = [
                os.path.join(output_dir, f"audio_{unique_id}_*.*"),
                os.path.join(output_dir, f"*{video_id}*.mp3"),
                os.path.join(output_dir, f"*{video_id}*.m4a"),
            ]
            
            for pattern in patterns:
                matches = glob.glob(pattern)
                if matches:
                    audio_path = matches[0]
                    if os.path.exists(audio_path):
                        print(f"Ses dosyası indirildi: {video_title}")
                        return audio_path, video_title
            
            # Son çare: dizindeki en son oluşturulan ses dosyasını bul
            all_audio_files = []
            for ext in audio_extensions:
                all_audio_files.extend(glob.glob(os.path.join(output_dir, f"*{ext}")))
            
            if all_audio_files:
                # En son değiştirilen dosyayı bul
                latest_file = max(all_audio_files, key=os.path.getmtime)
                # Son 10 saniye içinde oluşturulmuş mu kontrol et
                if time.time() - os.path.getmtime(latest_file) < 10:
                    print(f"Ses dosyası indirildi: {video_title}")
                    return latest_file, video_title
            
            print(f"HATA: İndirilen dosya bulunamadı.")
            print(f"Beklenen yol: {audio_path}")
            print(f"Yeni dosyalar: {new_files}")
            sys.exit(1)
                
    except Exception as e:
        print(f"HATA: Video indirilirken hata oluştu: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def convert_audio_to_wav(input_path: str, output_path: str = None) -> str:
    """
    Ses dosyasını WAV formatına dönüştürür.
    
    Args:
        input_path: Giriş ses dosyası yolu
        output_path: Çıkış WAV dosyası yolu (opsiyonel)
    
    Returns:
        WAV dosyasının yolu
    """
    if output_path is None:
        output_path = str(Path(input_path).with_suffix('.wav'))
    
    try:
        audio = pydub.AudioSegment.from_file(input_path)
        audio.export(output_path, format="wav")
        return output_path
    except Exception as e:
        print(f"HATA: Ses dosyası dönüştürülürken hata oluştu: {e}")
        sys.exit(1)


def get_chunk_size_mb(chunk_path: str) -> float:
    """
    Parça dosyasının boyutunu MB cinsinden döndürür.
    
    Args:
        chunk_path: Parça dosyası yolu
    
    Returns:
        Dosya boyutu (MB)
    """
    try:
        size_bytes = os.path.getsize(chunk_path)
        return size_bytes / (1024 * 1024)
    except:
        return 0


def split_audio_file(audio_path: str, chunk_length_minutes: int = 5, max_size_mb: float = 20.0) -> list:
    """
    Büyük ses dosyasını parçalara böler.
    Parça boyutu 25MB limitini aşmaması için dinamik olarak ayarlanır.
    
    Args:
        audio_path: Ses dosyası yolu
        chunk_length_minutes: Her parçanın uzunluğu (dakika cinsinden)
        max_size_mb: Maksimum parça boyutu (MB, varsayılan: 20MB, limit: 25MB)
    
    Returns:
        Parça dosya yollarının listesi
    """
    try:
        audio = pydub.AudioSegment.from_file(audio_path)
        chunk_length_ms = chunk_length_minutes * 60 * 1000  # Dakikayı milisaniyeye çevir
        total_length_ms = len(audio)
        
        # Eğer dosya parçalara bölünmeyecek kadar kısaysa, direkt döndür
        if total_length_ms <= chunk_length_ms:
            # Tek dosya için boyut kontrolü yap
            file_size_mb = get_chunk_size_mb(audio_path)
            if file_size_mb > max_size_mb:
                print(f"UYARI: Dosya boyutu ({file_size_mb:.2f}MB) limiti aşıyor. Parçalara bölünüyor...")
            else:
                return [audio_path]
        
        chunks = []
        temp_dir = tempfile.gettempdir()
        base_name = Path(audio_path).stem
        
        # Dosyayı parçalara böl
        start = 0
        chunk_index = 0
        current_chunk_length_ms = chunk_length_ms
        
        while start < total_length_ms:
            end = min(start + current_chunk_length_ms, total_length_ms)
            chunk = audio[start:end]
            
            # Geçici dosya oluştur
            chunk_path = os.path.join(temp_dir, f"{base_name}_chunk_{chunk_index:03d}.wav")
            chunk.export(chunk_path, format="wav")
            
            # Parça boyutunu kontrol et
            chunk_size_mb = get_chunk_size_mb(chunk_path)
            
            # Eğer parça çok büyükse, boyutu küçült ve tekrar dene
            if chunk_size_mb > max_size_mb:
                os.remove(chunk_path)  # Büyük parçayı sil
                
                # Parça uzunluğunu yarıya indir
                current_chunk_length_ms = int(current_chunk_length_ms * 0.5)
                if current_chunk_length_ms < 30000:  # 30 saniyeden az olmasın
                    current_chunk_length_ms = 30000
                
                print(f"UYARI: Parça {chunk_index+1} çok büyük ({chunk_size_mb:.2f}MB). Parça uzunluğu {current_chunk_length_ms/60000:.1f} dakikaya düşürülüyor...")
                continue  # Aynı başlangıç noktasından tekrar dene
            
            chunks.append(chunk_path)
            start = end
            chunk_index += 1
            
            # Başarılı parça oluşturulduktan sonra varsayılan uzunluğa geri dön
            if current_chunk_length_ms < chunk_length_ms:
                current_chunk_length_ms = chunk_length_ms
        
        return chunks
    except Exception as e:
        print(f"HATA: Ses dosyası parçalara bölünürken hata oluştu: {e}")
        sys.exit(1)


def transcribe_chunk(chunk_path: str, chunk_index: int, total_chunks: int, api_key: str, max_retries: int = 3) -> tuple:
    """
    Tek bir parçayı transkript eder (paralel işleme için).
    Retry mekanizması ile bağlantı hatalarını yönetir.
    
    Args:
        chunk_path: Parça dosyası yolu
        chunk_index: Parça indeksi (0-based)
        total_chunks: Toplam parça sayısı
        api_key: OpenAI API anahtarı
        max_retries: Maksimum deneme sayısı (varsayılan: 3)
    
    Returns:
        (chunk_index, transcript_text) tuple
    """
    client = OpenAI(api_key=api_key)
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                wait_time = min(2 ** attempt, 10)  # Exponential backoff, max 10 saniye
                print(f"Parça {chunk_index+1}/{total_chunks} tekrar deneniyor (deneme {attempt+1}/{max_retries})...")
                time.sleep(wait_time)
            else:
                print(f"Parça {chunk_index+1}/{total_chunks} işleniyor...")
            
            with open(chunk_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            print(f"Parça {chunk_index+1}/{total_chunks} tamamlandı.")
            return (chunk_index, transcript.text)
        except Exception as e:
            error_str = str(e)
            # 413 hatası (dosya çok büyük) için retry yapma
            if "413" in error_str or "Maximum content size" in error_str:
                print(f"HATA: Parça {chunk_index+1} çok büyük (25MB limiti aşıldı). Bu parça atlanıyor.")
                return (chunk_index, f"[Parça {chunk_index+1} çok büyük, işlenemedi]")
            
            # Son denemede hata döndür
            if attempt == max_retries - 1:
                print(f"HATA: Parça {chunk_index+1} {max_retries} denemeden sonra işlenemedi: {e}")
                return (chunk_index, f"[Parça {chunk_index+1} işlenemedi: {str(e)}]")
            
            # Connection error için retry yap
            if "Connection" in error_str or "timeout" in error_str.lower():
                continue  # Retry yap
    
    # Buraya gelmemeli ama yine de güvenlik için
    return (chunk_index, f"[Parça {chunk_index+1} işlenemedi]")


def transcribe_audio(audio_path: str, api_key: str = None, chunk_length_minutes: int = 5, max_workers: int = None, max_chunk_size_mb: float = 20.0) -> str:
    """
    Ses dosyasını OpenAI Whisper API kullanarak metne çevirir.
    Büyük dosyalar otomatik olarak parçalara bölünür ve birleştirilir.
    Dil otomatik olarak algılanır ve ses dosyasındaki dilde transkript edilir.
    Parçalar paralel olarak işlenir, bu da işlem süresini önemli ölçüde kısaltır.
    
    Args:
        audio_path: Ses dosyası yolu
        api_key: OpenAI API anahtarı (opsiyonel, ortam değişkeninden alınabilir)
        chunk_length_minutes: Parça uzunluğu (dakika cinsinden, varsayılan: 5)
        max_workers: Paralel işlem sayısı (varsayılan: 3, connection error'ları önlemek için)
        max_chunk_size_mb: Maksimum parça boyutu (MB, varsayılan: 20MB)
    
    Returns:
        Transkript edilmiş metin (ses dosyasındaki dilde)
    """
    # API anahtarını kontrol et
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("HATA: OpenAI API anahtarı bulunamadı.")
        print("Lütfen OPENAI_API_KEY ortam değişkenini ayarlayın veya --api-key parametresini kullanın.")
        sys.exit(1)
    
    try:
        # Ses dosyasının süresini kontrol et
        audio = pydub.AudioSegment.from_file(audio_path)
        duration_minutes = len(audio) / (60 * 1000)
        
        print(f"Ses dosyası süresi: {duration_minutes:.2f} dakika")
        
        # Dosyayı parçalara böl (gerekirse)
        chunks = split_audio_file(audio_path, chunk_length_minutes, max_chunk_size_mb)
        
        if len(chunks) > 1:
            print(f"Dosya {len(chunks)} parçaya bölündü (her parça ~{chunk_length_minutes} dakika, max {max_chunk_size_mb}MB)")
            # Paralel işlem sayısını sınırla (connection error'ları önlemek için)
            if max_workers is None:
                max_workers = min(3, len(chunks))  # Varsayılan olarak max 3 paralel işlem
            print(f"Parçalar paralel olarak işlenecek (max {max_workers} eşzamanlı işlem)...")
        else:
            max_workers = 1
        
        # Geçici dosyaları takip et
        temp_chunk_files = [chunk for chunk in chunks if chunk != audio_path]
        
        # Paralel işleme için ThreadPoolExecutor kullan
        all_transcripts = [None] * len(chunks)  # Sonuçları doğru sırada saklamak için
        
        if len(chunks) == 1:
            # Tek parça varsa normal işle
            result = transcribe_chunk(chunks[0], 0, 1, api_key)
            all_transcripts[0] = result[1]
        else:
            # Birden fazla parça varsa paralel işle
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Tüm parçaları işleme gönder
                future_to_chunk = {
                    executor.submit(transcribe_chunk, chunk_path, i, len(chunks), api_key): (i, chunk_path)
                    for i, chunk_path in enumerate(chunks)
                }
                
                # Tamamlanan işlemleri topla
                for future in as_completed(future_to_chunk):
                    chunk_index, transcript_text = future.result()
                    all_transcripts[chunk_index] = transcript_text
        
        # Parçaları birleştir
        final_transcript = " ".join(all_transcripts)
        
        # Geçici parça dosyalarını temizle
        for chunk_file in temp_chunk_files:
            try:
                if os.path.exists(chunk_file):
                    os.remove(chunk_file)
            except:
                pass
        
        return final_transcript
        
    except Exception as e:
        print(f"HATA: Transkript işlemi sırasında hata oluştu: {e}")
        sys.exit(1)


def save_transcript(text: str, output_path: str):
    """
    Transkripti dosyaya kaydeder.
    
    Args:
        text: Kaydedilecek metin
        output_path: Çıkış dosyası yolu
    """
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Transkript kaydedildi: {output_path}")
    except Exception as e:
        print(f"HATA: Dosya kaydedilirken hata oluştu: {e}")
        sys.exit(1)


# ============================================
# DOSYA YOLU AYARLARI
# ============================================
# Dosya yolu artık konsoldan kullanıcıdan alınacaktır.
# ============================================


def main():
    parser = argparse.ArgumentParser(
        description="Ses dosyalarını (.opus, .mp3) veya video URL'lerini metne çevirir",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python main.py dosya.mp3
  python main.py dosya.opus --output transkript.txt
  python main.py https://youtu.be/VIDEO_ID
  python main.py https://www.tiktok.com/@user/video/123456
  python main.py dosya.mp3 --api-key YOUR_API_KEY
        """
    )
    
    parser.add_argument(
        "input_file",
        type=str,
        nargs='?',  # Opsiyonel hale getir
        default=None,
        help="Transkript edilecek ses dosyası (.opus veya .mp3) veya video URL'si"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Çıkış dosyası yolu (varsayılan: input_dosya_transkript.txt)"
    )
    
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="OpenAI API anahtarı (opsiyonel, OPENAI_API_KEY ortam değişkeninden de alınabilir)"
    )
    
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Sadece konsola yazdır, dosyaya kaydetme"
    )
    
    parser.add_argument(
        "--chunk-length",
        type=int,
        default=5,
        help="Büyük dosyalar için parça uzunluğu (dakika cinsinden, varsayılan: 5)"
    )
    
    parser.add_argument(
        "--max-workers",
        type=int,
        default=None,
        help="Paralel işlem sayısı (varsayılan: 3, connection error'ları önlemek için)"
    )
    
    parser.add_argument(
        "--max-chunk-size",
        type=float,
        default=20.0,
        help="Maksimum parça boyutu (MB, varsayılan: 20MB, limit: 25MB)"
    )
    
    args = parser.parse_args()
    
    # Giriş dosyasını belirle: önce komut satırı, yoksa kullanıcıdan sor
    input_file = args.input_file
    if input_file is None:
        print("Ses dosyasının yolunu veya video URL'sini girin:")
        print("(Örnek: C:\\Videos\\dosya.mp3 veya https://youtu.be/VIDEO_ID)")
        input_file = input().strip()
        
        # Kullanıcı boş girdi verirse hata ver
        if not input_file:
            print("HATA: Ses dosyası yolu veya URL boş olamaz.")
            print("Kullanım: python main.py dosya.mp3")
            print("          python main.py https://youtu.be/VIDEO_ID")
            print("Veya komut çalıştırıldığında dosya yolunu/URL'yi girin.")
            sys.exit(1)
    
    # URL mi yoksa dosya yolu mu kontrol et
    is_url_input = is_url(input_file)
    
    # URL'den indirilen dosyayı takip etmek için
    downloaded_audio_path = None
    video_title = None
    
    if is_url_input:
        # URL'den ses indir
        platform = get_platform_name(input_file)
        print(f"\n{platform} URL'si algılandı!")
        downloaded_audio_path, video_title = download_audio_from_url(input_file)
        input_path = Path(downloaded_audio_path)
    else:
        # Giriş dosyasını kontrol et
        input_path = Path(input_file)
        if not input_path.exists():
            print(f"HATA: Dosya bulunamadı: {input_file}")
            print(f"Lütfen dosya yolunun doğru olduğundan emin olun.")
            sys.exit(1)
        
        # Dosya uzantısını kontrol et
        if input_path.suffix.lower() not in ['.opus', '.mp3', '.wav', '.m4a', '.flac', '.ogg', '.mp4']:
            print(f"UYARI: Desteklenen formatlar: .opus, .mp3, .wav, .m4a, .flac, .ogg, .mp4")
            print(f"Yüklenen dosya: {input_path.suffix}")
    
    # Geçici WAV dosyası oluştur (gerekirse)
    audio_path = str(input_path)
    temp_wav = None
    
    if input_path.suffix.lower() in ['.opus', '.mp3', '.m4a', '.flac', '.ogg', '.mp4']:
        print("Ses dosyası WAV formatına dönüştürülüyor...")
        temp_wav = convert_audio_to_wav(audio_path)
        audio_path = temp_wav
    
    try:
        # Transkript işlemi
        transcript = transcribe_audio(audio_path, args.api_key, args.chunk_length, args.max_workers, args.max_chunk_size)
        
        # Sonuçları göster
        print("\n" + "="*50)
        if video_title:
            print(f"TRANSKRİPT: {video_title}")
        else:
            print("TRANSKRİPT:")
        print("="*50)
        print(transcript)
        print("="*50 + "\n")
        
        # Dosyaya kaydetme işlemi
        # Eğer --no-save parametresi kullanıldıysa kaydetme
        if args.no_save:
            print("Transkript kaydedilmedi (--no-save parametresi kullanıldı).")
        else:
            # Kullanıcıya kaydetmek isteyip istemediğini sor
            print("Transkripti dosyaya kaydetmek istiyor musunuz? (E/H): ", end="")
            kaydet_cevap = input().strip().upper()
            
            if kaydet_cevap in ['E', 'EVET', 'Y', 'YES']:
                # Eğer --output parametresi verildiyse onu kullan
                if args.output:
                    output_path = args.output
                else:
                    # Kullanıcıdan dosya yolunu sor
                    print("Dosya yolunu girin (örnek: C:\\Users\\botyum\\Desktop): ", end="")
                    dosya_yolu = input().strip()
                    
                    # Boş girilirse varsayılan olarak mevcut dizine kaydet
                    if not dosya_yolu:
                        dosya_yolu = str(Path.cwd())
                    
                    # Dosya yolunu Path objesine çevir
                    yol_path = Path(dosya_yolu)
                    
                    # Eğer yol bir klasör ise, dosya adını otomatik oluştur
                    if yol_path.is_dir() or not yol_path.suffix:
                        # Klasör yoluna dosya adını ekle
                        if video_title:
                            # Video başlığından güvenli dosya adı oluştur
                            safe_title = re.sub(r'[<>:"/\\|?*]', '_', video_title)
                            dosya_adi = safe_title + "_transkript.txt"
                        else:
                            dosya_adi = input_path.stem + "_transkript.txt"
                        output_path = str(yol_path / dosya_adi)
                    else:
                        # Tam dosya yolu verilmiş
                        output_path = dosya_yolu
                
                save_transcript(transcript, output_path)
            else:
                print("Transkript kaydedilmedi.")
    
    finally:
        # Geçici WAV dosyasını temizle
        if temp_wav and os.path.exists(temp_wav):
            try:
                os.remove(temp_wav)
                print(f"Geçici dosya temizlendi: {temp_wav}")
            except:
                pass
        
        # İndirilen ses dosyasını temizle
        if downloaded_audio_path and os.path.exists(downloaded_audio_path):
            try:
                os.remove(downloaded_audio_path)
                print(f"İndirilen ses dosyası temizlendi.")
            except:
                pass


if __name__ == "__main__":
    main()

