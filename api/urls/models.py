from urllib.parse import urlparse

from pydantic import BaseModel, model_validator, field_validator


class UrlCreate(BaseModel):
    url: str

    @field_validator("url", mode="after")
    @classmethod
    def validate_url(cls, value) -> "UrlCreate":
        result = urlparse(value)
        is_valid = all([result.scheme, result.netloc])
        if not is_valid:
            raise ValueError("The url is invalid")
        return value


class ShortPath(BaseModel):
    short_path: str

    @model_validator(mode="after")
    def validate_short(self) -> "ShortPath":
        if not len(self.short_path) == 7:
            raise ValueError("The shortened path should be 7 characters")
        if not self.short_path.isalnum():
            raise ValueError(
                "The shortened path should contain only alphanumeric characters"
            )
        return self
