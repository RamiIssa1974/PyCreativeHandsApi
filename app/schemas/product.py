from pydantic import BaseModel, ConfigDict
from typing import List, Optional


#DTOs (PascalCase to match old API)

class GetProductRequest(BaseModel):
    Id: int
    Name: str
    Description: Optional[str] = None
    Barcode: Optional[str] = None
    CategoryId: Optional[int] = None
    SubCategoryId: Optional[int] = None
    Skip: int = 0
    Limit: int = 50

class ProductVariationModel(BaseModel):
    Id: int
    ProductId: int
    Price: float
    Description: Optional[str] = None

class ProductVariationIn(BaseModel):
    Id: Optional[int] = None
    Price: float
    Description: Optional[str] = None

class SaveProductRequest(BaseModel):
    Id: Optional[int] = None
    Name: str
    Description: Optional[str] = None
    Barcode: Optional[str] = None
    Price: Optional[float] = None
    SalePrice: Optional[float] = None

    Images: List[str] = []               # ← same idea: not required, defaults to []
    UploadedImages: List[str] = []
    Categories: List[int] = []
    ProductVariations: List[ProductVariationIn] = []
    AvailableColours: List[str] = []

    StockQuantity: Optional[int] = 0     # optional, default 0

    model_config = ConfigDict(extra="ignore")
 
class ProductCategoryModel(BaseModel):
    Id: int
    ProductId: int
    CategoryId: int
 
class CategoryModel(BaseModel):
    Id: int
    Name: str

class ProductAvailableColoursModel(BaseModel):
    Id: int
    ProductId: int
    Code: str


class ProductImageModel(BaseModel):
    Id: int
    ProductId: int
    Extension: str

class ProductModel(BaseModel):
    Id: int
    Name: str
    Price: float
    SalePrice: Optional[float] = None
    Barcode: Optional[str] = None
    Description: Optional[str] = None
    Images: Optional[List[ProductImageModel]] = None
    Categories: Optional[List[CategoryModel]] = None
    ProductVariations: Optional[List[ProductVariationModel]] = None
    AvailableColours: Optional[List[ProductAvailableColoursModel]] = None
    StockQuantity: int

    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    Name: str
    Description: Optional[str] = None
    Price: Optional[float] = None
    SalePrice: Optional[float] = None
    Barcode: Optional[str] = None
    StockQuantity: Optional[int] = None

class ProductOut(BaseModel):
    Id: int
    Name: str
    Description: Optional[str] = None
    Price: Optional[float] = None
    SalePrice: Optional[float] = None
    Barcode: Optional[str] = None
    StockQuantity: Optional[int] = None
    class Config:
        from_attributes = True
