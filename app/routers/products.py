from fastapi import APIRouter, HTTPException
from typing import List
from app.repositories.products_repository import ProductsRepository
from app.schemas.product import (
    GetProductRequest, ProductImageModel,  SaveProductRequest,
    ProductModel, ProductCategoryModel, CategoryModel,
    ProductVariationModel, ProductAvailableColoursModel
)

router = APIRouter(tags=["Products"])  # no global prefix to keep legacy paths identical
repo = ProductsRepository()

# POST api/products/GetProducts
@router.post("/api/products/GetProducts", response_model=List[ProductModel])
def get_products(request: GetProductRequest):
    items = repo.get_products(request)
    if not items:
        raise HTTPException(status_code=404, detail="No products found.")
    return items

# GET api/products/ProductCategories
@router.get("/api/products/ProductCategories", response_model=List[ProductCategoryModel])
def get_product_categories():
    items = repo.get_product_categories()
    if not items:
        raise HTTPException(status_code=404, detail="No product categories found.")
    return items

# POST api/products/Product  (SaveProduct)
@router.post("/api/products/Product", response_model=int)
def save_product(request: SaveProductRequest):
    product_id = repo.save_product(request)
    if product_id <= 0:
        raise HTTPException(status_code=500, detail="An error occurred while saving the product.")
    return product_id

# GET api/products/Categories
@router.get("/api/products/Categories", response_model=List[CategoryModel])
def get_categories():
    items = repo.get_categories()
    if not items:
        raise HTTPException(status_code=404, detail="No categories found.")
    return items

# GET api/products/Images
@router.get("/api/products/Images", response_model=List[ProductImageModel])
def get_images():
    items = repo.get_images()
    if not items:
        raise HTTPException(status_code=404, detail="No images found.")
    return items

# GET api/products/ProductVariations
@router.get("/api/products/ProductVariations", response_model=List[ProductVariationModel])
def get_product_variations():
    items = repo.get_product_variations()
    if not items:
        raise HTTPException(status_code=404, detail="No product variations found.")
    return items

# GET api/products/AvailableColours
@router.get("/api/products/AvailableColours", response_model=List[ProductAvailableColoursModel])
def get_available_colours():
    items = repo.get_available_colours()
    if not items:
        raise HTTPException(status_code=404, detail="No colours available.")
    return items

# DELETE api/products/DeleteProduct/{ProductId}
@router.delete("/api/products/DeleteProduct/{ProductId}")
def delete_product(ProductId: int):
    res = repo.delete_product(ProductId)
    if res is True:
        return {"message": f"Product with ID {ProductId} deleted."}
    if res == "referenced":
        raise HTTPException(
            status_code=409,
            detail=f"Product {ProductId} cannot be deleted because it is referenced by order items."
        )
    raise HTTPException(status_code=404, detail=f"Product with ID {ProductId} not found.")
     