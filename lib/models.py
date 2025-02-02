# lib/models.py

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, computed_field, field_validator, validator

# Define Enum for Providers
# class LlmName(Enum):
#     ANTHROPIC = auto()
#     OPENAI = auto()

class LlmName(str, Enum):
    ChatGPT = "ChatGPT"
    Claude = "Claude"
    Gemini = "Gemini"

# Data class for an LLM model.
# @dataclass
# class LlmModel:
#     llm_name: LlmName
#     model_name: str

#     @computed_field
#     @property
#     def id(self) -> str:
#         return f"{self.llm_name.value}_{self.model_name}"
#     class Config:
#         frozen = True  # make Llm instances immutable and hashable
#     def to_dict(self) -> Dict:
#         return {"llm_name": self.llm_name.name, "model_name": self.model_name}

#     @classmethod
#     def from_dict(cls, data: Dict) -> "LlmModel":
#         return cls(llm_name=LlmName[data["llm_name"]], model_name=data["model_name"])
    
class LlmModel(BaseModel):
    llm_name: LlmName
    model_name: str

    @computed_field
    @property
    def id(self) -> str:
        # Use the enum's .name so that keys are consistent.
        return f"{self.llm_name.name}:{self.model_name}"

    class Config:
        frozen = True  # if you really need immutability

    def to_dict(self) -> Dict:
        return {"llm_name": self.llm_name.name, "model_name": self.model_name}

    @classmethod
    def from_dict(cls, data: Dict) -> "LlmModel":
        return cls(llm_name=LlmName[data["llm_name"]], model_name=data["model_name"])
    
# New entity: LlmModelConfig
class LlmModelConfig(BaseModel):
    model: LlmModel
    enabled: bool
    color: str
    initial_char: str  # expecting a single character

    @field_validator("initial_char")
    @classmethod
    def validate_initial_char(cls, value: str) -> str:
        if len(value) != 1:
            raise ValueError("initial_char must be a single character")
        return value

    @computed_field
    @property
    def id(self) -> str:
        # Combines the nested model's id with the initial_char.
        return f"{self.model.id}"

    model_config = ConfigDict(frozen=True)

    def to_dict(self) -> Dict:
        return {
            "model": self.model.to_dict(),
            "enabled": self.enabled,
            "color": self.color,
            "initial_char": self.initial_char
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "LlmModelConfig":
        return cls(
            model=LlmModel.from_dict(data["model"]),
            enabled=data["enabled"],
            color=data["color"],
            initial_char=data["initial_char"]
        )
# New entity: ModelPrice
class ModelPrice(BaseModel):
    input_price: float
    output_price: float
    currency: str = "USD"

# Data class for storing pricing response.
@dataclass
class PriceResponse:
    model: LlmModel
    pricing: ModelPrice
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            "model": self.model.to_dict(),  # Nested representation of LlmModel.
            "pricing": self.pricing.model_dump(),  # Using model_dump() for Pydantic models in v2.
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict, model: LlmModel) -> "PriceResponse":
        pricing = ModelPrice(**data["pricing"])
        return cls(
            model=model,
            pricing=pricing,
            timestamp=data.get("timestamp", datetime.now().isoformat())
        )
    
# New entity: AggregatedPrice
class AggregatedPrice(BaseModel):
    config: LlmModelConfig
    price: Optional[ModelPrice] = None

# New entity: AggregatedPriceResponse
class AggregatedPriceResponse(BaseModel):
    responses: List[AggregatedPrice]