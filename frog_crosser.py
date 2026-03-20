import os

os.environ["TF_USE_LEGACY_KERAS"] = "1"

import subprocess
import numpy as np
import time
import shutil
import glob
from datetime import datetime
from PIL import Image, ImageOps

import tf_keras
from tf_keras.models import load_model
from tf_keras.layers import DepthwiseConv2D

# 1. Configuratie van de veiligheidsbuffers
PHOTO_PATH = "/home/admin/photos"
MIN_FREE_SPACE_GB = 2.0  # Zorg dat er altijd minimaal 2GB vrij blijft
CPU_BUFFER_SECONDS = 1.0  # Korte adempauze voor de processor na elke analyse

if not os.path.exists(PHOTO_PATH):
    os.makedirs(PHOTO_PATH)


class CustomDepthwiseConv2D(DepthwiseConv2D):
    def __init__(self, **kwargs):
        if 'groups' in kwargs:
            del kwargs['groups']
        super().__init__(**kwargs)


np.set_printoptions(suppress=True)
print("Slimme AI gestart. Opslag en snelheid worden gemonitord...")

model = load_model("keras_model.h5", compile=False, custom_objects={'DepthwiseConv2D': CustomDepthwiseConv2D})
class_names = open("labels.txt", "r").readlines()
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)


def manage_storage():
    """Controleert de vrije ruimte en verwijdert de oudste foto's als de buffer wordt geraakt."""
    total, used, free = shutil.disk_usage("/")
    free_gb = free / (1024 ** 3)
    if free_gb < MIN_FREE_SPACE_GB:
        print(f"\n[OPSLAG WAARSCHUWING] Nog maar {free_gb:.2f}GB vrij. Opschonen gestart...")
        # Zoek alle jpg bestanden en sorteer op aanmaakdatum (oudste eerst)
        photos = sorted(glob.glob(f"{PHOTO_PATH}/*.jpg"), key=os.path.getmtime)
        # Verwijder de 20 oudste foto's om weer ruimte te maken
        for old_photo in photos[:20]:
            try:
                os.remove(old_photo)
            except OSError:
                pass
        print("[OPSLAG] Ruimte succesvol vrijgemaakt.")


time.sleep(2)

while True:
    start_time = time.time()
    # Controleer of we veilig kunnen opslaan
    manage_storage()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{PHOTO_PATH}/{timestamp}.jpg"

    try:
        subprocess.run(
            ["rpicam-still", "-o", filename, "-t", "1000", "--nopreview"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        print("Camera fout. Herkansing in 2 seconden.")
        time.sleep(2)
        continue

    if not os.path.exists(filename):
        continue

    # Analyse
    image = Image.open(filename).convert("RGB")
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    image_array = np.asarray(image)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
    data[0] = normalized_image_array
    prediction = model.predict(data, verbose=0)  # verbose=0 stopt extra Keras tekst
    index = np.argmax(prediction)
    class_name = class_names[index].strip()
    confidence_score = prediction[0][index]

    # Snelheidsberekening
    end_time = time.time()
    processing_time = end_time - start_time

    print(f"[{timestamp}] Gezien: {class_name[2:]} ({confidence_score:.2f}) | Snelheid: {processing_time:.1f}s")

    if not bool(class_name[0:1]):
        os.system(f"rm {PHOTO_PATH}")

    # De dynamische adempauze
    time.sleep(CPU_BUFFER_SECONDS)