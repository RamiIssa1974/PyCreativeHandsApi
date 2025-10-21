# app/schemas/upload.py
from typing import List, Optional
from pydantic import BaseModel, Field, AliasChoices

class UploadFilesResponse(BaseModel):
    VideoId: int = Field(0, serialization_alias="VideoId",
                         validation_alias=AliasChoices("VideoId","videoId"))
    ProductId: int = Field(0, serialization_alias="ProductId",
                           validation_alias=AliasChoices("ProductId","productId"))
    PurchaseId: int = Field(0, serialization_alias="PurchaseId",
                            validation_alias=AliasChoices("PurchaseId","purchaseId"))
    UploadedImages: Optional[List[str]] = Field(default=None,
                           serialization_alias="UploadedImages",
                           validation_alias=AliasChoices("UploadedImages","uploadedImages"))

    class Config:
        populate_by_name = True  # keep PascalCase in responses
