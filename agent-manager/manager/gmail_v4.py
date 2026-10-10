from __future__ import annotations

import argparse
import base64
import json
import os
from datetime import datetime
from email.message import EmailMessage
from email.utils import parseaddr
from pathlib import Path
from typing import Any

from .db_v3 import StoreV3

SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"
COMMAND_SCOPE = "https://www.googleapis.com/auth/gmail.modify"
SEND_IMPLEMENTATION = "gmail-send-only-v2"
COMMAND_IMPLEMENTATION = "gmail-command-bus-v3"


class GmailV4:
    def __init__(self, store: StoreV3 | None = None) -> None:
        self.store = store
        root = Path(__file__).resolve().parents[1]
        self.enabled = os.getenv("GMAIL_REPORTING_ENABLED", "0").strip().lower() in {"1","true","yes","on"}
        self.commands_enabled = os.getenv("GMAIL_COMMANDS_ENABLED", "0").strip().lower() in {"1","true","yes","on"}
        self.recipient = os.getenv("REPORT_TO_EMAIL", "").strip()
        self.sender = os.getenv("GMAIL_FROM_EMAIL", self.recipient).strip()
        self.client_file = Path(
            os.getenv("GMAIL_OAUTH_CLIENT_FILE", str(root / "data" / "gmail-client-secret.json"))
        ).expanduser()
        self.token_file = Path(
            os.getenv("GMAIL_OAUTH_TOKEN_FILE", str(root / "data" / "gmail-token.json"))
        ).expanduser()

    @property
    def scopes(self) -> list[str]:
        # The account already has gmail.send consent from reporting mode. During
        # incremental authorization Google returns the union of previously granted
        # and newly requested scopes. Request that union explicitly so oauthlib
        # does not reject the token response as a scope change.
        return [COMMAND_SCOPE, SEND_SCOPE] if self.commands_enabled else [SEND_SCOPE]

    @property
    def implementation(self) -> str:
        return COMMAND_IMPLEMENTATION if self.commands_enabled else SEND_IMPLEMENTATION

    def auth_state(self) -> str:
        if not self.enabled:
            return "DISABLED"
        if not self.recipient:
            return "RECIPIENT_REQUIRED"
        if not self.sender:
            return "SENDER_REQUIRED"
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

        creds = Credentials.from_authorized_user_file(str(self.token_file), self.scopes)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            self.token_file.write_text(creds.to_json(), encoding="utf-8")
        if not creds.valid:
            raise RuntimeError("Gmail OAuth credentials are not valid.")
        if not creds.has_scopes(self.scopes):
            raise RuntimeError("Gmail OAuth token does not include the scopes required by the current mode.")
        return creds

    def _service(self):
        from googleapiclient.discovery import build
        return build("gmail", "v1", credentials=self._credentials(), cache_discovery=False)

    def authorize(self) -> dict[str, Any]:
        if not self.client_file.exists():
            raise FileNotFoundError(
                f"Google OAuth desktop client JSON not found: {self.client_file}"
            )
        from google_auth_oauthlib.flow import InstalledAppFlow

        flow = InstalledAppFlow.from_client_secrets_file(str(self.client_file), self.scopes)
        creds = flow.run_local_server(
            host="127.0.0.1",
            port=0,
            open_browser=True,
            prompt="consent",
            include_granted_scopes="true",
        )
        self.token_file.parent.mkdir(parents=True, exist_ok=True)
        self.token_file.write_text(creds.to_json(), encoding="utf-8")
        return {
            "ok": True,
            "token_file": str(self.token_file),
            "scopes": self.scopes,
            "implementation": self.implementation,
        }

    def send(self, subject: str, body: str, recipient: str | None = None) -> str:
        if not self.enabled:
            raise RuntimeError("Gmail reporting is disabled.")
        to = (recipient or self.recipient).strip()
        if not to:
            raise RuntimeError("REPORT_TO_EMAIL is not configured.")
        sender = self.sender.strip()
        if not sender:
            raise RuntimeError("GMAIL_FROM_EMAIL is not configured.")

        service = self._service()
        msg = EmailMessage()
        msg["From"] = sender
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")
        sent = service.users().messages().send(userId="me", body={"raw": raw}).execute()
        return str(sent.get("id", ""))

    def list_messages(self, query: str, max_results: int = 20) -> list[dict[str, str]]:
        if not self.commands_enabled:
            raise RuntimeError("Gmail command mode is disabled.")
        service = self._service()
        data = service.users().messages().list(
            userId="me",
            q=query,
            maxResults=max(1, min(max_results, 100)),
        ).execute()
        return [
            {"id": str(row.get("id", "")), "threadId": str(row.get("threadId", ""))}
            for row in data.get("messages", [])
            if row.get("id")
        ]

    def get_message(self, message_id: str) -> dict[str, Any]:
        if not self.commands_enabled:
            raise RuntimeError("Gmail command mode is disabled.")
        service = self._service()
        return service.users().messages().get(
            userId="me",
            id=message_id,
            format="full",
        ).execute()

    @staticmethod
    def _decode_body(data: str) -> str:
        if not data:
            return ""
        raw = base64.urlsafe_b64decode(data + "=" * ((4 - len(data) % 4) % 4))
        return raw.decode("utf-8", errors="replace")

    def message_details(self, message: dict[str, Any]) -> dict[str, Any]:
        payload = message.get("payload") or {}
        headers = {
            str(row.get("name", "")).lower(): str(row.get("value", ""))
            for row in payload.get("headers", [])
        }
        text_parts: list[str] = []
        attachments: list[dict[str, Any]] = []
        generated_index = 0

        def walk(part: dict[str, Any]) -> None:
            nonlocal generated_index
            mime = str(part.get("mimeType") or "application/octet-stream").lower()
            body = part.get("body") or {}
            filename = str(part.get("filename") or "").strip()
            part_headers = {
                str(row.get("name", "")).lower(): str(row.get("value", ""))
                for row in part.get("headers", []) or []
            }

            if mime == "text/plain" and body.get("data") and not filename:
                text_parts.append(self._decode_body(str(body.get("data"))))

            attachment_id = str(body.get("attachmentId") or "").strip()
            inline_data = str(body.get("data") or "").strip() if filename or mime.startswith("image/") else ""
            if attachment_id or (inline_data and (filename or mime.startswith("image/"))):
                generated_index += 1
                if not filename:
                    ext = {
                        "image/jpeg": ".jpg",
                        "image/png": ".png",
                        "image/webp": ".webp",
                        "image/gif": ".gif",
                    }.get(mime, ".bin")
                    filename = f"inline-{generated_index}{ext}"
                attachments.append(
                    {
                        "filename": filename,
                        "mime_type": mime,
                        "size": int(body.get("size") or 0),
                        "attachment_id": attachment_id,
                        "inline_data": inline_data if not attachment_id else "",
                        "content_id": part_headers.get("content-id", "").strip("<>"),
                        "content_disposition": part_headers.get("content-disposition", ""),
                    }
                )

            for child in part.get("parts", []) or []:
                walk(child)

        walk(payload)
        body = "\n\n".join(x.strip() for x in text_parts if x.strip()).strip()
        if not body:
            body = str(message.get("snippet") or "").strip()

        sender = parseaddr(headers.get("from", ""))[1].strip().lower()
        return {
            "id": str(message.get("id") or ""),
            "thread_id": str(message.get("threadId") or ""),
            "sender": sender,
            "subject": headers.get("subject", "").strip(),
            "body": body,
            "message_id_header": headers.get("message-id", "").strip(),
            "attachments": attachments,
        }

    def attachment_bytes(self, message_id: str, attachment: dict[str, Any]) -> bytes:
        attachment_id = str(attachment.get("attachment_id") or "").strip()
        if attachment_id:
            service = self._service()
            data = service.users().messages().attachments().get(
                userId="me",
                messageId=message_id,
                id=attachment_id,
            ).execute()
            encoded = str(data.get("data") or "")
            if not encoded:
                raise RuntimeError("Gmail attachment payload is empty.")
            return base64.urlsafe_b64decode(encoded + "=" * ((4 - len(encoded) % 4) % 4))

        encoded = str(attachment.get("inline_data") or "")
        if not encoded:
            raise RuntimeError("Gmail attachment has no downloadable payload.")
        return base64.urlsafe_b64decode(encoded + "=" * ((4 - len(encoded) % 4) % 4))

    def mark_read(self, message_id: str) -> None:
        service = self._service()
        service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"removeLabelIds": ["UNREAD"]},
        ).execute()

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
        print(json.dumps({"ok": True, "message_id": mid, "implementation": gmail.implementation}, indent=2))


if __name__ == "__main__":
    main()
