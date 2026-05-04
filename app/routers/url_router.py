
"""Routes""" 

from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import URLShortenerService

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")
url_service = URLShortenerService()


@router.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "short_url": None
        }
    )


@router.post("/shorten")
def shorten_url(
    request: Request,
    original_url: str = Form(...),
    db: Session = Depends(get_db)
):
    url_mapping = url_service.create_short_url(
        db=db,
        original_url=original_url
    )

    base_url = str(request.base_url)
    short_url = f"{base_url}{url_mapping.short_code}"

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "short_url": short_url,
            "original_url": original_url
        }
    )


@router.get("/{short_code}")
def redirect_to_original_url(
    short_code: str,
    db: Session = Depends(get_db)
):
    url_mapping = url_service.get_original_url(
        db=db,
        short_code=short_code
    )

    if not url_mapping:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return RedirectResponse(url=url_mapping.original_url)
