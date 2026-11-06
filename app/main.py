import os
from pathlib import Path
from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from .platform import tenant
from .service import Rollouts

Latency = Annotated[float, Field(ge=0, le=1000000, allow_inf_nan=False)]

class Evaluation(BaseModel):
    service: str = Field(min_length=1, max_length=100)
    baseline_ms: list[Latency] = Field(min_length=1, max_length=500)
    candidate_ms: list[Latency] = Field(min_length=1, max_length=500)
    max_regression: float = Field(default=0.15, ge=0, le=1, allow_inf_nan=False)
    idempotency_key: str = Field(min_length=1, max_length=128)

def create_app(path=None):
    app = FastAPI(title='Signal Ops', version='1.0.0')
    rollouts = Rollouts(path or os.getenv('DATABASE_PATH', 'signals.db'))

    @app.get('/', response_class=HTMLResponse)
    def console(): return Path(__file__).with_name('console.html').read_text(encoding='utf-8')

    @app.get('/health')
    def health(): return {'status': 'ok'}

    @app.post('/evaluations')
    def evaluate(command: Evaluation, identity: str = Depends(tenant)):
        return rollouts.evaluate(identity, command)

    @app.get('/evaluations')
    def history(identity: str = Depends(tenant)): return rollouts.history(identity)

    return app

app = create_app()
