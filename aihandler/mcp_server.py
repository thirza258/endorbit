#!/usr/bin/env python
"""
MCP server providing e-commerce tools for the Endorbit chatbot.
Tools: product_search, filter_by_price, get_product_details.
"""

import os
import sys
import json

# Bootstrap Django so we can use the ORM in this standalone process.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "endorbit.settings")
import django

django.setup()

from mcp.server.fastmcp import FastMCP
from aihandler.models import Product
from aihandler.serializers import ProductSerializer
from aihandler.main import rag_index

mcp = FastMCP("Endorbit Ecommerce")


@mcp.tool()
def product_search(query: str, k: int = 5) -> str:
    """Search for relevant products using semantic (RAG) search.

    Args:
        query: Natural-language search query (e.g. "running shoes under $100")
        k: Number of products to return (default 5)
    """
    results = rag_index.retrieve_documents(query, k=k)
    if not results:
        return json.dumps({"message": "No matching products found."})

    products = []
    for doc in results:
        data = json.loads(doc)
        products.append(
            {
                "product_name": data.get("product_name"),
                "description": data.get("description"),
                "retail_price": data.get("retail_price"),
                "brand": data.get("brand"),
                "product_url": data.get("product_url"),
                "product_rating": data.get("product_rating"),
                "image": data.get("image"),
            }
        )

    return json.dumps(products, default=str)


@mcp.tool()
def filter_by_price(min_price: float = 0, max_price: float = float("inf"), limit: int = 10) -> str:
    """Filter products by price range from the database.

    Args:
        min_price: Minimum retail price (default 0)
        max_price: Maximum retail price (default unlimited)
        limit: Maximum number of results (default 10)
    """
    from django.db.models import Q

    products = Product.objects.filter(
        retail_price__gte=min_price,
        retail_price__lte=max_price,
    ).exclude(retail_price__isnull=True)[:limit]

    if not products:
        return json.dumps({"message": f"No products found between ${min_price:.2f} and ${max_price:.2f}."})

    data = ProductSerializer(products, many=True).data
    return json.dumps(data, default=str)


@mcp.tool()
def get_product_details(product_name: str) -> str:
    """Get full details of a specific product by its exact name.

    Args:
        product_name: Exact product name to look up
    """
    from django.db.models import Q

    try:
        product = Product.objects.filter(product_name__iexact=product_name).first()
        if not product:
            # Fallback: fuzzy match
            product = Product.objects.filter(product_name__icontains=product_name).first()
        if not product:
            return json.dumps({"error": f"Product '{product_name}' not found."})

        data = ProductSerializer(product).data
        return json.dumps(data, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    mcp.run(transport="stdio")
