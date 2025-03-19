from paddle_billing.Entities.Collections import Paginator, ProductCollection
from paddle_billing.Entities.Product import Product

from paddle_billing.ResponseParser import ResponseParser

from paddle_billing.Resources.Products.Operations import CreateProduct, ListProducts

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from paddle_billing.AsyncClient import AsyncClient


class AsyncProductsClient:
    def __init__(self, client: "AsyncClient"):
        self.client = client

    async def list(self, operation: ListProducts = None) -> ProductCollection:
        if operation is None:
            operation = ListProducts()

        response = await self.client.make_request("GET", "/products", params=operation.get_parameters())
        parser = ResponseParser(response)

        return ProductCollection.from_list(
            parser.get_data(), Paginator(self.client, parser.get_pagination(), ProductCollection)
        )

    async def create(self, operation: CreateProduct) -> Product:
        response = await self.client.make_request("POST", "/products", payload=operation)
        parser = ResponseParser(response)

        return Product.from_dict(parser.get_data())
