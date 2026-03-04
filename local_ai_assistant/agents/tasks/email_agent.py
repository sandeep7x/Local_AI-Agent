import os
import json
import email
from email.header import decode_header
from dotenv import load_dotenv

load_dotenv()

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
_CACHE_PATH = os.path.join(_PROJECT_ROOT, "data", "email_cache.json")

# Try to import imapclient but allow the codebase to run without it (local-only mode)
try:
    import imapclient  # may not be installed in pure-local setups
    IMAP_AVAILABLE = True
except Exception:
    imapclient = None
    IMAP_AVAILABLE = False


if IMAP_AVAILABLE:
    class EmailAgent:
        def __init__(self):
            self.host = os.getenv("EMAIL_HOST")
            self.port = int(os.getenv("EMAIL_PORT")) if os.getenv("EMAIL_PORT") else None
            self.user = os.getenv("EMAIL_USER")
            self.password = os.getenv("EMAIL_PASS")
            self.client = None

        def connect(self):
            self.client = imapclient.IMAPClient(self.host, ssl=True)
            self.client.login(self.user, self.password)

        def decode_str(self, value):
            if not value:
                return ""
            decoded, charset = decode_header(value)[0]
            if isinstance(decoded, bytes):
                return decoded.decode(charset or "utf-8", errors="ignore")
            return decoded

        def get_body(self, msg):
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        return part.get_payload(decode=True).decode("utf-8", errors="ignore")
            else:
                return msg.get_payload(decode=True).decode("utf-8", errors="ignore")
            return ""

        def fetch_unread_emails(self):
            """Fetch unread (UNSEEN) emails from INBOX."""
            return self.fetch_recent_emails(folder="INBOX", last_n=100, unseen_only=False)

        def fetch_recent_emails(self, folder="INBOX", last_n=100, unseen_only=False):
            """Fetch the most recent `last_n` emails (read + unread) from `folder`."""
            self.connect()
            self.client.select_folder(folder)

            if unseen_only:
                msg_ids = self.client.search(["UNSEEN"])
            else:
                msg_ids = self.client.search(["ALL"])

            # Take the last_n most recent (highest IDs)
            msg_ids = sorted(msg_ids)[-last_n:]

            emails = []
            for msgid in msg_ids:
                raw_msg = self.client.fetch(msgid, ["RFC822"])
                msg = email.message_from_bytes(raw_msg[msgid][b"RFC822"])
                emails.append({
                    "id": str(msgid),
                    "subject": self.decode_str(msg["Subject"]),
                    "from": self.decode_str(msg["From"]),
                    "date": msg["Date"],
                    "body": self.get_body(msg)
                })

            return emails

        def save_to_cache(self, emails):
            path = _CACHE_PATH

            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception:
                    data = {"emails": []}
            else:
                data = {"emails": []}

            # Deduplicate by email ID so re-fetching doesn't add duplicates
            existing_ids = {str(e.get("id")) for e in data["emails"]}
            new_only = [e for e in emails if str(e.get("id")) not in existing_ids]

            data["emails"].extend(new_only)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            return f"Saved {len(new_only)} new email(s) to cache (skipped {len(emails)-len(new_only)} duplicates)."

else:
    # Fallback EmailAgent for local-only demos where imapclient isn't installed
    class EmailAgent:
        def __init__(self):
            self.available = False

        def connect(self):
            raise RuntimeError("IMAP not available in this environment. Install 'imapclient' to enable IMAP fetching.")

        def fetch_unread_emails(self):
            # Return empty list so the rest of the assistant can operate on local cached emails
            return []

        def save_to_cache(self, emails):
            path = _CACHE_PATH

            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception:
                    data = {"emails": []}
            else:
                data = {"emails": []}

            data["emails"].extend(emails)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            return "Emails saved to local cache (imap disabled)."