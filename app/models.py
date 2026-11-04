from datetime import datetime
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Signon(Base):
    __tablename__ = "signon"
    username: Mapped[str] = mapped_column(String(25), primary_key=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)


class BannerData(Base):
    __tablename__ = "bannerdata"
    favcategory: Mapped[str] = mapped_column(String(80), primary_key=True)
    bannername: Mapped[str | None] = mapped_column(String(255))


class Account(Base):
    __tablename__ = "account"
    userid: Mapped[str] = mapped_column(String(80), primary_key=True)
    email: Mapped[str] = mapped_column(String(80), nullable=False)
    firstname: Mapped[str] = mapped_column(String(80), nullable=False)
    lastname: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str | None] = mapped_column(String(2), default="OK")
    addr1: Mapped[str] = mapped_column(String(80), nullable=False)
    addr2: Mapped[str | None] = mapped_column(String(40))
    city: Mapped[str] = mapped_column(String(80), nullable=False)
    state: Mapped[str] = mapped_column(String(80), nullable=False)
    zip: Mapped[str] = mapped_column(String(20), nullable=False)
    country: Mapped[str] = mapped_column(String(20), nullable=False)
    phone: Mapped[str] = mapped_column(String(80), nullable=False)


class Profile(Base):
    __tablename__ = "profile"
    userid: Mapped[str] = mapped_column(String(80), ForeignKey("account.userid"), primary_key=True)
    langpref: Mapped[str] = mapped_column(String(80), nullable=False, default="english")
    favcategory: Mapped[str | None] = mapped_column(String(30))
    mylistopt: Mapped[bool] = mapped_column(Boolean, default=True)
    banneropt: Mapped[bool] = mapped_column(Boolean, default=True)


class Category(Base):
    __tablename__ = "category"
    catid: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(80))
    descn: Mapped[str | None] = mapped_column(String(255))
    products: Mapped[list["Product"]] = relationship(back_populates="category_rel")


class Product(Base):
    __tablename__ = "product"
    productid: Mapped[str] = mapped_column(String(10), primary_key=True)
    category: Mapped[str] = mapped_column(String(10), ForeignKey("category.catid"), nullable=False)
    name: Mapped[str | None] = mapped_column(String(80))
    descn: Mapped[str | None] = mapped_column(String(255))
    category_rel: Mapped["Category"] = relationship(back_populates="products")
    items: Mapped[list["Item"]] = relationship(back_populates="product")


class Supplier(Base):
    __tablename__ = "supplier"
    suppid: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str | None] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(2), nullable=False)
    addr1: Mapped[str | None] = mapped_column(String(80))
    addr2: Mapped[str | None] = mapped_column(String(80))
    city: Mapped[str | None] = mapped_column(String(80))
    state: Mapped[str | None] = mapped_column(String(80))
    zip: Mapped[str | None] = mapped_column(String(5))
    phone: Mapped[str | None] = mapped_column(String(80))


class Item(Base):
    __tablename__ = "item"
    itemid: Mapped[str] = mapped_column(String(10), primary_key=True)
    productid: Mapped[str] = mapped_column(String(10), ForeignKey("product.productid"), nullable=False)
    listprice: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    unitcost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    supplier: Mapped[int | None] = mapped_column(Integer, ForeignKey("supplier.suppid"))
    status: Mapped[str | None] = mapped_column(String(2))
    attr1: Mapped[str | None] = mapped_column(String(80))
    attr2: Mapped[str | None] = mapped_column(String(80))
    attr3: Mapped[str | None] = mapped_column(String(80))
    attr4: Mapped[str | None] = mapped_column(String(80))
    attr5: Mapped[str | None] = mapped_column(String(80))
    product: Mapped["Product"] = relationship(back_populates="items")
    inventory: Mapped["Inventory"] = relationship(back_populates="item", uselist=False)


class Inventory(Base):
    __tablename__ = "inventory"
    itemid: Mapped[str] = mapped_column(String(10), ForeignKey("item.itemid"), primary_key=True)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    item: Mapped["Item"] = relationship(back_populates="inventory")


class Order(Base):
    __tablename__ = "orders"
    orderid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    userid: Mapped[str] = mapped_column(String(80), ForeignKey("account.userid"), nullable=False)
    orderdate: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    shipaddr1: Mapped[str] = mapped_column(String(80), nullable=False)
    shipaddr2: Mapped[str | None] = mapped_column(String(80))
    shipcity: Mapped[str] = mapped_column(String(80), nullable=False)
    shipstate: Mapped[str] = mapped_column(String(80), nullable=False)
    shipzip: Mapped[str] = mapped_column(String(20), nullable=False)
    shipcountry: Mapped[str] = mapped_column(String(20), nullable=False)
    billaddr1: Mapped[str] = mapped_column(String(80), nullable=False)
    billaddr2: Mapped[str | None] = mapped_column(String(80))
    billcity: Mapped[str] = mapped_column(String(80), nullable=False)
    billstate: Mapped[str] = mapped_column(String(80), nullable=False)
    billzip: Mapped[str] = mapped_column(String(20), nullable=False)
    billcountry: Mapped[str] = mapped_column(String(20), nullable=False)
    courier: Mapped[str] = mapped_column(String(80), default="UPS", nullable=False)
    totalprice: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    billtofirstname: Mapped[str] = mapped_column(String(80), nullable=False)
    billtolastname: Mapped[str] = mapped_column(String(80), nullable=False)
    shiptofirstname: Mapped[str] = mapped_column(String(80), nullable=False)
    shiptolastname: Mapped[str] = mapped_column(String(80), nullable=False)
    creditcard: Mapped[str] = mapped_column(String(80), nullable=False)
    exprdate: Mapped[str] = mapped_column(String(7), nullable=False)
    cardtype: Mapped[str] = mapped_column(String(80), nullable=False)
    locale: Mapped[str] = mapped_column(String(80), default="CA", nullable=False)
    line_items: Mapped[list["LineItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class OrderStatus(Base):
    __tablename__ = "orderstatus"
    orderid: Mapped[int] = mapped_column(Integer, ForeignKey("orders.orderid"), primary_key=True)
    linenum: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    status: Mapped[str] = mapped_column(String(2), default="P", nullable=False)


class LineItem(Base):
    __tablename__ = "lineitem"
    orderid: Mapped[int] = mapped_column(Integer, ForeignKey("orders.orderid"), primary_key=True)
    linenum: Mapped[int] = mapped_column(Integer, primary_key=True)
    itemid: Mapped[str] = mapped_column(String(10), ForeignKey("item.itemid"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unitprice: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    order: Mapped["Order"] = relationship(back_populates="line_items")


class Sequence(Base):
    __tablename__ = "sequence"
    name: Mapped[str] = mapped_column(String(30), primary_key=True)
    nextid: Mapped[int] = mapped_column(Integer, nullable=False)
    