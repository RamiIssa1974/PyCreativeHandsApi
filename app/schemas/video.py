# app/schemas/video.py
from typing import Optional
from pydantic import BaseModel, Field, AliasChoices

class VideoModel(BaseModel):
    Id: int = Field(..., serialization_alias="Id")
    VideoName: str = Field(..., serialization_alias="VideoName")
    Extension: str = Field(..., serialization_alias="Extension")
    Title: Optional[str] = Field(None, serialization_alias="Title")
    Description: Optional[str] = Field(None, serialization_alias="Description")

    class Config:
        populate_by_name = True  # keep PascalCase in responses


class VideoModelIn(BaseModel):
    Id: int = Field(-1, validation_alias=AliasChoices("Id", "id"))
    VideoName: str = Field(..., validation_alias=AliasChoices("VideoName", "videoName"))
    Extension: Optional[str] = Field(None, validation_alias=AliasChoices("Extension", "extension"))
    Title: Optional[str] = Field(None, validation_alias=AliasChoices("Title", "title"))
    Description: Optional[str] = Field(None, validation_alias=AliasChoices("Description", "description"))

    class Config:
        populate_by_name = True
