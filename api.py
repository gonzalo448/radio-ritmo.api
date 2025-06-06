from fastapi import FastAPI
import requests
import os

CENTOVACAST_API_URL = "https://estructuraweb.com.co:2199/rpc/ritmo/streaminfo.get"
STREAMING_URL = "https://estructuraweb.com.co:9309/live"
COVERS_DIR = "/home/root/api_radio/covers"

# Crear la aplicación FastAPI
app = FastAPI()

@app.get("/musica")
async def obtener_metadatos():
    """Obtiene los metadatos de CentovaCast y devuelve la información de la canción en reproducción."""
    try:
        respuesta = requests.get(CENTOVACAST_API_URL)
        if respuesta.status_code == 200:
            datos = respuesta.json()

            # Verificar si "data" existe y tiene contenido
            if "data" in datos and isinstance(datos["data"], list) and datos["data"]:
                track = datos["data"][0].get("track", {})
            else:
                return {"error": "La API de CentovaCast no devolvió datos válidos."}

            artist = track.get("artist", "Desconocido")
            title = track.get("title", "Desconocido")
            album = track.get("album", "No disponible")
            imageurl = track.get("imageurl", None)
            tuneinurl = datos["data"][0].get("tuneinurl", STREAMING_URL)

            # Nombre de archivo seguro para la carátula
            filename = f"{artist}-{title}.jpg".replace(" ", "_")
            manual_path = os.path.join(COVERS_DIR, "manual", filename)
            downloaded_path = os.path.join(COVERS_DIR, filename)

            # URL por defecto de carátula
            cover_url = "https://api.radioritmonline.com/covers/default.jpg"

            # Verificar imagen manual primero
            if os.path.exists(manual_path):
                cover_url = f"https://api.radioritmonline.com/covers/manual/{filename}"
            elif os.path.exists(downloaded_path):
                cover_url = f"https://api.radioritmonline.com/covers/{filename}"
            elif imageurl:
                try:
                    img_res = requests.get(imageurl)
                    if img_res.status_code == 200:
                        with open(downloaded_path, "wb") as img_file:
                            img_file.write(img_res.content)
                        cover_url = f"https://api.radioritmonline.com/covers/{filename}"
                except Exception as e:
                    print(f"⚠️ Error al descargar imagen: {str(e)}")

            return {
                "artist": artist,
                "title": title,
                "album": album,
                "cover": cover_url,
                "streaming_url": tuneinurl
            }
        else:
            return {"error": f"Error al obtener datos: Código {respuesta.status_code}"}
    except Exception as e:
        return {"error": f"Error de conexión: {str(e)}"}

@app.get("/stream")
async def obtener_stream():
    """Devuelve solo la URL del streaming de audio."""
    return {"streaming_url": STREAMING_URL}
