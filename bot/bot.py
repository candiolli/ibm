#!/usr/bin/env python3
"""Bot do Telegram que conversa com o Claude Code dentro do acervo.

Cada mensagem recebida vira um `claude -p` rodando na raiz do repositório,
retomando a mesma sessão, então dá para montar programas de culto, buscar
músicas e fazer commit/push pelo celular como fazemos no terminal.

Configuração (arquivo ~/.config/ibm-bot/env, lido pelo systemd):
    TELEGRAM_TOKEN=123456:ABC...        token do @BotFather
    TELEGRAM_ALLOWED_IDS=111111111      ids de usuário autorizados, separados por vírgula

Comandos no chat:
    /novo              começa uma conversa nova (esquece o contexto)
    /arquivo <caminho> envia um arquivo do acervo (pdf, pptx, md...)
    /id                mostra seu id do Telegram
"""

import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STATE_FILE = Path(os.environ.get("IBM_BOT_STATE", Path.home() / ".local/state/ibm-bot/sessions.json"))
TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
ALLOWED_IDS = {int(x) for x in os.environ.get("TELEGRAM_ALLOWED_IDS", "").replace(" ", "").split(",") if x}
CLAUDE = os.environ.get("CLAUDE_BIN", "claude")
CLAUDE_TIMEOUT = int(os.environ.get("CLAUDE_TIMEOUT", "900"))
API = f"https://api.telegram.org/bot{TOKEN}"
MAX_MSG = 4000  # limite do Telegram é 4096

# O que o Claude pode fazer sem pedir permissão (não há ninguém para aprovar no celular).
ALLOWED_TOOLS = [
    "Read", "Grep", "Glob", "Edit", "Write",
    "Bash(git status:*)", "Bash(git diff:*)", "Bash(git log:*)", "Bash(git show:*)",
    "Bash(git add:*)", "Bash(git commit:*)", "Bash(git push:*)", "Bash(git pull:*)",
    "Bash(ls:*)", "Bash(find:*)", "Bash(grep:*)", "Bash(pdftotext:*)",
    "Bash(python3 tools/build.py:*)",
]

SYSTEM_PROMPT = """\
Você está sendo acessado por um bot do Telegram, pelo celular do Silas, dirigente do \
ministério de louvor. Responda em português, de forma curta e direta, em texto simples \
(o Telegram não renderiza tabelas Markdown). Os programas de culto ficam em cultos/ \
e o acervo em Musicas/; siga o padrão dos programas já existentes. \
Faça commit e push só quando ele pedir. \
Para mandar um arquivo do acervo para ele, escreva numa linha sozinha: \
ENVIAR: <caminho relativo à raiz do repositório>"""

SEND_RE = re.compile(r"^ENVIAR:\s*(.+?)\s*$", re.MULTILINE)


def log(*args):
    print(time.strftime("%Y-%m-%d %H:%M:%S"), *args, flush=True)


def tg(method, http_timeout=60, **params):
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(f"{API}/{method}", data=data, timeout=http_timeout) as resp:
        return json.load(resp)


def send_text(chat_id, text):
    text = text.strip() or "(sem resposta)"
    for i in range(0, len(text), MAX_MSG):
        tg("sendMessage", chat_id=chat_id, text=text[i:i + MAX_MSG])


def send_file(chat_id, rel_path):
    path = (REPO / rel_path).resolve()
    if not path.is_relative_to(REPO) or not path.is_file():
        send_text(chat_id, f"Arquivo não encontrado no acervo: {rel_path}")
        return
    boundary = uuid.uuid4().hex
    body = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"chat_id\"\r\n\r\n{chat_id}\r\n"
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"document\"; "
        f"filename*=UTF-8''{urllib.parse.quote(path.name)}\r\n"
        "Content-Type: application/octet-stream\r\n\r\n"
    ).encode() + path.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        f"{API}/sendDocument", data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    try:
        urllib.request.urlopen(req, timeout=300).close()
    except urllib.error.HTTPError as e:
        send_text(chat_id, f"Não consegui enviar {path.name}: {e.read().decode(errors='replace')[:300]}")


def load_sessions():
    try:
        return json.loads(STATE_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_sessions(sessions):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(sessions))


def ask_claude(prompt, session_id):
    cmd = [
        CLAUDE, "-p", prompt,
        "--output-format", "json",
        "--permission-mode", "acceptEdits",
        "--allowedTools", ",".join(ALLOWED_TOOLS),
        "--append-system-prompt", SYSTEM_PROMPT,
    ]
    if session_id:
        cmd += ["--resume", session_id]
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=CLAUDE_TIMEOUT)
    try:
        out = json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise RuntimeError((proc.stderr or proc.stdout or "sem saída").strip()[-1500:])
    if out.get("is_error"):
        raise RuntimeError(out.get("result") or json.dumps(out)[:1500])
    return out.get("result", ""), out.get("session_id")


def handle(msg, sessions):
    chat_id = msg["chat"]["id"]
    user_id = msg.get("from", {}).get("id")
    text = (msg.get("text") or msg.get("caption") or "").strip()

    if text == "/id":
        send_text(chat_id, f"Seu id: {user_id}")
        return
    if user_id not in ALLOWED_IDS:
        log("recusado", user_id, text[:50])
        send_text(chat_id, "Acesso não autorizado.")
        return
    if not text:
        send_text(chat_id, "Por enquanto só entendo texto.")
        return
    if text in ("/start", "/novo"):
        sessions.pop(str(chat_id), None)
        save_sessions(sessions)
        send_text(chat_id, "Conversa nova. Pode mandar o que precisa para o culto.")
        return
    if text.startswith("/arquivo"):
        send_file(chat_id, text.removeprefix("/arquivo").strip())
        return

    log("pergunta", chat_id, text[:80])
    tg("sendChatAction", chat_id=chat_id, action="typing")
    sid = sessions.get(str(chat_id))
    try:
        reply, new_sid = ask_claude(text, sid)
    except subprocess.TimeoutExpired:
        send_text(chat_id, "Demorou demais e eu interrompi. Tente de novo ou divida o pedido.")
        return
    except RuntimeError as e:
        if sid:  # sessão pode ter sumido; tenta de novo do zero
            log("erro com sessão, recomeçando:", e)
            sessions.pop(str(chat_id), None)
            try:
                reply, new_sid = ask_claude(text, None)
            except Exception as e2:
                send_text(chat_id, f"Erro: {e2}")
                return
        else:
            send_text(chat_id, f"Erro: {e}")
            return

    if new_sid:
        sessions[str(chat_id)] = new_sid
        save_sessions(sessions)
    files = SEND_RE.findall(reply)
    send_text(chat_id, SEND_RE.sub("", reply))
    for f in files:
        send_file(chat_id, f)


def main():
    if not TOKEN:
        sys.exit("TELEGRAM_TOKEN não definido (veja ~/.config/ibm-bot/env)")
    if not ALLOWED_IDS:
        log("aviso: TELEGRAM_ALLOWED_IDS vazio — ninguém está autorizado; use /id para descobrir o seu")
    sessions = load_sessions()
    offset = None
    log("bot iniciado em", REPO)
    while True:
        try:
            params = {"timeout": 50, "allowed_updates": json.dumps(["message"])}
            if offset is not None:
                params["offset"] = offset
            updates = tg("getUpdates", http_timeout=70, **params).get("result", [])
        except Exception as e:  # sem rede no boot, Telegram fora etc.
            log("falha no getUpdates:", e)
            time.sleep(10)
            continue
        for upd in updates:
            offset = upd["update_id"] + 1
            if "message" in upd:
                try:
                    handle(upd["message"], sessions)
                except Exception as e:
                    log("erro tratando mensagem:", repr(e))


if __name__ == "__main__":
    main()
