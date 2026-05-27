from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class DocumentFieldSet:
    fecha_emision: str | None = None
    fecha_evento: str | None = None
    monto: float | None = None
    proveedor: str | None = None
    placa: str | None = None
    tipo_documento: str | None = None


@dataclass
class DocumentInconsistency:
    codigo: str
    descripcion: str
    severidad: str
    field_name: str = ''


@dataclass
class DocumentAnalysisResult:
    id_documento: str
    id_siniestro: str
    tipo_detectado: str
    legibilidad_score: float
    presente: bool
    campos_extraidos: DocumentFieldSet
    inconsistencias: list[DocumentInconsistency] = field(default_factory=list)
    document_score: float = 0.0
    recomendacion: str = ''
    fuente: str = 'document_ai'
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            'id_documento': self.id_documento,
            'id_siniestro': self.id_siniestro,
            'tipo_detectado': self.tipo_detectado,
            'legibilidad_score': round(self.legibilidad_score, 3),
            'presente': int(self.presente),
            'campos_extraidos': asdict(self.campos_extraidos),
            'inconsistencias': [asdict(item) for item in self.inconsistencias],
            'document_score': round(self.document_score, 2),
            'recomendacion': self.recomendacion,
            'fuente': self.fuente,
            'metadata': self.metadata,
        }


@dataclass
class ClaimDocumentAssessment:
    id_siniestro: str
    document_score: float
    documentos_analizados: int
    documentos_con_alerta: int
    inconsistencias: list[DocumentInconsistency] = field(default_factory=list)
    resultados: list[DocumentAnalysisResult] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            'id_siniestro': self.id_siniestro,
            'document_score': round(self.document_score, 2),
            'documentos_analizados': self.documentos_analizados,
            'documentos_con_alerta': self.documentos_con_alerta,
            'inconsistencias': [asdict(item) for item in self.inconsistencias],
            'resultados': [item.as_dict() for item in self.resultados],
        }
