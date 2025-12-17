from __future__ import annotations
from sqlalchemy import ForeignKey

from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import db

class CertificateSANs(db.Model):
    __tablename__ = "sans"

    id: Mapped[int] = mapped_column(primary_key=True)
    san: Mapped[str] = mapped_column(nullable=False)

    # Chave Estrangeira
    certificate_id: Mapped[int] = mapped_column(ForeignKey("certificates.id"), nullable=False)

    # Relacionamentos
    certificate = relationship("Certificate", back_populates="sans")


    # ------------ Serialização ------------
    def format_sans(self):
        return {
            "id": self.id,
            "san": self.san
        }