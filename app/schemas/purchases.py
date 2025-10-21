# app/schemas/purchases.py
from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field, AliasChoices
from typing import Optional, List


# ---------- Provider ----------

class ProviderModel(BaseModel):
    Id: int = Field(..., serialization_alias="Id")
    Name: str = Field(..., serialization_alias="Name")
    IdN: Optional[str] = Field(None, serialization_alias="IdN")
    Tel1: Optional[str] = Field(None, serialization_alias="Tel1")
    Tel2: Optional[str] = Field(None, serialization_alias="Tel2")
    Address: Optional[str] = Field(None, serialization_alias="Address")
    Description: Optional[str] = Field(None, serialization_alias="Description")
    WebSite: Optional[str] = Field(None, serialization_alias="WebSite")
    Email: Optional[str] = Field(None, serialization_alias="Email")
    IsActive: bool = Field(..., serialization_alias="IsActive")

    class Config:
        populate_by_name = True
        # For responses, keep PascalCase (serialization_alias above)


class ProviderModelIn(BaseModel):
    # Accept PascalCase or camelCase
    Id: Optional[int] = Field(None, validation_alias=AliasChoices("Id", "id"))
    Name: str = Field(..., validation_alias=AliasChoices("Name", "name"))
    IdN: Optional[str] = Field(None, validation_alias=AliasChoices("IdN", "idN"))
    Tel1: Optional[str] = Field(None, validation_alias=AliasChoices("Tel1", "tel1"))
    Tel2: Optional[str] = Field(None, validation_alias=AliasChoices("Tel2", "tel2"))
    Address: Optional[str] = Field(None, validation_alias=AliasChoices("Address", "address"))
    Description: Optional[str] = Field(None, validation_alias=AliasChoices("Description", "description"))
    WebSite: Optional[str] = Field(None, validation_alias=AliasChoices("WebSite", "webSite"))
    Email: Optional[str] = Field(None, validation_alias=AliasChoices("Email", "email"))
    IsActive: bool = Field(True, validation_alias=AliasChoices("IsActive", "isActive"))

    class Config:
        populate_by_name = True


# ---------- Purchase ----------

class PurchaseModel(BaseModel):
    Id: int = Field(..., serialization_alias="Id")
    ProviderId: int = Field(..., serialization_alias="ProviderId")
    Amount: float = Field(..., serialization_alias="Amount")
    CreateDate: str = Field(..., serialization_alias="CreateDate")  # dd/MM/yyyy (string, per .NET)
    Description: Optional[str] = Field(None, serialization_alias="Description")
    PurchaseLink: Optional[str] = Field(None, serialization_alias="PurchaseLink")
    Image: Optional[str] = Field(None, serialization_alias="Image")

    class Config:
        populate_by_name = True


class PurchaseModelIn(BaseModel):
    # Accept PascalCase or camelCase; CreateDate is string "dd/MM/yyyy"
    Id: Optional[int] = Field(None, validation_alias=AliasChoices("Id", "id"))
    ProviderId: int = Field(..., validation_alias=AliasChoices("ProviderId", "providerId"))
    Amount: float = Field(..., validation_alias=AliasChoices("Amount", "amount"))
    CreateDate: str = Field(..., validation_alias=AliasChoices("CreateDate", "createDate"))
    Description: Optional[str] = Field(None, validation_alias=AliasChoices("Description", "description"))
    PurchaseLink: Optional[str] = Field(None, validation_alias=AliasChoices("PurchaseLink", "purchaseLink"))
    Image: Optional[str] = Field(None, validation_alias=AliasChoices("Image", "image"))

    class Config:
        populate_by_name = True


# ---------- GetPurchaseRequest ----------

class GetPurchaseRequest(BaseModel):
    Id: int = Field(-1, validation_alias=AliasChoices("Id", "id"))
    ProviderId: int = Field(-1, validation_alias=AliasChoices("ProviderId", "providerId"))
    FromDate: Optional[datetime] = Field(None, validation_alias=AliasChoices("FromDate", "fromDate"))
    ToDate: Optional[datetime] = Field(None, validation_alias=AliasChoices("ToDate", "toDate"))

    class Config:
        populate_by_name = True
