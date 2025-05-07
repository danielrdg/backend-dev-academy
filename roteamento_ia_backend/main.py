from fastapi import FastAPI
from contextlib import asynccontextmanager
from roteamento_ia_backend.routers import prompts, execute
from roteamento_ia_backend.core.logging import logger
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
    "http://localhost:27017",
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    logger.info("Aplicacao iniciada")
    yield
    # shutdown
    logger.info("Aplicacao encerrando")

app = FastAPI(
    title="Roteamento de IA",
    version="0.1.0",
    description="API para gerenciar prompts e executar IAs",
    lifespan=lifespan,       
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prompts.router, prefix="/prompts", tags=["prompts"])
app.include_router(execute.router, prefix="/execute", tags=["execute"])