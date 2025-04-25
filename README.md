# 🚀 Roteamento de IA Backend

API em **FastAPI** + **MongoDB** para gerenciar prompts e rotear requisições a diferentes IAs (ChatGPT, Gemini).

---

## 📋 Visão Geral

Este projeto foi criado para:

- Receber inputs em texto (e, futuramente, imagens, áudios, PDF)
- Gerenciar prompts (CRUD) com variáveis dinâmicas
- Enviar requisições a modelos de IA e retornar respostas
- Registrar métricas de execução (latência, custo)

---

## 🛠 Tecnologias

- **Python 3.11+**
- **FastAPI** como servidor ASGI
- **Motor** (driver async para MongoDB)
- **Uvicorn** para desenvolvimento local
- **MongoDB** como banco de dados
- **Docker** / **docker-compose** (opcional)
- **Loguru** para loggings 

---

## ⚙️ Pré-requisitos

- Python 3.11+
- MongoDB rodando localmente ou em container
- (Opcional) Docker & docker-compose
- Conta e _API key_ da OpenAI (para integrar GPT)

---

## 📥 Instalação & Setup

1. **Clone este repositório**
   ```bash
   git clone https://github.com/seu-usuario/roteamento-ia-backend.git
   cd roteamento-ia-backend
   ```

2. **Crie e ative o virtualenv**
   ```bash
   python -m venv .venv
   # PowerShell
   . .\.venv\Scripts\Activate.ps1
   # ou Bash
   source .venv/bin/activate
   ```

3. **Instale as dependências**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente**
   Crie um arquivo `.env` na raiz com:
   ```dotenv
   MONGO_URI=mongodb://localhost:27017
   MONGO_DB=roteamento_ia
   OPENAI_API_KEY=sk-…
   ```

5. **(Opcional) Levante o MongoDB via Docker**
   ```bash
   docker-compose up -d db
   ```

---

## ▶️ Como rodar

```bash
uvicorn roteamento_ia_backend.main:app --reload
```

Acesse a documentação interativa em:
```
http://localhost:8000/docs
```

---

## 📖 Endpoints Principais

### Health check
```
GET /health
```

### Modelos disponíveis
```
GET /models
```

### CRUD de Prompts
- `POST /prompts`
- `GET  /prompts`
- `GET  /prompts/{id}`
- `PUT  /prompts/{id}`
- `DELETE /prompts/{id}`
- `GET  /prompts/{id}/metrics`

### Executar Prompt
```
POST /execute
```
**Payload exemplo**:
```json
{
  "prompt_id": "643f5b2e...",
  "input":   { "type": "text", "data": "Olá, IA!" },
  "variables": { "nome": "Gui" },
  "ia_model": "gpt-3.5-turbo"
}
```
**Resposta**:
```json
{
  "output": "Mock resposta: Olá, IA!",
  "latency_ms": 123,
  "cost": 0.0
}
```

---

## 📂 Estrutura do Projeto

```
roteamento-ia-backend/
├── .env
├── docker-compose.yml
├── requirements.txt
├── README.md
└── roteamento_ia_backend/
    ├── main.py
    ├── core/
    ├── db/
    └── routers/
```
{
  "output": "Mock resposta: Olá, IA!",
  "latency_ms": 123,
  "cost": 0.0
}
