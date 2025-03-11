import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Assistant(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, unique=False, nullable=True)
    system_instructions = Column(String, unique=False, nullable=False)
    first_message = Column(String, unique=False, nullable=True)
    voice = Column(String, unique=False, nullable=True)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )

    user = relationship("User", back_populates="assistants")

    def __repr__(self):
        return f"<Assistant(name={self.name})>"
