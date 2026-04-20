# Proxy LLM — Deploy no EasyPanel

## O que é isso
Proxy FastAPI que recebe requests dos alunos (com token simples),
valida o token e repassa para api.anthropic.com com a sua API key real.

## Estrutura
```
proxy/
├── main.py           # aplicação FastAPI
├── requirements.txt  # dependências
├── Dockerfile        # imagem para deploy
└── teste_conexao.ipynb  # notebook de validação para os alunos
```

## Deploy no EasyPanel

### 1. Criar o serviço
- No EasyPanel, crie um novo serviço do tipo **App**
- Escolha **Dockerfile** como método de build
- Aponte para este repositório/pasta

### 2. Configurar variável de ambiente
Na aba **Environment** do serviço, adicione:
```
ANTHROPIC_API_KEY=sk-ant-sua-chave-aqui
```

### 3. Configurar domínio
- Na aba **Domains**, adicione um domínio (ex: `llm.seudominio.com`)
- Ative HTTPS (Let's Encrypt automático no EasyPanel)
- Porta interna: `8000`

### 4. Fazer o deploy
- Clique em **Deploy**
- Aguarde o build (~1-2 minutos)

### 5. Validar
Acesse: `https://llm.seudominio.com/health`

Resposta esperada:
```json
{
  "status": "ok",
  "anthropic_key_configured": true,
  "alunos_registrados": 10
}
```

## Personalizar tokens dos alunos

Edite o dicionário `VALID_TOKENS` em `main.py`:
```python
VALID_TOKENS = {
    "aluno-01": "João Silva",
    "aluno-02": "Maria Santos",
    ...
}
```

## Testar localmente antes do deploy
```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-sua-chave-aqui
uvicorn main:app --reload
```

Acesse: http://localhost:8000/health
