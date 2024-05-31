from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")


async def get_templates() -> Jinja2Templates:
    return templates
