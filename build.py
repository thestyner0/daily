#!/usr/bin/env python3
"""Daily 대시보드 빌드 도구.

  python3 build.py extract          # app.enc → src/app.html, src/data.json (비밀번호 필요)
  python3 build.py build            # src/ → app.enc (암호화)

비밀번호는 환경변수 DAILY_PW 로 받습니다. 원본(src/)은 저장소에 커밋하지 않습니다(.gitignore).
"""
import base64, json, os, re, sys
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
ITER = 200_000
MARK_A = "<!--DAILY-SRC-DATA:"
MARK_B = ":DAILY-SRC-DATA-->"


def key(pw, salt):
    return PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(pw.encode())


def build(pw):
    tpl = (SRC / "app.html").read_text(encoding="utf-8")
    data = json.loads((SRC / "data.json").read_text(encoding="utf-8"))
    dj = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    assert "/*DATA*/" in tpl
    html = tpl.replace("/*DATA*/", dj)
    # 템플릿 원본을 같이 넣어 두어 extract 로 되살릴 수 있게 함
    html += "\n" + MARK_A + base64.b64encode(tpl.encode()).decode() + MARK_B + "\n"
    salt, iv = os.urandom(16), os.urandom(12)
    ct = AESGCM(key(pw, salt)).encrypt(iv, html.encode(), None)
    b = lambda x: base64.b64encode(x).decode()
    (ROOT / "app.enc").write_text(json.dumps({"v": 1, "iter": ITER, "salt": b(salt), "iv": b(iv), "ct": b(ct)}))
    print("built app.enc", len(html), "chars;", len(data.get("events", [])), "events,", len(data.get("hotplaces", [])), "places")


def extract(pw):
    j = json.loads((ROOT / "app.enc").read_text())
    d = lambda x: base64.b64decode(x)
    html = AESGCM(key(pw, d(j["salt"]))).decrypt(d(j["iv"]), d(j["ct"]), None).decode()
    tpl = base64.b64decode(html.split(MARK_A)[1].split(MARK_B)[0]).decode()
    m = re.search(r'<script id="daily-data" type="application/json">(.*?)</script>', html, re.S)
    data = json.loads(m.group(1).replace("<\\/", "</"))
    SRC.mkdir(exist_ok=True)
    (SRC / "app.html").write_text(tpl, encoding="utf-8")
    (SRC / "data.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print("extracted src/app.html, src/data.json (updated", data.get("updated"), ")")


if __name__ == "__main__":
    pw = os.environ.get("DAILY_PW") or sys.exit("DAILY_PW 환경변수가 필요합니다")
    {"build": build, "extract": extract}[sys.argv[1]](pw)
