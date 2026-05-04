"""Repository handles only database operations."""

from sqlalchemy.orm import Session

from app.models import URLMapping


class URLRepository:
    def create_url_mapping(self, db: Session, original_url: str, short_code: str):
        url_mapping = URLMapping(original_url=original_url, short_code=short_code)

        db.add(url_mapping)
        db.commit()
        db.refresh(url_mapping)

        return url_mapping

    def get_by_short_code(self, db: Session, short_code: str):
        return db.query(URLMapping).filter(URLMapping.short_code == short_code).first()

    def get_by_original_url(self, db: Session, original_url: str):
        return (
            db.query(URLMapping).filter(URLMapping.original_url == original_url).first()
        )
