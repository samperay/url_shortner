"""Service layer contains business logic.

Generate short code
Check duplicate URL
Check duplicate short code
Return existing short URL if already created

"""

import random
import string
from sqlalchemy.orm import Session

from app.repositories import URLRepository


class URLShortenerService:

    def __init__(self):
        self.repository = URLRepository()

    def generate_short_code(self, length: int = 6) -> str:
        characters = string.ascii_letters + string.digits
        return "".join(random.choice(characters) for _ in range(length))

    def create_short_url(self, db: Session, original_url: str):
        existing_url = self.repository.get_by_original_url(
            db=db,
            original_url=original_url
        )

        if existing_url:
            return existing_url

        while True:
            short_code = self.generate_short_code()

            existing_code = self.repository.get_by_short_code(
                db=db,
                short_code=short_code
            )

            if not existing_code:
                break

        return self.repository.create_url_mapping(
            db=db,
            original_url=original_url,
            short_code=short_code
        )

    def get_original_url(self, db: Session, short_code: str):
        return self.repository.get_by_short_code(
            db=db,
            short_code=short_code
        )