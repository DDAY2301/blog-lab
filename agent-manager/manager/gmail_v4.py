from __future__ import annotations

import argparse
import base64
import json
import os
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from typing import Any

from .db_v3 import StoreV3

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


class GmailV4:
    def __init__(self, store: StoreV3 | None = None) -> None:
        self.store = store
        root = Path(__file__).resolve().parents[1]
        self.enabled = os.getenv("GMAIL_REPORTING_ENABLED", "0").strip().lower() in {"1","true","yes","on"}
        self.recipient = os.getenv("REPORT_TO_EMAIL", "").strip()
        self.client_file = Path(
            os.getenv("GMAIL_OAUTH_CLIENT_FILE", str(root / "data" / "gmail-client-secret.json"))
        ).expanduser()
        self.token_file = Path(
            os.getenv("GMAIL_OAUTH_TOKEN_FILE", str(root / "data" / "gmail-token.json"))
        ).expanduser()

    def auth_state(self) -> str:
        if not self.enabled:
            return "DISABLED"
        if not self.recipient:
            return "RECIPIENT_REQUIRED"
        if not self.client_file.exists():
            return "CLIENT_SECRET_REQUIRED"
        if not self.token_file.exists():
            return "AUTH_REQUIRED"
        try:
            self._credentials()
            return "CONFIGURED"
        except Exception:
            return "AUTH_REQUIRED"

    def _credentials(self):
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials

        creds = Credentials.from_authorized_user_file(str(self.token_file), SCOPES)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            self.token_file.write_text(creds.to_json(), encoding="utf-8")
        if not creds.valid:
            raise RuntimeError("Gmail OAuth credentials are not valid.")
        return creds

    def authorize(self) -> dict[str, Any]:
        if not self.client_file.exists():
            raise FileNotFoundError(
                f"Google OAuth desktop client JSON not found: {self.client_file}"
            )
        from google_auth_oauthlib.flow import InstalledAppFlow

        flow = InstalledAppFlow.from_client_secrets_file(str(self.client_file), SCOPES)
        creds = flow.run_local_server(host="127.0.0.1", port=0, open_browser=True)
        self.token_file.parent.mkdir(parents=True, exist_ok=True)
        self.token_file.write_text(creds.to_json(), encoding="utf-8")
        return {"ok": True, "token_file": str(self.token_file)}

    def send(self, subject: str, body: str, recipient: str | None = None) -> str:
        if not self.enabled:
            raise RuntimeError("Gmail reporting is disabled.")
        to = (recipient or self.recipient).strip()
        if not to:
            raise RuntimeError("REPORT_TO_EMAIL is not configured.")

        from googleapiclient.discovery import build

        service = build("gmail", "v1", credentials=self._credentials(), cache_discovery=False)
        profile = service.users().getProfile(userId="me").execute()
        sender = str(profile.get("emailAddress") or "").strip()
        if not sender:
            raise RuntimeError("Could not determine authenticated Gmail sender address.")

        msg = EmailMessage()
        msg["From"] = sender
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")
        sent = service.users().messages().send(userId="me", body={"raw": raw}).execute()
        return str(sent.get("id", ""))

    def flush_queue(self, limit: int = 20) -> dict[str, int]:
        if not self.store or self.auth_state() != "CONFIGURED":
            return {"sent": 0, "failed": 0}
        rows = self.store.query(
            "SELECT * FROM email_queue WHERE status='pending' ORDER BY priority ASC,id ASC LIMIT ?",
            (max(1, min(limit, 100)),),
        )
        sent = failed = 0
        for row in rows:
            try:
                message_id = self.send(row["subject"], row["body"], row.get("recipient") or self.recipient)
                self.store.execute(
                    "UPDATE email_queue SET status='sent',attempts=attempts+1,last_error=NULL WHERE id=?",
                    (row["id"],),
                )
                self.store.action(
                    "gmail-v4",
                    "send_email",
                    str(row["id"]),
                    "sent",
                    {"message_id": message_id, "recipient": row.get("recipient") or self.recipient},
                )
                sent += 1
            except Exception as exc:
                attempts = int(row.get("attempts") or 0) + 1
                status = "failed" if attempts >= 5 else "pending"
                self.store.execute(
                    "UPDATE email_queue SET status=?,attempts=?,last_error=? WHERE id=?",
                    (status, attempts, str(exc)[:1000], row["id"]),
                )
                failed += 1
        return {"sent": sent, "failed": failed}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authorize", action="store_true")
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()

    gmail = GmailV4()
    if args.authorize:
        print(json.dumps(gmail.authorize(), indent=2))
    if args.test:
        mid = gmail.send(
            "Agent Manager V4 - Gmail test",
            f"Gmail reporting is working. Test sent at {datetime.now().isoformat(timespec='seconds')}.",
        )
        print(json.dumps({"ok": True, "message_id": mid}, indent=2))


if __name__ == "__main__":
    main()
