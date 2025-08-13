# convlog.py
import os, json, time
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False

from foodrec.config.structure.paths import CONVERSATION

LOG_DIR = Path(CONVERSATION)
LOG_DIR.mkdir(parents=True, exist_ok=True)

def _lock(f):
    if HAS_FCNTL:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
def _unlock(f):
    if HAS_FCNTL:
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

def _cid(env_override: Optional[str] = None) -> str:
    cid = env_override or os.getenv("CHAT_ID")
    if not cid:
        raise RuntimeError("CHAT_ID not set")
    return cid

def record(role: str, content: str, meta: Optional[Dict[str, Any]] = None, chat_id: Optional[str] = None):
    cid = _cid(chat_id)
    path = LOG_DIR / f"{cid}.jsonl"
    entry = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "chat_id": cid,
        "role": role,
        "content": content,
        "meta": meta or None,
    }
    with open(path, "a", encoding="utf-8") as f:
        _lock(f)
        f.write(json.dumps(entry, ensure_ascii=False))
        f.write("\n")
        _unlock(f)

def finalize_to_json(chat_id: Optional[str] = None):
    cid = _cid(chat_id)
    src = LOG_DIR / f"{cid}.jsonl"
    if not src.exists():
        return
    dst = LOG_DIR / f"{cid}.json"
    lines = [json.loads(line) for line in src.read_text(encoding="utf-8").splitlines() if line.strip()]
    dst.write_text(json.dumps(lines, ensure_ascii=False, indent=2), encoding="utf-8")

class ConversationSession:
    """Context Manager: setzt CHAT_ID, finalisiert am Ende automatisch."""
    def __init__(self, chat_id: str):
        self.chat_id = chat_id
        self._prev = None
    def __enter__(self):
        self._prev = os.environ.get("CHAT_ID")
        os.environ["CHAT_ID"] = self.chat_id
        record("system", "conversation started", meta={"chat_id": self.chat_id})
        return self
    def __exit__(self, exc_type, exc, tb):
        if exc:
            record("error", f"{exc_type.__name__}: {exc}")
        record("system", "conversation ended")
        finalize_to_json(self.chat_id)
        # vorheriges ENV zurücksetzen
        if self._prev is None:
            os.environ.pop("CHAT_ID", None)
        else:
            os.environ["CHAT_ID"] = self._prev
