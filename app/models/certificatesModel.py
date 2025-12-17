from __future__ import annotations
from datetime import datetime
from sqlalchemy import ForeignKey
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import db

class Certificate(db.Model):
    __tablename__ = "certificates"

    id: Mapped[int] = mapped_column(primary_key=True)
    common_name: Mapped[str] = mapped_column(nullable=False)
    valid_from: Mapped[datetime] = mapped_column(nullable=False)
    valid_to: Mapped[datetime] = mapped_column(nullable=False)
    company: Mapped[Optional[str]] = mapped_column(nullable=True)

    # Chave Estrangeira
    ca_id: Mapped[int] = mapped_column(ForeignKey("cacertificates.id"), nullable=False)

    # Relacionamentos
    issuer = relationship("CACertificate", back_populates="certificates")
    sans = relationship("CertificateSANs", back_populates="certificate", cascade="all, delete-orphan")


    # ------------ Serialização ------------
    def format_certificate(self):
        # Converte list SANs para string
        sans_list = [san.san for san in self.sans]
        sans_str = '<br>'.join(sans_list)
        return {
            "id": self.id,
            "issuer": self.issuer.common_name if self.issuer else None,
            "common_name": self.common_name,
            "valid_from": self.valid_from,
            "valid_to": self.valid_to,
            "company": self.company,
            "sans": sans_str
        }