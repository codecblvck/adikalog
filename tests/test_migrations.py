import pytest

from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Sale, SaleItem


def make_sale(user, key="k1", total=1000, discount=0):
    sale = Sale(client_key=key, discount=discount, total=total, created_by=user.id)
    db.session.add(sale)
    db.session.commit()
    return sale


def make_item(sale, quantity=1, selling_price=1200):
    item = SaleItem(
        sale_id=sale.id,
        product_name="U-Bolt",
        quantity=quantity,
        selling_price=selling_price,
    )
    db.session.add(item)
    db.session.commit()
    return item


def test_tables_exist(app):
    with app.app_context():
        names = set(inspect(db.engine).get_table_names())
    assert {"sales", "sale_items", "users"} <= names


def test_valid_sale_is_saved(user):
    sale = make_sale(user)
    make_item(sale)
    assert sale.receipt_no == "0001"
    assert len(sale.items) == 1


def test_total_must_be_positive(user):
    with pytest.raises(IntegrityError):
        make_sale(user, total=0)


def test_discount_cannot_be_negative(user):
    with pytest.raises(IntegrityError):
        make_sale(user, discount=-1)


def test_quantity_must_be_at_least_one(user):
    sale = make_sale(user)
    with pytest.raises(IntegrityError):
        make_item(sale, quantity=0)


def test_selling_price_must_be_at_least_one(user):
    sale = make_sale(user)
    with pytest.raises(IntegrityError):
        make_item(sale, selling_price=0)


def test_client_key_must_be_unique(user):
    make_sale(user, key="k1")
    with pytest.raises(IntegrityError):
        make_sale(user, key="k1")
