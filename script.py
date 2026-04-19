import os
import io
from PIL import Image
from supabase import create_client

SUPABASE_URL = "https://alpwauztirqqwillpmxx.supabase.co"
SUPABASE_KEY = "YOUR_SERVICE_ROLE_KEY"
BUCKET_NAME = "media"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

INPUT_DIR = "input_images"


def upload(path, data):
    try:
        supabase.storage.from_(BUCKET_NAME).upload(
            path, data, {"content-type": "image/webp"}
        )
    except Exception:
        print(f"Skipping {path}")


def process():
    for file in os.listdir(INPUT_DIR):
        if not file.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        path = os.path.join(INPUT_DIR, file)
        name = os.path.splitext(file)[0]

        with Image.open(path) as img:
            # RAW
            raw_bytes = io.BytesIO()
            img.save(raw_bytes, format="JPEG")
            raw_path = f"{name}_raw.jpg"

            # MOBILE
            mobile = img.copy()
            mobile.thumbnail((1080, 1080))
            mobile_bytes = io.BytesIO()
            mobile.save(mobile_bytes, format="WEBP", quality=80)
            mobile_path = f"{name}_mobile.webp"

            # THUMB
            thumb = img.copy()
            thumb.thumbnail((300, 300))
            thumb_bytes = io.BytesIO()
            thumb.save(thumb_bytes, format="WEBP", quality=70)
            thumb_path = f"{name}_thumb.webp"

            # Upload
            upload(raw_path, raw_bytes.getvalue())
            upload(mobile_path, mobile_bytes.getvalue())
            upload(thumb_path, thumb_bytes.getvalue())

            # URLs
            raw_url = supabase.storage.from_(BUCKET_NAME).get_public_url(raw_path)
            mobile_url = supabase.storage.from_(BUCKET_NAME).get_public_url(mobile_path)
            thumb_url = supabase.storage.from_(BUCKET_NAME).get_public_url(thumb_path)

            # Insert into DB
            supabase.table("posts").insert({
                "media_thumb_url": thumb_url,
                "media_mobile_url": mobile_url,
                "media_raw_url": raw_url,
            }).execute()

            print(f"Uploaded: {file}")


process()
print("Done")