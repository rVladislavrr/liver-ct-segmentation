from starlette.middleware.cors import CORSMiddleware

from src.create_app import create_app
from src.api.v1 import router
from src.middlewares.authmiddleware import AuthMiddleware
from src.middlewares.logmiddleware import LogExecutionTimeMiddleware

app = create_app()
origins = [
    "http://26.25.133.178:3000",
    "https://26.25.133.178:3000",
    "http://26.25.133.178",
    "https://26.25.133.178",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",

    "http://192.168.65.1:3000"
]
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LogExecutionTimeMiddleware)
app.add_middleware(AuthMiddleware)