from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import edge_tts
import os

app = FastAPI(title="Open TTS Studio - Neural Edition", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Voces neuronales de alta calidad (Masculinas y Femeninas)
AVAILABLE_VOICES = [
    {"id": "es-MX-JorgeNeural", "name": "Español (México) - Masculina (Profunda y Cinematográfica)"},
    {"id": "es-ES-AlvaroNeural", "name": "Español (España) - Masculina (Narrador de Terror Clásico)"},
    {"id": "es-MX-JorgeNeural", "name": "Español (México) - Masculina (Profunda/Seria)"},
    {"id": "es-MX-DaliaNeural", "name": "Español (México) - Femenina (Natural)"},
    {"id": "es-MX-LucianoNeural", "name": "Español (México) - Masculina (Joven/Dinámica)"},
    {"id": "es-AR-TomasNeural", "name": "Español (Argentina) - Masculina (Acento Rioplatense)"},
    {"id": "es-ES-AlvaroNeural", "name": "Español (España) - Masculina (Narrador Solemne)"},
    {"id": "es-ES-ElviraNeural", "name": "Español (España) - Femenina (Clara/Profesional)"},
    {"id": "es-CO-GonzaloNeural", "name": "Español (Colombia) - Masculina (Cercana/Amigable)"},
    {"id": "en-US-ChristopherNeural", "name": "Inglés (EE.UU.) - Masculina (Cine/Grave)"},
    {"id": "en-US-AriaNeural", "name": "Inglés (EE.UU.) - Femenina (Profesional)"},
    {"id": "es-MX-ReynaNeural", "name": "Español (México) - Femenina (Firme y Profesional)"},
    {"id": "es-US-AlonsoNeural", "name": "Español (EE.UU.) - Masculina (Voz Neutra / Corporativa)"},
    {"id": "es-MX-DarioNeural", "name": "Español (México) - Masculina (Voz de Niño / Joven Serio)"},
    {"id": "es-MX-YuritziNeural", "name": "Español (México) - Femenina (Voz de Niña / Clara y Dramática)"}
]
class TTSRequest(BaseModel):
    text: str
    voice: str = "es-MX-JorgeNeural"

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    html_path = os.path.abspath("../frontend/index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h3>Error: No se encontró el index.html</h3>"

@app.get("/voices")
def get_voices():
    return {"voices": AVAILABLE_VOICES}

@app.post("/generate-audio")
async def generate_audio(request: TTSRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="El texto no puede estar vacío.")
    
    valid_voices = [v["id"] for v in AVAILABLE_VOICES]
    voice = request.voice if request.voice in valid_voices else "es-MX-JorgeNeural"
    
    output_filename = "output.mp3"
    
    try:
        # Generar audio neuronal de alta calidad con Edge TTS
        communicate = edge_tts.Communicate(request.text, voice)
        await communicate.save(output_filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el motor neuronal: {str(e)}")
    
    if os.path.exists(output_filename):
        return FileResponse(output_filename, media_type="audio/mpeg", filename="audio_neuronal.mp3")
    
    raise HTTPException(status_code=500, detail="No se pudo crear el archivo de audio.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)