import pytest
from json import loads, dumps
from os import getenv
from pytest import raises

from paddle_billing.Exceptions.ApiError import ApiError
from paddle_billing.Entities.Shared import TaxCategory, CustomData
from paddle_billing.Resources.Shared.Operations import Pager

from paddle_billing import Environment

from paddle_billing.Resources.Products.Operations import CreateProduct, ListProducts
from paddle_billing.AsyncClient import AsyncClient

from tests.Utils.ReadsFixture import ReadsFixtures


class TestAsyncProductsClient:
    @pytest.mark.asyncio
    async def test_create_product(
        self,
        httpx_mock,
    ):
        base_url = Environment.SANDBOX.base_url
        expected_request_body = ReadsFixtures.read_raw_json_fixture("request/create_full")
        expected_response_body = ReadsFixtures.read_raw_json_fixture("response/minimal_entity")
        expected_url = f"{base_url}/products"
        httpx_mock.add_response(method="POST", url=expected_url, status_code=201, text=expected_response_body)

        client = AsyncClient(
            api_key=getenv("PADDLE_API_SECRET_KEY"),
            version=1,
            env=Environment.SANDBOX,
        )

        product = await client.products.create(
            CreateProduct(
                name="ChatApp Full",
                tax_category=TaxCategory.Standard,
                description="Spend more time engaging with students with ChataApp Education.",
                image_url="https://paddle-sandbox.s3.amazonaws.com/user/10889/2nmP8MQSret0aWeDemRw_icon1.png",
                custom_data=CustomData(
                    {
                        "features": {
                            "reports": True,
                            "crm": False,
                            "data_retention": True,
                        },
                    }
                ),
            ),
        )

        assert product.id == "pro_01h7zcgmdc6tmwtjehp3sh7azf"

        last_request = httpx_mock.get_requests()[-1]
        assert (
            last_request.url == expected_url
        ), "The URL does not match the expected URL, verify the query string is correct"
        assert loads(last_request.content) == loads(
            expected_request_body
        ), "The request JSON doesn't match the expected fixture JSON"

    @pytest.mark.asyncio
    async def test_create_product_bad_request(
        self,
        httpx_mock,
    ):
        base_url = Environment.SANDBOX.base_url
        expected_response_body = dumps(
            {
                "error": {
                    "type": "request_error",
                    "code": "bad_request",
                    "detail": "Invalid request",
                    "documentation_url": "https://developer.paddle.com/v1/errors/shared/bad_request",
                    "errors": [{"field": "some_field", "message": "Some error message"}],
                },
                "meta": {"request_id": "f00bb3ca-399d-4686-889c-50b028f4c912"},
            }
        )
        expected_url = f"{base_url}/products"
        httpx_mock.add_response(method="POST", url=expected_url, status_code=400, text=expected_response_body)

        client = AsyncClient(
            api_key=getenv("PADDLE_API_SECRET_KEY"),
            version=1,
            env=Environment.SANDBOX,
        )

        with raises(ApiError) as exception_info:
            await client.products.create(
                CreateProduct(
                    name="ChatApp Full",
                    tax_category=TaxCategory.Standard,
                ),
            )

        api_error = exception_info.value

        assert api_error.detail == "Invalid request"
        assert api_error.error_type == "request_error"
        assert api_error.error_code == "bad_request"
        assert api_error.docs_url == "https://developer.paddle.com/v1/errors/shared/bad_request"
        assert api_error.field_errors[0].field == "some_field"
        assert api_error.field_errors[0].error == "Some error message"

    @pytest.mark.asyncio
    async def test_list_products(
        self,
        httpx_mock,
    ):
        base_url = Environment.SANDBOX.base_url
        expected_response_body = ReadsFixtures.read_raw_json_fixture("response/list_default")
        expected_url = f"{base_url}/products?order_by=id[asc]&per_page=50"

        httpx_mock.add_response(method="GET", url=expected_url, status_code=200, text=expected_response_body)

        client = AsyncClient(
            api_key=getenv("PADDLE_API_SECRET_KEY"),
            version=1,
            env=Environment.SANDBOX,
        )

        products = await client.products.list(ListProducts(Pager()))

        product = products.items[0]

        assert product.id == "pro_01h1vjes1y163xfj1rh1tkfb65"
