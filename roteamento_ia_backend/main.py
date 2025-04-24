from fastapi import FastAPI
from roteamento_ia_backend.routers import prompts, execute

app = FastAPI(
    title="Roteamento de IA",
    version="0.1.0",
    description="API para gerenciar prompts e executar IAs"
)

app.include_router(prompts.router, prefix="/prompts", tags=["prompts"])
app.include_router(execute.router, prefix="/execute", tags=["execute"])
