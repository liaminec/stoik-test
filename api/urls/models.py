from urllib.parse import urlparse

from pydantic import BaseModel, field_validator


class UrlCreate(BaseModel):
    url: str

    @field_validator("url", mode="after")
    def validate_url(self, value: str) -> str:
        result = urlparse(value)
        is_valid = all([result.scheme, result.netloc])
        if not is_valid:
            raise ValueError("The url is not valid")
        return value


class ShortPath(BaseModel):
    short_path: str

    @field_validator("short", mode="after")
    def validate_short(self, value: str) -> str:
        if not len(value) == 7:
            raise ValueError("The shortened path should be 7 characters")
        if not value.isalnum():
            raise ValueError(
                "The shortened path should contain only alphanumeric characters"
            )
        return value
