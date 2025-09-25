from urllib.parse import urlparse

from pydantic import BaseModel, model_validator, field_validator

BLACKLIST = ["localhost:5000", "0.0.0.0:5000", "127.0.0.1:5000"]


class UrlCreate(BaseModel):
    url: str

    @field_validator("url", mode="after")
    @classmethod
    def validate_url(cls, value) -> "UrlCreate":
        result = urlparse(value)
        is_valid = all([result.scheme, result.netloc])
        if not is_valid:
            raise ValueError("The url is invalid")
        if result.netloc in BLACKLIST:
            raise ValueError("The url is blacklisted")
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
