"""Contratos HTTP e validações da API AquaSafe."""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DrenagemInput(BaseModel):
    tipo: str = Field(min_length=1, max_length=50)
    quantidade: int = Field(default=1, gt=0)
    capacidade_individual_l_s: float | None = Field(default=None, ge=0)
    capacidade_total_l_s: float | None = Field(default=None, ge=0)
    observacao: str | None = None


class TrechoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    codigo: str = Field(min_length=1, max_length=40)
    rodovia_id: int = Field(gt=0)
    km_inicial: float = Field(ge=0)
    km_final: float = Field(gt=0)
    comprimento_m: float | None = Field(default=None, gt=0)
    largura_m: float | None = Field(default=None, gt=0)
    area_contribuicao_m2: float | None = Field(default=None, gt=0)
    coeficiente_escoamento: float | None = Field(default=None, ge=0, le=1)
    inclinacao_percentual: float | None = Field(default=None, ge=-100, le=100)
    estado_inclinacao: str | None = None
    pavimentacao: str | None = Field(default=None, max_length=50)
    estado_pavimento: str | None = Field(default=None, max_length=30)
    mtd_mm: float | None = Field(default=None, gt=0)
    caminho_escoamento_m: float | None = Field(default=None, gt=0)
    declividade_caminho_percentual: float | None = Field(default=None, gt=0, le=100)
    drenagem: DrenagemInput | None = None
    geometria: dict | None = None
    geometria_validada: bool = False
    origem_dados: str = "manual"
    origem_geometria: str | None = None

    @model_validator(mode="after")
    def validar_intervalo_e_geometria(self):
        if self.km_final <= self.km_inicial:
            raise ValueError("km_final deve ser maior que km_inicial")
        if self.geometria is not None:
            if self.geometria.get("type") != "LineString" or not isinstance(self.geometria.get("coordinates"), list) or len(self.geometria["coordinates"]) < 2:
                raise ValueError("geometria deve ser um GeoJSON LineString com ao menos dois pontos")
            for point in self.geometria["coordinates"]:
                if not isinstance(point, list) or len(point) < 2 or not -180 <= point[0] <= 180 or not -90 <= point[1] <= 90:
                    raise ValueError("coordenadas GeoJSON devem seguir [longitude, latitude]")
        return self


class TrechoUpdateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    codigo: str | None = Field(default=None, min_length=1, max_length=40)
    rodovia_id: int | None = Field(default=None, gt=0)
    km_inicial: float | None = Field(default=None, ge=0)
    km_final: float | None = Field(default=None, gt=0)
    comprimento_m: float | None = Field(default=None, gt=0)
    largura_m: float | None = Field(default=None, gt=0)
    area_contribuicao_m2: float | None = Field(default=None, gt=0)
    coeficiente_escoamento: float | None = Field(default=None, ge=0, le=1)
    inclinacao_percentual: float | None = Field(default=None, ge=-100, le=100)
    estado_inclinacao: str | None = None
    pavimentacao: str | None = None
    estado_pavimento: str | None = None
    mtd_mm: float | None = Field(default=None, gt=0)
    caminho_escoamento_m: float | None = Field(default=None, gt=0)
    declividade_caminho_percentual: float | None = Field(default=None, gt=0, le=100)
    drenagem: DrenagemInput | None = None
    geometria: dict | None = None
    geometria_validada: bool | None = None
    origem_dados: str | None = None
    origem_geometria: str | None = None


class MedicaoMeteorologicaInput(BaseModel):
    trecho_id: int = Field(gt=0)
    fonte: str = Field(min_length=1, max_length=100)
    precipitacao_mm: float | None = Field(default=None, ge=0)
    intensidade_mm_h: float | None = Field(default=None, ge=0)
    data_hora: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    estacao_id: int | None = Field(default=None, gt=0)
    identificador_externo: str | None = Field(default=None, max_length=150)

    @model_validator(mode="after")
    def exigir_medida(self):
        if self.precipitacao_mm is None and self.intensidade_mm_h is None:
            raise ValueError("Informe precipitação acumulada e/ou intensidade de chuva")
        return self


class EstacaoMeteorologicaInput(BaseModel):
    codigo_externo: str = Field(min_length=1, max_length=100)
    fonte: str = Field(min_length=1, max_length=100)
    nome: str = Field(min_length=1, max_length=150)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    origem_dados: Literal["real", "mock"] | None = None
    observacoes: str | None = None

    @model_validator(mode="after")
    def validar_par_de_coordenadas(self):
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("Informe latitude e longitude juntas, ou deixe ambas ausentes")
        return self


class AssociacaoEstacaoInput(BaseModel):
    status_associacao: Literal["validada", "candidata", "pendente_validacao", "inativa"] = "pendente_validacao"
    distancia_km: float | None = Field(default=None, ge=0)
    justificativa: str | None = None


class AnaliseRiscoInput(BaseModel):
    trecho_id: int = Field(gt=0)
    intensidade_mm_h: float | None = Field(default=None, ge=0)
    precipitacao_mm: float | None = Field(default=None, ge=0)
    estado_pavimento: str | None = None
    data_hora: datetime | None = None


class LocalizacaoInput(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    sentido: Literal["crescente", "decrescente"] | None = None


class SimulacaoInput(BaseModel):
    cenario_id: int = Field(gt=0)
    trecho_id: int = Field(default=1, gt=0)
