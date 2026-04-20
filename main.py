"""
Proxy LLM — Anthropic
Redireciona requests dos alunos para api.anthropic.com
injetando a API key real e validando tokens dos alunos.
"""

import os
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from dotenv import load_dotenv
import json

load_dotenv()  # carrega .env em dev; em produção as vars do ambiente têm precedência

app = FastAPI(title="LLM Proxy — Curso Agentes IA")

# ---------------------------------------------------------
# Configuração
# ---------------------------------------------------------

# Em dev: lido do .env  |  Em produção: injetado pelo painel do EasyPanel
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = os.environ.get("MODEL", "claude-haiku-4-5-20251001")

# Tokens válidos dos alunos → nome para logging
# Formato da env var: "token1:Nome 1,token2:Nome 2,..."
def _parse_tokens(raw: str) -> dict:
    result = {}
    for entry in raw.split(","):
        entry = entry.strip()
        if ":" in entry:
            token, name = entry.split(":", 1)
            result[token.strip()] = name.strip()
    return result

VALID_TOKENS = _parse_tokens(os.environ.get("VALID_TOKENS", ""))

ANTHROPIC_BASE_URL = "https://api.anthropic.com"

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def get_aluno(request: Request) -> str:
    """Valida o token do aluno e retorna o nome dele."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token ausente. Use: Authorization: Bearer aluno-XX")
    
    token = auth.removeprefix("Bearer ").strip()
    
    if token not in VALID_TOKENS:
        raise HTTPException(status_code=403, detail=f"Token inválido: '{token}'")
    
    return VALID_TOKENS[token]


def build_headers(original_headers: dict) -> dict:
    """Monta os headers para repassar à Anthropic, injetando a API key real."""
    headers = {
        "content-type": "application/json",
        "anthropic-version": original_headers.get("anthropic-version", "2023-06-01"),
        "x-api-key": ANTHROPIC_API_KEY,
    }
    # Repassa beta headers se existirem
    if "anthropic-beta" in original_headers:
        headers["anthropic-beta"] = original_headers["anthropic-beta"]
    return headers


# ---------------------------------------------------------
# Rota principal — proxy de /v1/messages
# ---------------------------------------------------------

@app.post("/v1/messages")
async def proxy_messages(request: Request):
    aluno = get_aluno(request)
    
    body = await request.body()

    try:
        payload = json.loads(body)
        payload["model"] = MODEL  # força o modelo configurado, ignorando o do cliente
        body = json.dumps(payload).encode()
        n_messages = len(payload.get("messages", []))
        stream = payload.get("stream", False)
        print(f"[{aluno}] model={MODEL} messages={n_messages} stream={stream}")
    except Exception:
        pass

    upstream_headers = build_headers(dict(request.headers))

    # --- Streaming ---
    if payload.get("stream", False):
        async def stream_generator():
            async with httpx.AsyncClient(timeout=120) as client:
                async with client.stream(
                    "POST",
                    f"{ANTHROPIC_BASE_URL}/v1/messages",
                    headers=upstream_headers,
                    content=body,
                ) as upstream:
                    if upstream.status_code != 200:
                        error = await upstream.aread()
                        yield error
                        return
                    async for chunk in upstream.aiter_bytes():
                        yield chunk

        return StreamingResponse(
            stream_generator(),
            media_type="text/event-stream",
            headers={"x-aluno": aluno},
        )

    # --- Não-streaming ---
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            f"{ANTHROPIC_BASE_URL}/v1/messages",
            headers=upstream_headers,
            content=body,
        )

    return JSONResponse(
        content=response.json(),
        status_code=response.status_code,
        headers={"x-aluno": aluno},
    )


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.get("/health")
def health():
    has_key = bool(ANTHROPIC_API_KEY)
    return {
        "status": "ok",
        "anthropic_key_configured": has_key,
        "model": MODEL,
        "alunos_registrados": len(VALID_TOKENS),
    }


@app.get("/")
def root():
    return {"message": "Proxy LLM do curso. Endpoint: POST /v1/messages"}
