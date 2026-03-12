"""
Konuşma → Metin Dönüştürücü — OpenAI Whisper API
Ses kaydını otomatik olarak Türkçe metne çevirir.
"""

import os
import tempfile
import base64


def transcribe_audio(audio_base64: str) -> dict:
    """
    Base64 kodlu ses kaydını Whisper API ile Türkçe metne çevirir.
    
    Returns:
        dict: {"success": bool, "text": str, "duration": float, "error": str}
    """
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("OPENAI_API_KEY", "")
        except Exception:
            pass
    
    if not api_key:
        return {
            "success": False,
            "text": "",
            "duration": 0,
            "error": "OPENAI_API_KEY bulunamadı. Lütfen ortam değişkenlerini kontrol edin."
        }
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Base64'ten binary'ye çevir
        audio_bytes = base64.b64decode(audio_base64)
        
        # Geçici dosya oluştur (Whisper API dosya ister)
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        
        try:
            # Whisper API ile transkripsiyon
            with open(tmp_path, "rb") as audio_file:
                result = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="tr",
                    response_format="verbose_json",
                    prompt="Bu bir Türk ilkokul veya ortaokul öğrencisinin sesli okuma kaydıdır."
                )
            
            text = result.text if hasattr(result, 'text') else str(result)
            duration = result.duration if hasattr(result, 'duration') else 0
            
            return {
                "success": True,
                "text": text.strip(),
                "duration": duration,
                "error": ""
            }
        finally:
            # Geçici dosyayı temizle
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
    
    except Exception as e:
        return {
            "success": False,
            "text": "",
            "duration": 0,
            "error": f"Whisper API hatası: {str(e)}"
        }
