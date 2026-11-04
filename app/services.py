from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session
from app.models import (
    Account, BannerData, Category, Inventory, Item,
    LineItem, Order, OrderStatus, Product, Profile, Sequence, Signon
)
from app.schemas import AccountCreate, AccountOut, ItemOut, OrderCreate, OrderOut
from app.security import hash_password, verify_password


class CatalogService:
    @staticmethod
    def list_categories(db: Session) -> list[Category]:
        return list(db.scalars(select(Category).order_by(Category.catid)).all())

    @staticmethod
    def list_products_by_category(db: Session, catid: str) -> list[Product]:
        return list(db.scalars(select(Product).where(Product.category == catid.upper())).all())

    @staticmethod
    def search_products(db: Session, query: str) -> list[Product]:
        keywords = [kw.strip().lower() for kw in query.split() if kw.strip()]
        if not keywords:
            return []
        conditions = [func.lower(Product.name).like(f"%{kw}%") for kw in keywords]
        return list(db.scalars(select(Product).where(or_(*conditions))).all())

    @staticmethod
    def list_items_by_product(db: Session, productid: str) -> list[ItemOut]:
        items = db.scalars(select(Item).where(Item.productid == productid.upper())).all()
        return [CatalogService._to_item_out(i) for i in items]

    @staticmethod
    def get_item(db: Session, itemid: str) -> ItemOut:
        item = db.get(Item, itemid.upper())
        if not item:
            raise HTTPException(status_code=404, detail=f"Item {itemid} not found")
        return CatalogService._to_item_out(item)

    @staticmethod
    def _to_item_out(item: Item) -> ItemOut:
        return ItemOut(
            itemid=item.itemid,
            productid=item.productid,
            product_name=item.product.name if item.product else None,
            listprice=item.listprice,
            unitcost=item.unitcost,
            status=item.status,
            attr1=item.attr1,
            quantity_available=item.inventory.qty if item.inventory else 0,
        )


class AccountService:
    @staticmethod
    def authenticate(db: Session, username: str, password: str) -> str | None:
        signon = db.get(Signon, username)
        if not signon or not verify_password(password, signon.password):
            return None
        return signon.username

    @staticmethod
    def register_account(db: Session, payload: AccountCreate) -> AccountOut:
        if db.get(Signon, payload.username):
            raise HTTPException(status_code=400, detail="Username already exists")
        db.add(Signon(username=payload.username, password=hash_password(payload.password)))
        db.add(Account(
            userid=payload.username, email=payload.email, firstname=payload.firstname,
            lastname=payload.lastname, addr1=payload.addr1, addr2=payload.addr2,
            city=payload.city, state=payload.state, zip=payload.zip,
            country=payload.country, phone=payload.phone
        ))
        db.add(Profile(
            userid=payload.username, langpref=payload.langpref,
            favcategory=payload.favcategory, mylistopt=payload.mylistopt,
            banneropt=payload.banneropt
        ))
        db.commit()
        return AccountService.get_account(db, payload.username)

    @staticmethod
    def get_account(db: Session, username: str) -> AccountOut:
        acct = db.get(Account, username)
        prof = db.get(Profile, username)
        if not acct or not prof:
            raise HTTPException(status_code=404, detail="Account not found")
        banner = db.get(BannerData, prof.favcategory) if prof.favcategory else None
        return AccountOut(
            username=acct.userid, email=acct.email, firstname=acct.firstname,
            lastname=acct.lastname, addr1=acct.addr1, addr2=acct.addr2,
            city=acct.city, state=acct.state, zip=acct.zip, country=acct.country,
            phone=acct.phone, langpref=prof.langpref, favcategory=prof.favcategory,
            mylistopt=prof.mylistopt, banneropt=prof.banneropt,
            bannername=banner.bannername if banner else None
        )


class OrderService:
    @staticmethod
    def create_order(db: Session, username: str, payload: OrderCreate) -> OrderOut:
        """
        Modernized equivalent of legacy OrderService.insertOrder(order).
        Executes atomically: validates & decrements inventory, increments sequence,
        and persists ORDERS, ORDERSTATUS, and LINEITEM.
        """
        acct = db.get(Account, username)
        if not acct:
            raise HTTPException(status_code=404, detail="Account not found")

        try:
            total_price = Decimal("0.00")
            line_items_to_create: list[tuple[int, Item, int]] = []

            for idx, req_item in enumerate(payload.items, start=1):
                item = db.get(Item, req_item.itemid.upper())
                if not item:
                    raise HTTPException(status_code=404, detail=f"Item {req_item.itemid} not found")

                # Atomic conditional inventory decrement (fixes legacy negative stock bug)
                stmt = (
                    update(Inventory)
                    .where(Inventory.itemid == item.itemid, Inventory.qty >= req_item.quantity)
                    .values(qty=Inventory.qty - req_item.quantity)
                )
                result = db.execute(stmt)
                if result.rowcount == 0:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Insufficient inventory for item {item.itemid}"
                    )

                total_price += item.listprice * req_item.quantity
                line_items_to_create.append((idx, item, req_item.quantity))

            seq = db.get(Sequence, "ordernum")
            if not seq:
                seq = Sequence(name="ordernum", nextid=1000)
                db.add(seq)
            order_id = seq.nextid
            seq.nextid += 1

            order = Order(
                orderid=order_id,
                userid=acct.userid,
                shipaddr1=payload.shipaddr1 or acct.addr1,
                shipaddr2=acct.addr2,
                shipcity=payload.shipcity or acct.city,
                shipstate=payload.shipstate or acct.state,
                shipzip=payload.shipzip or acct.zip,
                shipcountry=payload.shipcountry or acct.country,
                billaddr1=acct.addr1,
                billaddr2=acct.addr2,
                billcity=acct.city,
                billstate=acct.state,
                billzip=acct.zip,
                billcountry=acct.country,
                totalprice=total_price,
                billtofirstname=acct.firstname,
                billtolastname=acct.lastname,
                shiptofirstname=acct.firstname,
                shiptolastname=acct.lastname,
                creditcard=payload.creditcard,
                exprdate=payload.exprdate,
                cardtype=payload.cardtype,
            )
            db.add(order)
            db.add(OrderStatus(orderid=order_id, linenum=order_id, status="P"))

            for linenum, item, qty in line_items_to_create:
                db.add(LineItem(
                    orderid=order_id, linenum=linenum,
                    itemid=item.itemid, quantity=qty, unitprice=item.listprice
                ))

            db.commit()
            db.refresh(order)
            return OrderOut.model_validate(order)
        except Exception:
            db.rollback()
            raise
