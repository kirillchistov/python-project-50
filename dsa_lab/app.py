from pathlib import Path
from typing import Optional

from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from dsa_lab.content import get_lesson
from dsa_lab.site import template_context
from dsa_lab.tracers import run_trace


ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / 'web'

app = FastAPI(
    title='DSA Lab',
    description='Учебный кабинет алгоритмов рядом с gendiff',
)
app.mount('/static', StaticFiles(directory=WEB / 'static'), name='static')
templates = Jinja2Templates(directory=str(WEB / 'templates'))


@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        'index.html',
        template_context(request=request),
    )


@app.get('/lessons/{slug}', response_class=HTMLResponse)
def lesson_page(request: Request, slug: str):
    lesson = get_lesson(slug)
    if lesson is None:
        raise HTTPException(status_code=404, detail='Урок не найден')
    return templates.TemplateResponse(
        'lesson.html',
        template_context(request=request, lesson=lesson),
    )


@app.post('/api/trace/{algorithm}')
def api_trace(algorithm: str, payload: Optional[dict] = Body(default=None)):
    try:
        return run_trace(algorithm, payload or {})
    except KeyError as error:
        raise HTTPException(
            status_code=404,
            detail='Неизвестный алгоритм: {0}'.format(error),
        )
    except (TypeError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post('/api/gendiff/trace')
def api_gendiff(payload: Optional[dict] = Body(default=None)):
    return api_trace('gendiff_build', payload or {})
