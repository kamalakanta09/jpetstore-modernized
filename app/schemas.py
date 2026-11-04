from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    catid: str
    name: str | None
    descn: str | None


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    productid: str
    category: str
    name: str | None
    descn: str | None


class ItemOut(BaseModel):
    itemid: str
    productid: str
    product_name: str | None
    listprice: Decimal
    unitcost: Decimal
    status: str | None
    attr1: str | None
    quantity_available: int


class AccountCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=25)
    password: str = Field(..., min_length=4, max_length=80)
    email: EmailStr
    firstname: str
    lastname: str
    addr1: str
    addr2: str | None = None
    city: str
    state: str
    zip: str
    country: str
    phone: str
    langpref: str = "english"
    favcategory: str = "DOGS"
    mylistopt: bool = True
    banneropt: bool = True


class AccountOut(BaseModel):
    username: str
    email: str
    firstname: str
    lastname: str
    addr1: str
    addr2: str | None
    city: str
    state: str
    zip: str
    country: str
    phone: str
    langpref: str
    favcategory: str | None
    mylistopt: bool
    banneropt: bool
    bannername: str | None = None


class OrderItemInput(BaseModel):
    itemid: str
    quantity: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    items: list[OrderItemInput] = Field(..., min_length=1)
    cardtype: str = "Visa"
    creditcard: str = "999 9999 9999 9999"
    exprdate: str = "12/2028"
    shipaddr1: str | None = None
    shipcity: str | None = None
    shipstate: str | None = None
    shipzip: str | None = None
    shipcountry: str | None = None


class LineItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    linenum: int
    itemid: str
    quantity: int
    unitprice: Decimal


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    orderid: int
    userid: str
    orderdate: datetime
    totalprice: Decimal
    cardtype: str
    status: str = "P"
    line_items: list[LineItemOut]