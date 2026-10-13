"""Templates Jinja2 e gerador de URLs usados pela interface HTML."""

from pathlib import Path

from starlette.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _template_url_for(endpoint, **values):
    fixed_routes = {
        "auth.login": "/login",
        "auth.cadastro": "/cadastro",
        "auth.logout": "/logout",
        "empresa.home": "/empresa/home",
    }
    if endpoint == "static":
        return f"/static/{values['filename']}"
    if endpoint in {"empresa.subscribe", "empresa.config", "config", "add_pizza"}:
        paths = {
            "empresa.subscribe": "/empresa/subscribe",
            "empresa.config": "/empresa/config",
            "config": "/config",
            "add_pizza": "/add",
        }
        return f"{paths[endpoint]}/{values['empresa_id']}"
    try:
        return fixed_routes[endpoint]
    except KeyError as exc:
        raise ValueError(f"URL de template não configurada: {endpoint}") from exc


templates.env.globals["url_for"] = _template_url_for
