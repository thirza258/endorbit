from django.db import models
from pydantic import BaseModel, Field
from typing import List

# Create your models here.
class Product(models.Model):
    product_url = models.URLField(max_length=200, null=True, blank=True)
    product_name = models.CharField(max_length=200, null=True, blank=True)
    retail_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.URLField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    product_rating = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    brand = models.CharField(max_length=200, null=True, blank=True)
    
    def __str__(self):
        return self.product_name
    
class ProductReturnResponseModel(BaseModel):
    product_url: str = Field(..., description="URL of the product")
    product_name: str = Field(..., description="Name of the product")
    retail_price: float = Field(..., description="Retail price of the product")
    image: str = Field(..., description="URL of the product image")
    description: str = Field(..., description="Description of the product")
    product_rating: float = Field(..., description="Rating of the product")
    brand: str = Field(..., description="Brand of the product")
    
class ResponseModel(BaseModel):
    response : str 
    products : List[ProductReturnResponseModel] 
    