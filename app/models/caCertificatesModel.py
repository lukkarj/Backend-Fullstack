from __future__ import annotations
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import db

class CACertificate(db.Model):
    __tablename__ = "cacertificates"

    id: Mapped[int] = mapped_column(primary_key=True)
    common_name: Mapped[str] = mapped_column(nullable=False)
    valid_from: Mapped[datetime] = mapped_column(nullable=False)
    valid_to: Mapped[datetime] = mapped_column(nullable=False)
    company: Mapped[str] = mapped_column(nullable=False)
    state: Mapped[str] = mapped_column(nullable=False)
    locality: Mapped[str] = mapped_column(nullable=False)
    country: Mapped[str] = mapped_column(nullable=False)
    key: Mapped[str] = mapped_column(nullable=False)
    crt: Mapped[str] = mapped_column(nullable=False)

    # Relacionamentos
    certificates = relationship("Certificate", back_populates="issuer")

    # ------------ Serialização ------------
    def format_CACertificate(self):
        return {
            "id": self.id,
            "common_name": self.common_name,
            "valid_from": self.valid_from,
            "valid_to": self.valid_to,
            "company": self.company,
            "state": self.state,
            "locality": self.locality,
            "country": self.country,
            "key": self.key,
            "crt": self.crt
        }
