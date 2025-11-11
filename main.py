#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ses Dosyası Transkript Uygulaması
.opus ve .mp3 formatındaki ses dosyalarını metne çevirir.
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from openai import OpenAI
    import pydub
except ImportError as e:
    print(f"HATA: Gerekli kütüphane eksik: {e}")
    print("Lütfen 'pip install -r requirements.txt' komutunu çalıştırın.")
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


def transcribe_audio(audio_path: str, api_key: str = None) -> str:
    """
    Ses dosyasını OpenAI Whisper API kullanarak metne çevirir.
    
    Args:
        audio_path: Ses dosyası yolu
        api_key: OpenAI API anahtarı (opsiyonel, ortam değişkeninden alınabilir)
    
    Returns:
        Transkript edilmiş metin
    """
    # API anahtarını kontrol et
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("HATA: OpenAI API anahtarı bulunamadı.")
        print("Lütfen OPENAI_API_KEY ortam değişkenini ayarlayın veya --api-key parametresini kullanın.")
        sys.exit(1)
    
    client = OpenAI(api_key=api_key)
    
    try:
        print(f"Ses dosyası işleniyor: {audio_path}")
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="tr"  # Türkçe için
            )
        return transcript.text
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


def main():
    parser = argparse.ArgumentParser(
        description="Ses dosyalarını (.opus, .mp3) metne çevirir",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python main.py dosya.mp3
  python main.py dosya.opus --output transkript.txt
  python main.py dosya.mp3 --api-key YOUR_API_KEY
        """
    )
    
    parser.add_argument(
        "input_file",
        type=str,
        help="Transkript edilecek ses dosyası (.opus veya .mp3)"
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
    
    args = parser.parse_args()
    
    # Giriş dosyasını kontrol et
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"HATA: Dosya bulunamadı: {args.input_file}")
        sys.exit(1)
    
    # Dosya uzantısını kontrol et
    if input_path.suffix.lower() not in ['.opus', '.mp3', '.wav', '.m4a', '.flac']:
        print(f"UYARI: Desteklenen formatlar: .opus, .mp3, .wav, .m4a, .flac")
        print(f"Yüklenen dosya: {input_path.suffix}")
    
    # Geçici WAV dosyası oluştur (gerekirse)
    audio_path = str(input_path)
    temp_wav = None
    
    if input_path.suffix.lower() in ['.opus', '.mp3', '.m4a', '.flac']:
        print("Ses dosyası WAV formatına dönüştürülüyor...")
        temp_wav = convert_audio_to_wav(audio_path)
        audio_path = temp_wav
    
    try:
        # Transkript işlemi
        transcript = transcribe_audio(audio_path, args.api_key)
        
        # Sonuçları göster
        print("\n" + "="*50)
        print("TRANSKRİPT:")
        print("="*50)
        print(transcript)
        print("="*50 + "\n")
        
        # Dosyaya kaydet (eğer --no-save kullanılmadıysa)
        if not args.no_save:
            if args.output:
                output_path = args.output
            else:
                output_path = str(input_path.with_suffix('')) + "_transkript.txt"
            save_transcript(transcript, output_path)
    
    finally:
        # Geçici WAV dosyasını temizle
        if temp_wav and os.path.exists(temp_wav):
            try:
                os.remove(temp_wav)
                print(f"Geçici dosya temizlendi: {temp_wav}")
            except:
                pass


if __name__ == "__main__":
    main()

