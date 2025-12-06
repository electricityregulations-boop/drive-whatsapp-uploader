# app.py
"""
Streamlit app: Upload -> Google Drive (optional) -> WhatsApp Cloud API
This single-file version has keys embedded directly for quick testing.
**Remove secrets from code and move to Streamlit Secrets for production.**
"""

import streamlit as st
import json, io, time, requests, traceback, mimetypes
from typing import Optional

# --- === PASTE YOUR SECRETS HERE (embedded for quick testing) === ---
# Google Service Account JSON (full JSON string)
GDRIVE_SA_JSON = """
{
  "type": "service_account",
  "project_id": "report-automation-480315",
  "private_key_id": "ad92dc11d3b17de5ffc7f84e025af66c2e39fab5",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCzDawFneoMOxYS\nY+DOOZWJjJcku6e+cvYq2vYmj49wgTJeo1CW9+rAJAKkUsk8l15qxxonvfWPBoQq\nPCNj0XpjSDa2BI9GNMNlWtagl6IvxTkAX2N9rx4CBqdOEOQenytOUg1iYhUz6bue\nSHOPSrNY0Qm74h+TwMAttmI0K7ks8MVHZrEUSTLB4GXN6hTTuG/2TqfvzJ/nO/fH\n3pY6HUhXBnRkhYjKty+XtNoxGStuEX5v1lsXtugR577xLB9nzVXLtgoAltaDFeIX\nHs2rdozQWYkvx9IyVOETm1GaQuwySOwW2PNyMItQJ9qlrKBaXiL3y+JaI3WwZ4sZ\nIyy3et0vAgMBAAECggEAIC5t45iNT2NzRRzkc8xPvyggpj6AGK/K5Mr0ANw+mKbv\n6aiKvIeUjrIqM2SZvKUsGB7u6YOv1eQC7yBd7/vfdmatRqutIJ4tHFNmTfjS8qkM\n5K9AT3+g8hZGDbbleUd8XhhLRYqBaxIwYXN+KZvwfh8cE8PBjynOoKiuH9hX8OaM\nQHzAxUE/1Gn/30ZwS4ksyOmq6yBLKublG02XeW8J15gyPkN3I5ab185DSkGIqmg\n6fPeMM56WZUJxccax+kdnEpKSOxEzZyISDYwPId/s+tJM4Ugoa/pILZG+12dbL+C\nh67SGOrZ3sEnvePqUP9SzMIRulklBr1SDdBTHn1+EQKBgQDkNLJY+LsTtX/7w7BW\nLZPbks0bZRiiw/4E5uvoMgRLzXUG9FMWaan6ytgPyrgN0X1ZoCFO5RKm7eaQff8o\nIsX2ijwJFEdJRrxY2MJ+SyBljS1ZHVSL6GsLAyEx/OYDgB+8M3MJSXt4oFAnLlxF\nNqTGjPKIiAYpMYC+0+4kE1pc9wKBgQDI3G+CHlYtWzrUoyLpfIjZ+k49WT01LIbn\nKd5il4mAC4uOW2bI7kWVWMpwMnpXidl2IDaTpg3gVoFLE7lwkIMGYNcem0agCbQD\n72+I2JghqvNlMXT8/D9cpaA6qLd0pwNSM5DSUq0O065EGiZA6LQVitf+KT9IMenj\nepkvAUOLiQKBgBykyKYGQmUM6Q2O2HlYqzBqUrhXjioP87hly8KPVJ63ITNIQ42S\nobVK9Ke2yDdjzhoL0WJ3ukmdns0QI5DEHJj/bN2u3+vApy93taHoiB53A/QljFEr\nURRGxknh9nUGBfW3d3747DiN1sG0PfyqCTCqzF56xFszTXemXkPE8hitAoGAPq0a\nVn3k4i5Pgz6MjFMB2RLUCyynfsowJj3YWOd0TnJLz9YRkq1XJS0ZrjzyFBK9urB+\nlz//oHsdyTGUcd2GJR1ewvws449jjr7ODOOZRRg07uSp3q9PjjdYcjVnWY0r6iCR\nFjAaNEA1ZqbKPQLf/sDeeT6hsoNwujztQ8+fJhECgYBJ9tbYi+fRFlHxbyDnIH/B\nhHnIjk2ghJZlZ/VncbGTVI4Kka7KvHo13gU+KY+O4mHSvbrV+kHorzxloRIf064K\n2D2opvxbsyB0TTT3ZMplLLwAGg7mFuurFAAAl8nfkKnbR/OpkoV/pHA7+OXWsGLd\n0k/KVTQkNZi2WFbj/csRwQ==\n-----END PRIVATE KEY-----\n",
  "client_email": "streamlit-drive-sa@report-automation-480315.iam.gserviceaccount.com",
  "client_id": "118415599829889929602",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/streamlit-drive-sa%40report-automation-480315.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
"""

# Drive folder ID
GDRIVE_FOLDER_ID = "1wCrpAvGO2dShMWHqxmvTwsHRuvUwTIWy"

# WhatsApp Cloud API credentials (temporary token provided earlier)
WHATSAPP_TOKEN = "EAAWyxnnXSA4BQKMBJeqw1GzCTcnUdhIJxqkAZBHcsFXnH5DEUKuraSCR9WvWZBSRlJ7PjMT8w9Sh7ZBoeBpKwECdLDI5MvnU4EZBy06TMOOH4OmKJsLTMvwQKQhMKRgukwUhZAxdkfXpuAC2wVWuiWfZBuyIXS3uZCDCbeETTXz6UWBJj6cp3MYKrLxZAsxeaeHum1ceakBSJlFgk9dESg9MkK8NDCXufyeXr5NytwIBOEIRVYZBlTmdWECWUil5THYkKwfeyBWh7fXUsbSwRER6dkzqMvZCKOzLY9Ub3xd7AZD"
WHATSAPP_PHONE_ID = "859290280608485"
WHATSAPP_TO = "+917752020462"

# --- end of embedded secrets ---
# Note: For production, move above values to Streamlit Secrets.

# Try to import Google libs (they must be listed in requirements.txt)
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    GOOGLE_LIBS_AVAILABLE = True
except Exception:
    GOOGLE_LIBS_AVAILABLE = False

st.set_page_config(page_title="Uploader → Drive & WhatsApp", layout="centered")
st.title("Upload → Google Drive (optional) → WhatsApp")

st.markdown(
    """
Use this app to upload a file to Google Drive and/or send it via the WhatsApp Cloud API.

**Important**:
- This test file embeds secrets for convenience. Move them to Streamlit Secrets for production.
- Temporary WhatsApp tokens expire (~24 hrs). Replace with long-lived tokens for production.
"""
)

# -------------------------
# Basic UI & flags
# -------------------------
enable_drive = bool(GDRIVE_SA_JSON and GDRIVE_FOLDER_ID)
enable_whatsapp = bool(WHATSAPP_TOKEN and WHATSAPP_PHONE_ID and WHATSAPP_TO)

if not GOOGLE_LIBS_AVAILABLE and enable_drive:
    st.warning("Google client libraries are not available. Add them to requirements.txt.")

st.subheader("Choose upload options")
col1, col2 = st.columns(2)
with col1:
    do_drive = st.checkbox("Upload to Google Drive (create share link)", value=enable_drive)
with col2:
    do_whatsapp_media = st.checkbox("Upload & send file to WhatsApp as media", value=enable_whatsapp)

if do_drive and not enable_drive:
    st.error("Drive not fully configured. Check embedded service account JSON and installed packages.")
if do_whatsapp_media and not enable_whatsapp:
    st.error("WhatsApp not fully configured. Check embedded WhatsApp credentials.")

st.write("---")

uploaded = st.file_uploader("Choose file to upload (PDF, image, etc.)", type=None)
note = st.text_input("Optional message / caption to include with WhatsApp message", "")

# -------------------------
# Helper functions
# -------------------------
def get_drive_service():
    sa_info = json.loads(GDRIVE_SA_JSON)
    creds = service_account.Credentials.from_service_account_info(sa_info, scopes=["https://www.googleapis.com/auth/drive"])
    service = build("drive", "v3", credentials=creds, cache_discovery=False)
    return service

def upload_to_drive_bytes(filename: str, file_bytes: bytes, mimetype: Optional[str]) -> str:
    if not GOOGLE_LIBS_AVAILABLE:
        raise RuntimeError("google-api libs not installed.")
    service = get_drive_service()
    fh = io.BytesIO(file_bytes)
    media = MediaIoBaseUpload(fh, mimetype=mimetype or "application/octet-stream", resumable=True)
    metadata = {"name": filename}
    if GDRIVE_FOLDER_ID:
        metadata["parents"] = [GDRIVE_FOLDER_ID]
    request = service.files().create(body=metadata, media_body=media, fields="id")
    response = None
    while True:
        status, response = request.next_chunk()
        if status:
            st.info(f"Drive upload progress: {int(status.progress() * 100)}%")
        if response:
            break
    return response["id"]

def make_drive_file_public(file_id: str) -> str:
    service = get_drive_service()
    try:
        service.permissions().create(fileId=file_id, body={"role":"reader","type":"anyone"}).execute()
    except Exception as e:
        st.warning("Drive permission creation returned: " + str(e))
    meta = service.files().get(fileId=file_id, fields="id, webViewLink, webContentLink").execute()
    return meta.get("webViewLink") or meta.get("webContentLink") or f"https://drive.google.com/file/d/{file_id}/view"

def upload_media_to_whatsapp(file_bytes: bytes, filename: str, mimetype: Optional[str]) -> str:
    """Upload file to WhatsApp media endpoint. Returns media_id.
       Ensures a valid MIME type is sent."""
    if not (WHATSAPP_TOKEN and WHATSAPP_PHONE_ID):
        raise RuntimeError("WhatsApp credentials missing.")
    # Guess mimetype if empty
    if not mimetype:
        guessed, _ = mimetypes.guess_type(filename)
        mimetype = guessed or "application/octet-stream"

    upload_url = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_ID}/media"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}

    # requests wants (filename, fileobj_or_bytes, content-type)
    files = {
        "file": (filename, file_bytes, mimetype)
    }
    data = {"messaging_product": "whatsapp"}
    resp = requests.post(upload_url, headers=headers, files=files, data=data, timeout=120)
    if resp.status_code not in (200,201):
        raise RuntimeError(f"WhatsApp media upload failed {resp.status_code}: {resp.text}")
    j = resp.json()
    media_id = j.get("id")
    if not media_id:
        raise RuntimeError("WhatsApp upload returned no media id: " + resp.text)
    return media_id

def send_whatsapp_media(media_id: str, filename: str, mimetype: Optional[str], caption: str = ""):
    url = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    if mimetype and mimetype.startswith("image/"):
        payload = {
            "messaging_product": "whatsapp",
            "to": WHATSAPP_TO,
            "type": "image",
            "image": {"id": media_id, "caption": caption}
        }
    else:
        payload = {
            "messaging_product": "whatsapp",
            "to": WHATSAPP_TO,
            "type": "document",
            "document": {"id": media_id, "filename": filename}
        }
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    if resp.status_code not in (200,201):
        raise RuntimeError(f"WhatsApp send failed {resp.status_code}: {resp.text}")
    return resp  # return requests.Response for consistency

def send_whatsapp_text(body: str):
    url = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product":"whatsapp","to":WHATSAPP_TO,"type":"text","text":{"body":body}}
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    if resp.status_code not in (200,201):
        raise RuntimeError(f"WhatsApp text send failed {resp.status_code}: {resp.text}")
    return resp  # return Response object

# -------------------------
# Main action
# -------------------------
if uploaded:
    st.write(f"File: **{uploaded.name}** — {uploaded.size} bytes — MIME: {uploaded.type}")
    if st.button("Start upload & send"):
        try:
            uploaded.seek(0)
            file_bytes = uploaded.getvalue()
            filename = uploaded.name
            mimetype = uploaded.type or None

            drive_link = None
            whatsapp_media_resp = None

            # 1) upload to Drive if selected
            if do_drive:
                if not (GDRIVE_SA_JSON and GDRIVE_FOLDER_ID):
                    st.error("Drive not configured.")
                else:
                    st.info("Uploading to Google Drive...")
                    file_id = upload_to_drive_bytes(filename, file_bytes, mimetype)
                    st.success("Uploaded to Drive. File ID: " + file_id)
                    st.info("Creating shareable link...")
                    drive_link = make_drive_file_public(file_id)
                    st.success("Drive link: " + drive_link)

            # 2) upload to WhatsApp media endpoint if selected
            if do_whatsapp_media:
                if not (WHATSAPP_TOKEN and WHATSAPP_PHONE_ID and WHATSAPP_TO):
                    st.error("WhatsApp not configured.")
                else:
                    st.info("Uploading media to WhatsApp...")
                    media_id = upload_media_to_whatsapp(file_bytes, filename, mimetype)
                    st.success("Media uploaded to WhatsApp (media_id=" + str(media_id) + ")")
                    st.info("Sending media message...")
                    resp = send_whatsapp_media(media_id, filename, mimetype, caption=note or "")
                    st.success("WhatsApp media message sent.")
                    try:
                        st.json(resp.json())
                    except Exception:
                        st.write(resp.text)
                    whatsapp_media_resp = resp

            # 3) if Drive link exists and user did not send media, send link via WhatsApp text
            if drive_link and not do_whatsapp_media and (WHATSAPP_TOKEN and WHATSAPP_PHONE_ID and WHATSAPP_TO):
                st.info("Sending drive link to WhatsApp as text message...")
                body = (note + "\n\n" if note else "") + f"New report: {drive_link}"
                rsp = send_whatsapp_text(body)
                st.success("WhatsApp text sent.")
                try:
                    st.json(rsp.json())
                except Exception:
                    st.write(rsp.text)

            st.balloons()

        except Exception as e:
            st.error("Operation failed: " + str(e))
            st.write(traceback.format_exc())

else:
    st.info("Choose a file to upload, pick options above, then click Start upload & send.")

st.write("---")
st.markdown("**Embedded credentials (for quick testing only)** — remove after testing.")
st.code(
"""
GDRIVE_SA_JSON = \"\"\"{ ... entire service account JSON ... }\"\"\"
GDRIVE_FOLDER_ID = "1wCrpAvGO2dShMWHqxmvTwsHRuvUwTIWy"
WHATSAPP_TOKEN = "EAAWyxnnXSA4B..."
WHATSAPP_PHONE_ID = "859290280608485"
WHATSAPP_TO = "+917752020462"
""", language="text")

# -------------------------
# WhatsApp quick tests (UI helpers)
# -------------------------
st.markdown("---")
st.header("Quick WhatsApp tests (dev only)")

# 1) Test sending a plain text message via WhatsApp
st.subheader("1) Send a test text message")
test_text = st.text_input("Message to send (text)", value="Hello from Streamlit test!")
if st.button("Send test text message"):
    try:
        resp = send_whatsapp_text(test_text)
        # resp is a requests.Response
        st.success("Text sent — response:")
        try:
            st.json(resp.json())
        except Exception:
            st.write(resp.text)
    except Exception as e:
        st.error("Failed to send test text: " + str(e))

st.write("")  # spacer

# 2) Test uploading a small file to WhatsApp and sending it as media
st.subheader("2) Upload & send a file to WhatsApp (media)")
test_file = st.file_uploader("Choose a small file (image/pdf) to test media send", type=None, key="wa_media_test")
if test_file is not None:
    st.write("Selected:", test_file.name, f"({test_file.size} bytes)")
    if st.button("Upload & send media"):
        try:
            test_file.seek(0)
            file_bytes = test_file.getvalue()
            filename = test_file.name
            mimetype = test_file.type or None

            st.info("Uploading media to WhatsApp...")
            media_id = upload_media_to_whatsapp(file_bytes, filename, mimetype)
            st.success("Uploaded to WhatsApp media (media_id=" + str(media_id) + ")")

            st.info("Sending media message...")
            resp = send_whatsapp_media(media_id, filename, mimetype, caption="Test file from Streamlit")
            st.success("Media message sent — response:")
            try:
                st.json(resp.json())
            except Exception:
                st.write(resp.text)

        except Exception as e:
            st.error("Media test failed: " + str(e))
            st.text(traceback.format_exc())

st.markdown("**Note:** Temporary tokens expire in 24 hrs. Use long-lived tokens when you move to production.")
