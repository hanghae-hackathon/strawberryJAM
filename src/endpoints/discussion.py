from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.utils import get_templates


router = APIRouter(prefix="/discussions", tags=["discussion"])


@router.get("/{discussion_id}", response_class=HTMLResponse)
async def read_discussion(
    request: Request,
    discussion_id: int,
    templates: Jinja2Templates = Depends(get_templates),
):
    return templates.TemplateResponse(
        request=request,
        name="discussions/index.html",
        context={"discussion_id": discussion_id},
    )
