from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CaseReview:
    id_siniestro: str
    estado_actual: str = 'pendiente_revision'
    decision_humana: str = ''
    comentario: str = ''
    revisado_por: str = 'sistema'


@dataclass
class StatusEvent:
    id_siniestro: str
    estado: str
    comentario: str = ''
    actor: str = 'sistema'
