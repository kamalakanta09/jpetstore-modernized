from decimal import Decimal
from sqlalchemy.orm import Session
from app.models import (
    Account, BannerData, Category, Inventory, Item,
    Product, Profile, Sequence, Signon, Supplier
)
from app.security import hash_password


def seed_database(db: Session) -> None:
    if db.get(Category, "FISH"):
        return  # Already seeded

    # 1. Seed Legacy Accounts (j2ee / j2ee and ACID / ACID)
    for uid, pwd, fname, lname, fav in [
        ("j2ee", "j2ee", "ABC", "XYX", "DOGS"),
        ("ACID", "ACID", "ABC", "XYX", "BIRDS"),
    ]:
        db.add(Signon(username=uid, password=hash_password(pwd)))
        db.add(Account(
            userid=uid, email="yourname@yourdomain.com", firstname=fname, lastname=lname,
            status="OK", addr1="901 San Antonio Road", addr2="MS UCUP02-206",
            city="Palo Alto", state="CA", zip="94303", country="USA", phone="555-555-5555"
        ))
        db.add(Profile(userid=uid, langpref="english", favcategory=fav, mylistopt=True, banneropt=True))

    # 2. Seed Banner Data & Sequence
    for cat in ["FISH", "CATS", "DOGS", "REPTILES", "BIRDS"]:
        db.add(BannerData(favcategory=cat, bannername=f"banner_{cat.lower()}.gif"))
    db.add(Sequence(name="ordernum", nextid=1000))
    db.add(Supplier(suppid=1, name="XYZ Pets", status="AC", city="Los Angeles", state="CA"))

    # 3. Seed 5 Categories
    categories = [
        ("FISH", "Fish", "Saltwater, Freshwater"),
        ("DOGS", "Dogs", "Various Breeds"),
        ("REPTILES", "Reptiles", "Lizards, Turtles, Snakes"),
        ("CATS", "Cats", "Various Breeds, Exotic Varieties"),
        ("BIRDS", "Birds", "Exotic Varieties"),
    ]
    for cid, name, descn in categories:
        db.add(Category(catid=cid, name=name, descn=descn))

    # 4. Seed Representative Products & Items from jpetstore-hsqldb-dataload.sql
    products = [
        ("FI-SW-01", "FISH", "Angelfish", "Saltwater fish from Australia"),
        ("FI-SW-02", "FISH", "Tiger Shark", "Saltwater fish from Australia"),
        ("K9-BD-01", "DOGS", "Bulldog", "Friendly dog from England"),
        ("K9-PO-02", "DOGS", "Poodle", "Cute dog from France"),
        ("RP-SN-01", "REPTILES", "Rattlesnake", "Doubles as a watch dog"),
        ("FL-DSH-01", "CATS", "Manx", "Great for reducing mouse populations"),
        ("AV-CB-01", "BIRDS", "Amazon Parrot", "Great companion for up to 75 years"),
    ]
    for pid, cat, name, descn in products:
        db.add(Product(productid=pid, category=cat, name=name, descn=descn))

    items = [
        ("EST-1", "FI-SW-01", "16.50", "10.00", "Large"),
        ("EST-2", "FI-SW-01", "16.50", "10.00", "Small"),
        ("EST-3", "FI-SW-02", "18.50", "12.00", "Toothless"),
        ("EST-6", "K9-BD-01", "18.50", "12.00", "Male Adult"),
        ("EST-7", "K9-BD-01", "18.50", "12.00", "Female Puppy"),
        ("EST-8", "K9-PO-02", "18.50", "12.00", "Male Puppy"),
        ("EST-11", "RP-SN-01", "18.50", "12.00", "Venomless"),
        ("EST-14", "FL-DSH-01", "58.50", "12.00", "Tailless"),
        ("EST-18", "AV-CB-01", "193.50", "92.00", "Adult Male"),
    ]
    for iid, pid, lp, uc, attr1 in items:
        db.add(Item(
            itemid=iid, productid=pid, listprice=Decimal(lp),
            unitcost=Decimal(uc), supplier=1, status="P", attr1=attr1
        ))
        db.add(Inventory(itemid=iid, qty=10000))

    db.commit()
