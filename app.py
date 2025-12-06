# OPTIMIZED WHATSAPP CLOUD API CODE FOR PDF-ONLY UPLOADS
# Simplified and hardened for production use with PDFs

import streamlit as st
import json, io, time, requests, traceback
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

GDRIVE_FOLDER_ID = "1wCrpAvGO2dShMWHqxmvTwsHRuvUwTIWy"

# WhatsApp Cloud API credentials
WHATSAPP_TOKEN = "EAAWyxnnXSA4BQKMBJeqw1GzCTcnUdhIJxqkAZBHcsFXnH5DEUKuraSCR9WvWZBSRlJ7PjMT8w9Sh7ZBoeBpKwECdLDI5MvnU4EZBy06TMOOH4OmKJsLTMvwQKQhMKRgukwUhZAxdkfXpuAC2wVWuiWfZBuyIXS3uZCDCbeETTXz6UWBJj6cp3MYKrLxZAsxeaeHum1ceakBSJlFgk9dESg9MkK8NDCXufyeXr5NytwIBOEIRVYZBlTmdWECWUil5THYkKwfeyBWh7fXUsbSwRER6dkzqMvZCKOzLY9Ub3xd7AZD"
WHATSAPP_PHONE_ID = "859290280608485"
WHATSAPP_TO = "+917752020462"

# PDF-specific constants
PDF_MIME_TYPE = "application/pdf"
PDF_MAX_SIZE = 100 * 1024 * 1024  # 100MB (WhatsApp limit for documents)

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    GOOGLE_LIBS_AVAILABLE = True
except Exception:
    GOOGLE_LIBS_AVAILABLE = False

st.set_page_config(page_title="PDF → Drive & WhatsApp", layout="centered")
st.title("📄 PDF Upload → Google Drive & WhatsApp")

st.markdown("""
Upload PDF reports to Google Drive and/or send them via WhatsApp Cloud API.

**Features:**
- ✅ Optimized for PDF files only
- ✅ Automatic file validation
- ✅ Enhanced error handling
- ✅ Drive shareable links
- ✅ WhatsApp document messaging
""")

# -------------------------
# OPTIMIZED HELPER FUNCTIONS FOR PDF
# -------------------------

def get_drive_service():
    """Initialize Google Drive service."""
    sa_info = json.loads(GDRIVE_SA_JSON)
    creds = service_account.Credentials.from_service_account_info(
        sa_info, 
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    service = build("drive", "v3", credentials=creds, cache_discovery=False)
    return service


def upload_pdf_to_drive(filename: str, file_bytes: bytes) -> str:
    """Upload PDF to Google Drive.
    
    Args:
        filename: PDF filename
        file_bytes: PDF content as bytes
        
    Returns:
        file_id: Google Drive file ID
        
    Raises:
        RuntimeError: If upload fails
    """
    if not GOOGLE_LIBS_AVAILABLE:
        raise RuntimeError("Google API libraries not installed.")
    
    try:
        service = get_drive_service()
        fh = io.BytesIO(file_bytes)
        media = MediaIoBaseUpload(
            fh, 
            mimetype=PDF_MIME_TYPE,
            resumable=True
        )
        
        metadata = {
            "name": filename,
            "mimeType": PDF_MIME_TYPE
        }
        
        if GDRIVE_FOLDER_ID:
            metadata["parents"] = [GDRIVE_FOLDER_ID]
        
        request = service.files().create(
            body=metadata, 
            media_body=media, 
            fields="id,name,mimeType"
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                st.info(f"📤 Drive upload progress: {progress}%")
        
        return response["id"]
        
    except Exception as e:
        raise RuntimeError(f"Drive upload failed: {str(e)}")


def make_drive_file_public(file_id: str) -> str:
    """Make Drive file publicly accessible and return link.
    
    Args:
        file_id: Google Drive file ID
        
    Returns:
        share_link: Public viewing URL
    """
    try:
        service = get_drive_service()
        
        # Create public permission
        service.permissions().create(
            fileId=file_id,
            body={"role": "reader", "type": "anyone"}
        ).execute()
        
        # Get file metadata with links
        meta = service.files().get(
            fileId=file_id, 
            fields="id,webViewLink,webContentLink,name"
        ).execute()
        
        return meta.get("webViewLink") or f"https://drive.google.com/file/d/{file_id}/view"
        
    except Exception as e:
        st.warning(f"Drive permission setup warning: {str(e)}")
        return f"https://drive.google.com/file/d/{file_id}/view"


def upload_pdf_to_whatsapp(file_bytes: bytes, filename: str) -> str:
    """Upload PDF to WhatsApp media endpoint.
    
    Args:
        file_bytes: PDF content as bytes
        filename: Original filename
        
    Returns:
        media_id: WhatsApp media ID
        
    Raises:
        RuntimeError: If upload fails
    """
    if not (WHATSAPP_TOKEN and WHATSAPP_PHONE_ID):
        raise RuntimeError("WhatsApp credentials missing.")
    
    # Validate file size
    if len(file_bytes) > PDF_MAX_SIZE:
        raise RuntimeError(
            f"PDF too large: {len(file_bytes) / (1024*1024):.1f}MB "
            f"(max 100MB for WhatsApp documents)"
        )
    
    # Use latest stable API version
    upload_url = f"https://graph.facebook.com/v21.0/{WHATSAPP_PHONE_ID}/media"
    
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    
    files = {
        "file": (filename, file_bytes, PDF_MIME_TYPE)
    }
    
    data = {
        "messaging_product": "whatsapp",
        "type": PDF_MIME_TYPE
    }
    
    try:
        resp = requests.post(
            upload_url, 
            headers=headers, 
            files=files, 
            data=data, 
            timeout=180  # 3 minutes for large PDFs
        )
        
        if resp.status_code == 401:
            raise RuntimeError(
                "WhatsApp token invalid or expired. Generate a new token."
            )
        elif resp.status_code == 413:
            raise RuntimeError("PDF file too large for WhatsApp.")
        elif resp.status_code == 429:
            raise RuntimeError("Rate limit exceeded. Wait before retrying.")
        elif resp.status_code not in (200, 201):
            error_detail = resp.json() if resp.text else resp.text
            raise RuntimeError(
                f"WhatsApp media upload failed ({resp.status_code}): {error_detail}"
            )
        
        response_data = resp.json()
        media_id = response_data.get("id")
        
        if not media_id:
            raise RuntimeError(
                f"No media ID returned from WhatsApp: {response_data}"
            )
        
        return media_id
        
    except requests.exceptions.Timeout:
        raise RuntimeError("Upload timed out. Check network connection or try smaller PDF.")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Network error: {str(e)}")


def send_pdf_via_whatsapp(media_id: str, filename: str, caption: str = ""):
    """Send PDF document via WhatsApp.
    
    Args:
        media_id: WhatsApp media ID
        filename: Original filename
        caption: Optional message caption
        
    Returns:
        dict: API response with message ID
        
    Raises:
        RuntimeError: If send fails
    """
    if not (WHATSAPP_TOKEN and WHATSAPP_PHONE_ID and WHATSAPP_TO):
        raise RuntimeError("WhatsApp credentials incomplete.")
    
    # CRITICAL: Remove '+' from phone number for API
    to_number = WHATSAPP_TO.replace("+", "").strip()
    
    url = f"https://graph.facebook.com/v21.0/{WHATSAPP_PHONE_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_number,
        "type": "document",
        "document": {
            "id": media_id,
            "filename": filename,
            "caption": caption[:1024] if caption else None  # WhatsApp 1KB limit
        }
    }
    
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if resp.status_code == 401:
            raise RuntimeError("Invalid WhatsApp token.")
        elif resp.status_code == 403:
            raise RuntimeError(
                "Permission denied. Check:\n"
                "- Phone number quality rating\n"
                "- Account not restricted\n"
                "- Recipient added to test numbers list"
            )
        elif resp.status_code == 429:
            raise RuntimeError("Rate limit exceeded.")
        elif resp.status_code not in (200, 201):
            error_detail = resp.json() if resp.text else resp.text
            raise RuntimeError(
                f"WhatsApp send failed ({resp.status_code}): {error_detail}"
            )
        
        return resp.json()
        
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Network error: {str(e)}")


def send_whatsapp_text(body: str):
    """Send plain text message via WhatsApp.
    
    Args:
        body: Message text
        
    Returns:
        dict: API response
    """
    if not (WHATSAPP_TOKEN and WHATSAPP_PHONE_ID and WHATSAPP_TO):
        raise RuntimeError("WhatsApp credentials incomplete.")
    
    to_number = WHATSAPP_TO.replace("+", "").strip()
    
    url = f"https://graph.facebook.com/v21.0/{WHATSAPP_PHONE_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_number,
        "type": "text",
        "text": {"body": body}
    }
    
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    
    if resp.status_code not in (200, 201):
        error_detail = resp.json() if resp.text else resp.text
        raise RuntimeError(f"Text send failed ({resp.status_code}): {error_detail}")
    
    return resp.json()


def validate_pdf(file_bytes: bytes, filename: str) -> tuple[bool, str]:
    """Validate that uploaded file is a proper PDF.
    
    Args:
        file_bytes: File content
        filename: Original filename
        
    Returns:
        (is_valid, error_message)
    """
    # Check extension
    if not filename.lower().endswith('.pdf'):
        return False, "File must have .pdf extension"
    
    # Check PDF magic bytes
    if not file_bytes.startswith(b'%PDF-'):
        return False, "File is not a valid PDF (invalid header)"
    
    # Check size
    size_mb = len(file_bytes) / (1024 * 1024)
    if len(file_bytes) > PDF_MAX_SIZE:
        return False, f"PDF too large ({size_mb:.1f}MB, max 100MB)"
    
    if len(file_bytes) < 100:
        return False, "PDF file appears corrupted (too small)"
    
    return True, ""


def diagnose_whatsapp():
    """Run diagnostics on WhatsApp configuration."""
    st.subheader("🔍 WhatsApp Configuration Diagnostics")
    
    with st.spinner("Running diagnostics..."):
        results = []
        
        # Check 1: Credentials
        if WHATSAPP_TOKEN and len(WHATSAPP_TOKEN) > 50:
            results.append(("✅", "Token", f"Present ({len(WHATSAPP_TOKEN)} chars)"))
        else:
            results.append(("❌", "Token", "Missing or invalid"))
        
        if WHATSAPP_PHONE_ID:
            results.append(("✅", "Phone ID", WHATSAPP_PHONE_ID))
        else:
            results.append(("❌", "Phone ID", "Missing"))
        
        if WHATSAPP_TO:
            to_clean = WHATSAPP_TO.replace("+", "").strip()
            results.append(("✅", "Recipient", f"{WHATSAPP_TO} → API: {to_clean}"))
        else:
            results.append(("❌", "Recipient", "Missing"))
        
        # Check 2: API connectivity
        try:
            url = f"https://graph.facebook.com/v21.0/{WHATSAPP_PHONE_ID}"
            headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
            resp = requests.get(url, headers=headers, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                results.append(("✅", "API Connection", "Connected"))
                results.append(("ℹ️", "Display Number", data.get("display_phone_number", "N/A")))
                results.append(("ℹ️", "Verified Name", data.get("verified_name", "N/A")))
                results.append(("ℹ️", "Quality Rating", data.get("quality_rating", "N/A")))
            elif resp.status_code == 401:
                results.append(("❌", "API Connection", "Token expired/invalid"))
            else:
                results.append(("⚠️", "API Connection", f"Error {resp.status_code}"))
        except Exception as e:
            results.append(("❌", "API Connection", str(e)))
        
        # Display results
        for icon, key, value in results:
            st.text(f"{icon} {key}: {value}")
        
        st.info(
            "**Next Steps:**\n"
            "1. Add recipient to test numbers in Meta Console (WITH '+')\n"
            "2. Verify with 6-digit code\n"
            "3. Use recipient WITHOUT '+' in API calls (handled automatically)\n"
            "4. Check quality rating is not 'Low'\n"
            "5. Ensure phone status is 'Connected'"
        )


# -------------------------
# MAIN UI
# -------------------------

enable_drive = bool(GDRIVE_SA_JSON and GDRIVE_FOLDER_ID and GOOGLE_LIBS_AVAILABLE)
enable_whatsapp = bool(WHATSAPP_TOKEN and WHATSAPP_PHONE_ID and WHATSAPP_TO)

st.subheader("Upload Options")
col1, col2 = st.columns(2)
with col1:
    do_drive = st.checkbox(
        "📁 Upload to Google Drive", 
        value=enable_drive,
        help="Creates a shareable public link"
    )
with col2:
    do_whatsapp = st.checkbox(
        "💬 Send via WhatsApp", 
        value=enable_whatsapp,
        help="Sends PDF as document attachment"
    )

if do_drive and not enable_drive:
    st.error("❌ Drive not configured. Check service account JSON and libraries.")

if do_whatsapp and not enable_whatsapp:
    st.error("❌ WhatsApp not configured. Check credentials.")

st.write("---")

# File uploader - PDF only
uploaded = st.file_uploader(
    "📄 Choose PDF file to upload",
    type=['pdf'],
    help="Maximum size: 100MB"
)

caption = st.text_area(
    "Optional message/caption",
    placeholder="Enter a message to include with the PDF...",
    max_chars=1024,
    help="WhatsApp caption limit: 1024 characters"
)

if uploaded:
    file_bytes = uploaded.getvalue()
    file_size_mb = len(file_bytes) / (1024 * 1024)
    
    st.info(f"**File:** {uploaded.name} | **Size:** {file_size_mb:.2f} MB")
    
    # Validate PDF
    is_valid, error_msg = validate_pdf(file_bytes, uploaded.name)
    
    if not is_valid:
        st.error(f"❌ Validation failed: {error_msg}")
    else:
        st.success("✅ Valid PDF file")
        
        if st.button("🚀 Start Upload & Send", type="primary"):
            try:
                drive_link = None
                whatsapp_response = None
                
                # Upload to Drive
                if do_drive:
                    with st.spinner("📤 Uploading to Google Drive..."):
                        file_id = upload_pdf_to_drive(uploaded.name, file_bytes)
                        st.success(f"✅ Uploaded to Drive (ID: {file_id})")
                    
                    with st.spinner("🔗 Creating shareable link..."):
                        drive_link = make_drive_file_public(file_id)
                        st.success(f"✅ Drive link: {drive_link}")
                
                # Send via WhatsApp
                if do_whatsapp:
                    with st.spinner("📤 Uploading PDF to WhatsApp..."):
                        media_id = upload_pdf_to_whatsapp(file_bytes, uploaded.name)
                        st.success(f"✅ Uploaded to WhatsApp (media_id: {media_id})")
                    
                    with st.spinner("💬 Sending WhatsApp message..."):
                        whatsapp_response = send_pdf_via_whatsapp(
                            media_id, 
                            uploaded.name, 
                            caption
                        )
                        st.success("✅ WhatsApp message sent!")
                        
                        # Show message ID
                        if "messages" in whatsapp_response:
                            msg_id = whatsapp_response["messages"][0]["id"]
                            st.code(f"Message ID: {msg_id}", language="text")
                
                # If only Drive (no WhatsApp direct), optionally send link
                if drive_link and not do_whatsapp and enable_whatsapp:
                    send_link = st.checkbox("Send Drive link via WhatsApp text?")
                    if send_link:
                        with st.spinner("💬 Sending Drive link..."):
                            body = (caption + "\n\n" if caption else "") + f"📄 PDF Report: {drive_link}"
                            resp = send_whatsapp_text(body)
                            st.success("✅ Link sent via WhatsApp!")
                
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Operation failed: {str(e)}")
                with st.expander("🐛 Debug Info"):
                    st.code(traceback.format_exc())

else:
    st.info("👆 Upload a PDF file to begin")

# -------------------------
# DIAGNOSTICS & TESTING
# -------------------------

st.write("---")
st.header("🔧 Developer Tools")

with st.expander("🔍 Run WhatsApp Diagnostics"):
    if st.button("Check Configuration"):
        diagnose_whatsapp()

with st.expander("✉️ Send Test Text Message"):
    test_msg = st.text_input("Test message", value="Hello from PDF uploader!")
    if st.button("Send Test"):
        try:
            resp = send_whatsapp_text(test_msg)
            st.success("✅ Test message sent!")
            st.json(resp)
        except Exception as e:
            st.error(f"❌ Failed: {str(e)}")

st.write("---")
st.caption(
    "⚠️ **Security Note:** This app has embedded credentials for testing. "
    "Move to Streamlit Secrets for production use."
)
