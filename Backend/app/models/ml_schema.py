from pydantic import BaseModel


#forecast input 

class ForecastRequest(BaseModel):

    quantity: int

    profit: float

    returns: int

    order_year: int

    order_month: int

    order_day: int

    profit_margin: float

    shipping_days: int


#anomaly request
class AnomalyRequest(BaseModel):

    profit: float
    profit_margin: float
    quantity: int
    sales: float
    shipping_days: int


#ml response

class MLResponse(BaseModel):

    success: bool

    routes: list[str]

    prediction: float | None = None

    anomaly_status: str | None = None

    answer: str