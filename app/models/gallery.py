from sqlalchemy import Column, String

from app.models.base import Base, default_timestamp, default_uuid


class Gallery(Base):
    __tablename__ = "gallery"

    id = default_uuid()

    # Details
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    service_category = Column(String, nullable=False)
    before_image_url = Column(String, nullable=True)
    after_image_url = Column(String, nullable=False)

    # Timestamps
    created_at = default_timestamp()

    def __repr__(self):
        return f"<Gallery(title='{self.title}')>"
