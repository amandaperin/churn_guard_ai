from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.api.routes.health import router as health_router
from src.api.routes.customers import router as customers_router
from src.api.routes.chat import router as chat_router


app = FastAPI(
    title="ChurnGuard AI API",
    description="API for customer churn risk analysis and segmentation.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="src/api/static"), name="static")
templates = Jinja2Templates(directory="src/api/templates")

app.include_router(health_router)
app.include_router(customers_router)
app.include_router(chat_router)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )