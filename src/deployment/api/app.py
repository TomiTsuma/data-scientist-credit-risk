from fastapi import FastAPI
from .routes import router

app = FastAPI(title='Sunculture Data Science API')
app.include_router(router, prefix='/api')

@app.get('/')
def root():
    return {'status': 'ok', 'service': 'sunculture-data-science'}
