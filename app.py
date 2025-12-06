# app.py
"""
Streamlit app: Upload -> Google Drive (optional) -> WhatsApp Cloud API
Features:
 - Upload file to Google Drive (service account) and create "anyone with link" share link.
 - OR upload file to WhatsApp media endpoint and send the media directly.
 - You can enable both flows: upload to Drive then also upload/send to WhatsApp media.
Secrets (set in Streamlit Cloud):
 - GDRIVE_SA_JSON   : full service account JSON (triple-quoted in secrets)
 - GDRIVE_FOLDER_ID : Drive folder id (string)
 - WHATSAPP_TOKEN   : WhatsApp Cloud API bearer token
 - WHATSAPP_PHONE_ID: WhatsApp phone number id (numeric)
 - WHATSAPP_TO      : destination phone (E.164) or group (test with phone first)
"""

import streamlit as st
import json, io, time, requests, traceback
from typing import Optional

# Try to import Google libs only when needed (faster cold start)
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
- Store credentials in Streamlit Secrets (see README in this page).
- For WhatsApp group delivery test with a personal number first — group support varies.
"""
)

# -------------------------
# Load secrets & validate
# -------------------------
secrets = st.secrets

# Drive secrets
GDRIVE_SA_JSON = secrets.get("GDRIVE_SA_JSON")
GDRIVE_FOLDER_ID = secrets.get("GDRIVE_FOLDER_ID", "").strip()

# WhatsApp secrets
WHATSAPP_TOKEN = secrets.get("WHATSAPP_TOKEN", "").strip()
WHATSAPP_PHONE_ID = secrets.get("WHATSAPP_PHONE_ID", "").strip()
WHATSAPP_TO = secrets.get("WHATSAPP_TO", "").strip()

# Flags
enable_drive = bool(GDRIVE_SA_JSON and GDRIVE_FOLDER_ID)
enable_whatsapp = bool(WHATSAPP_TOKEN and WHATSAPP_PHONE_ID and WHATSAPP_TO)

if not GOOGLE_LIBS_AVAILABLE and enable_drive:
    st.warning("Google client libraries are not available. Install them in requirements.txt. Drive functionality may fail.")

st.subheader("Choose upload options")
col1, col2 = st.columns(2)
with col1:
    do_drive = st.checkbox("Upload to Google Drive (create share link)", value=enable_drive)
with col2:
    do_whatsapp_media = st.checkbox("Upload & send file to WhatsApp as media", value=enable_whatsapp)

if do_drive and not enable_drive:
    st.error("Drive is not fully configured. Add GDRIVE_SA_JSON and GDRIVE_FOLDER_ID in Secrets.")
if do_whatsapp_media and not enable_whatsapp:
    st.error("WhatsApp not fully configured. Add WHATSAPP_TOKEN, WHATSAPP_PHONE_ID and WHATSAPP_TO in Secrets.")

st.write("---")

uploaded = st.file_uploader("Choose file to upload (PDF, image, etc.)", type=None)
note = st.text_input("Optional message / caption to include with WhatsApp message", "")

# -------------------------
# Helper functions
# -------------------------
def get_drive_service():
    """Return Drive service built from service account JSON in secrets"""
    sa_info = json.loads(GDRIVE_SA_JSON)
    creds = service_account.Credentials.from_service_account_info(sa_info, scopes=["https://www.googleapis.com/auth/drive"])
    service = build("drive", "v3", credentials=creds, cache_discovery=False)
    return service

def upload_to_drive_bytes(filename: str, file_bytes: bytes, mimetype: Optional[str]) -> str:
    """Upload bytes to Drive folder; returns file id"""
    if not GOOGLE_LIBS_AVAILABLE:
        raise RuntimeError("google-api libs not installed on server.")
    service = get_drive_service()
    fh = io.BytesIO(file_bytes)
    media = MediaIoBaseUpload(fh, mimetype=mimetype or "application/octet-stream", resumable=True)
    metadata = {"name": filename}
    if GDRIVE_FOLDER_ID:
        metadata["parents"] = [GDRIVE_FOLDER_ID]
    request = service.files().create(body=metadata, media_body=media, fields="id")
    response = None
    # resumable upload loop
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
        # Non-fatal (permission may exist)
        st.warning("Drive permission create returned: " + str(e))
    meta = service.files().get(fileId=file_id, fields="id, webViewLink, webContentLink").execute()
    return meta.get("webViewLink") or meta.get("webContentLink") or f"https://drive.google.com/file/d/{file_id}/view"

def upload_media_to_whatsapp(file_bytes: bytes, filename: str, mimetype: Optional[str]) -> str:
    """Upload file to WhatsApp media endpoint. Returns media_id."""
    url = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_ID}/media"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    files = {"file": (filename, file_bytes)}
    data = {"messaging_product": "whatsapp"}
    resp = requests.post(url, headers=headers, files=files, data=data, timeout=120)
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
    return resp.json()

def send_whatsapp_text(body: str):
    url = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product":"whatsapp","to":WHATSAPP_TO,"type":"text","text":{"body":body}}
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    if resp.status_code not in (200,201):
        raise RuntimeError(f"WhatsApp text send failed {resp.status_code}: {resp.text}")
    return resp.json()

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
                    st.error("Drive not configured. Add GDRIVE_SA_JSON and GDRIVE_FOLDER_ID in Streamlit Secrets.")
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
                    st.error("WhatsApp not configured. Add WHATSAPP_TOKEN, WHATSAPP_PHONE_ID, WHATSAPP_TO in Streamlit Secrets.")
                else:
                    st.info("Uploading media to WhatsApp...")
                    media_id = upload_media_to_whatsapp(file_bytes, filename, mimetype)
                    st.success("Media uploaded to WhatsApp (media_id=" + str(media_id) + ")")
                    st.info("Sending media message...")
                    resp = send_whatsapp_media(media_id, filename, mimetype, caption=note or "")
                    st.success("WhatsApp media message sent.")
                    st.write(resp)
                    whatsapp_media_resp = resp

            # 3) if Drive link exists and user did not send media, send link via WhatsApp text
            if drive_link and not do_whatsapp_media and (WHATSAPP_TOKEN and WHATSAPP_PHONE_ID and WHATSAPP_TO):
                st.info("Sending drive link to WhatsApp as text message...")
                body = (note + "\n\n" if note else "") + f"New report: {drive_link}"
                rsp = send_whatsapp_text(body)
                st.success("WhatsApp text sent.")
                st.write(rsp)

            st.balloons()

        except Exception as e:
            st.error("Operation failed: " + str(e))
            st.debug = True
            st.write(traceback.format_exc())

else:
    st.info("Choose a file to upload, pick options above, then click Start upload & send.")

st.write("---")
st.markdown("**Secrets required** (set in Streamlit Cloud → Settings → Secrets):")
st.code(
"""
GDRIVE_SA_JSON = \"\"\"{ ... entire service account JSON ... }\"\"\"
GDRIVE_FOLDER_ID = "1wCrpAvGO2dShMWHqxmvTwsHRuvUwTIWy"
WHATSAPP_TOKEN = "EAAWyxnnXSA4BQKMBJeqw1GzCTcnUdhIJxqkAZBHcsFXnH5DEUKuraSCR9WvWZBSRlJ7PjMT8w9Sh7ZBoeBpKwECdLDI5MvnU4EZBy06TMOOH4OmKJsLTMvwQKQhMKRgukwUhZAxdkfXpuAC2wVWuiWfZBuyIXS3uZCDCbeETTXz6UWBJj6cp3MYKrLxZAsxeaeHum1ceakBSJlFgk9dESg9MkK8NDCXufyeXr5NytwIBOEIRVYZBlTmdWECWUil5THYkKwfeyBWh7fXUsbSwRER6dkzqMvZCKOzLY9Ub3xd7AZD"
WHATSAPP_PHONE_ID = "859290280608485"
WHATSAPP_TO = "+917752020462"
""", language="text")

# -------------------------
# WhatsApp quick tests (UI helpers)
# Add this block at the end of your existing app.py
# -------------------------
st.markdown("---")
st.header("Quick WhatsApp tests (dev only)")

# 1) Test sending a plain text message via WhatsApp
st.subheader("1) Send a test text message")
test_text = st.text_input("Message to send (text)", value="Hello from Streamlit test!")
if st.button("Send test text message"):
    try:
        # reuse your send_whatsapp_text function if present
        resp = send_whatsapp_text(test_text)
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
            mimetype = test_file.type or ""

            # 2a) Upload to WhatsApp media endpoint
            st.info("Uploading media to WhatsApp...")
            media_id = upload_media_to_whatsapp(file_bytes, filename, mimetype)
            st.success("Uploaded to WhatsApp media (media_id=" + str(media_id) + ")")

            # 2b) Send the media message
            st.info("Sending media message...")
            resp = send_whatsapp_media(media_id, filename, mimetype, caption="Test file from Streamlit")
            st.success("Media message sent — response:")
            st.json(resp)
        except Exception as e:
            st.error("Media test failed: " + str(e))
            st.write("") 
            st.write("Traceback:")
            import traceback
            st.text(traceback.format_exc())

st.markdown("**Note:** Temporary tokens expire in 24 hrs. Use long-lived tokens when you move to production.")
