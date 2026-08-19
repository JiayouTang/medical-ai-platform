from dataclasses import dataclass

from medical_ai.config import Settings, get_settings


@dataclass(frozen=True)
class LLMConfig:
    base_url: str
    api_key: str
    model: str

    @property
    def configured(self) -> bool:
        return bool(self.base_url and self.api_key and self.model)


def get_llm_config(settings: Settings | None = None) -> LLMConfig:
    settings = settings or get_settings()
    return LLMConfig(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
    )
