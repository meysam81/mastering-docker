import asyncio

from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from httpx import AsyncClient
from pydantic import BaseModel, BaseSettings
from redis import Redis


class Settings(BaseSettings):
    PORT: int = 8000
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None

    EXCHANGE_RATE_API_URL: str = "https://api.exchangerate.host/latest"

    BASE_CURRENCIES: list[str] = ["USD", "EUR", "GBP"]


settings = Settings()
app = FastAPI()


redis = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
)


class ExchangeRate(BaseModel):
    base_currency: str
    target_currency: str
    exchange_rate: float


class BaseException_(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=self.status_code, detail=detail)


class RateNotFound(BaseException_):
    status_code = 404


@app.on_event("startup")
async def populate_redis():
    async with AsyncClient() as client:
        tasks = []
        for currency in settings.BASE_CURRENCIES:
            tasks.append(
                client.get(f"{settings.EXCHANGE_RATE_API_URL}?base={currency}")
            )

        responses = await asyncio.gather(*tasks)

    pipeline = redis.pipeline()

    for response in responses:
        data = response.json()

        pipeline.hset(
            data["base"],
            mapping=data["rates"],
        )

    pipeline.execute()


@app.get("/{base_currency}/{target_currency}", response_model=ExchangeRate)
async def get_exchange_rate(
    base_currency: str, target_currency: str
) -> dict[str, float]:
    exchange_rate = redis.hget(base_currency, target_currency)

    if exchange_rate is None:
        raise RateNotFound(
            detail=f"Exchange rate for {base_currency} to {target_currency} not found"
        )

    return {
        "base_currency": base_currency,
        "target_currency": target_currency,
        "exchange_rate": exchange_rate,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
