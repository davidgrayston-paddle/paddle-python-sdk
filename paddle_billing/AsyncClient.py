import httpx
import json

from paddle_billing import Environment
from paddle_billing.Operation import Operation
from paddle_billing.Json.PayloadEncoder import PayloadEncoder

from paddle_billing.ResponseParser import ResponseParser

from paddle_billing.Resources.Products.AsyncProductsClient import AsyncProductsClient


class AsyncClient:
    def __init__(self, api_key: str, version: int = 1, env: Environment = Environment.PRODUCTION):
        default_headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Paddle-Version": str(version),
        }

        self.client = httpx.AsyncClient(base_url=env.base_url, headers=default_headers)
        self.products = AsyncProductsClient(self)

    async def make_request(
        self,
        method: str,
        url: str,
        params: dict | None = None,
        payload: dict | Operation | None = None,
    ):
        try:
            response = await self.client.request(
                method=method,
                url=url,
                params=params,
                content=json.dumps(payload, cls=PayloadEncoder) if payload is not None else None,
            )
            response.raise_for_status()

            return response
        except httpx.HTTPStatusError as e:
            api_error = None
            if e.response is not None:
                response_parser = ResponseParser(e.response)
                api_error = response_parser.get_error()

            if api_error is not None:
                raise api_error

            raise
