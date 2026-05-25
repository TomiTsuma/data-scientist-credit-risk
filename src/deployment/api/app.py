from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router

try:
    from src.ai_platform.api import router as ai_router
except ImportError:
    ai_router = None

app = FastAPI(title='Sunculture Data Science API')
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://localhost:8080',
        'http://127.0.0.1:8080',
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(router, prefix='/api')
if ai_router is not None:
    app.include_router(ai_router, prefix='/api/ai')

@app.get('/')
def root():
    return {
        'status': 'ok',
        'service': 'sunculture-data-science',
        'ai_chat': '/api/ai/v1/chat/stream' if ai_router else None,
    }
