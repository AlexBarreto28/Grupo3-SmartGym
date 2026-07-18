from sqlalchemy import Column, Integer, ForeignKey, Date, Numeric, String, CheckConstraint
from sqlalchemy.sql import func  
from sqlalchemy.orm import relationship
from app.db.base import Base

class EvaluacionBiometrica(Base):
    __tablename__ = "evaluaciones_biometricas"
    __table_args__ = (
        CheckConstraint("peso > 0", name="check_peso"),
        CheckConstraint("estatura > 0", name="check_estatura"),
        CheckConstraint(
            "porcentaje_grasa >= 0 AND porcentaje_grasa <= 100",
            name="check_porcentaje_grasa",
        ),
    )

    id = Column(Integer, primary_key=True)
    fecha = Column(Date, nullable=False, server_default=func.now())
    peso = Column(Numeric(5, 2), nullable=False)
    estatura = Column(Numeric(5, 2), nullable=False)
    porcentaje_grasa = Column(Numeric(5, 2), nullable=False)
    observaciones = Column(String(255), nullable=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    estado = Column(String(20), default="activo", nullable=False)

    cliente = relationship("Cliente", back_populates="evaluaciones")
