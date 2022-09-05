from enum import Enum
import datetime

from handlers.common.base_model import BaseModel, db
from handlers.users.models import User


class Destination(BaseModel):
    __tablename__ = 'destinations'

    latitude = db.Column(db.VARCHAR(15), nullable=False)
    longitude = db.Column(db.VARCHAR(15), nullable=False)
    name = db.Column(db.VARCHAR(15), nullable=True)
    address = db.Column(db.VARCHAR(250), nullable=False)
    zipcode = db.Column(db.INT, nullable=False)
    ext_num = db.Column(db.VARCHAR(4), nullable=False)
    int_num = db.Column(db.VARCHAR(4), nullable=True)
    city = db.Column(db.VARCHAR(60), nullable=False)


class Product(BaseModel):
    __tablename__ = 'products'

    class SizeEnum(Enum):
        S = 'Small'
        M = 'Medium'
        L = 'Large'
        SPECIAL = 'Special'

    def get_size(self):
        if self.weight <= 5:
            return self.SizeEnum.S.name
        if self.weight <= 15:
            return self.SizeEnum.M.name
        if self.weight <= 25:
            return self.SizeEnum.L.name
        return self.SizeEnum.SPECIAL.name

    def __init__(self, weight, sku):
        self.weight = weight
        self.sku = sku
        self.size = self.get_size()

    weight = db.Column(db.DECIMAL, nullable=False)  # KG
    size = db.Column(db.VARCHAR(8), nullable=False)
    sku = db.Column(db.VARCHAR(10), nullable=False)


class OrderProducts(db.Model):
    __tablename__ = 'orders_products'
    id = db.Column(db.Integer(), primary_key=True)
    order_id = db.Column(db.Integer(), db.ForeignKey('orders.id', ondelete='CASCADE'))
    product_id = db.Column(db.Integer(), db.ForeignKey('products.id', ondelete='CASCADE'))


class Order(BaseModel):
    __tablename__ = 'orders'

    class OrdersStatus(Enum):
        creado = 'creado'
        recolectado = 'recolectado'
        en_estacion = 'en_estacion'
        en_ruta = 'en_ruta'
        entregado = 'entregado'
        cancelado = 'cancelado'

        @classmethod
        def list(cls):
            return list(map(lambda c: c.value, cls))

    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    products = db.relationship('Product', secondary='orders_products')
    origin_id = db.Column(db.Integer(), db.ForeignKey('destinations.id', ondelete='CASCADE'))
    destination_id = db.Column(db.Integer(), db.ForeignKey('destinations.id', ondelete='CASCADE'))
    status = db.Column(db.VARCHAR(15), nullable=False)

    def __init__(self, user_id, origin_id, destination_id):
        self.user_id = user_id
        self.origin_id = origin_id
        self.destination_id = destination_id
        self.status = self.OrdersStatus.CREATED.value

    def add_product(self, product):
        # Validations, stock check, user_credit, etc
        self.products.append(product)

    def move_forward(self):
        if self.status == self.OrdersStatus.creado.value:
            self.status = self.OrdersStatus.recolectado.value
        elif self.status == self.OrdersStatus.recolectado.value:
            self.status = self.OrdersStatus.en_estacion.value
        elif self.status == self.OrdersStatus.en_estacion.value:
            self.status = self.OrdersStatus.en_ruta.value
        elif self.status == self.OrdersStatus.en_ruta.value:
            self.status = self.OrdersStatus.entregado.value
        self.save()

    def cancel(self):
        # Check if we should return the funds
        if self.status == self.OrdersStatus.en_ruta.value or self.status == self.OrdersStatus.entregado.value:
            raise Exception("Can not be cancelled in it's current status")

        self.status = self.OrdersStatus.cancelado.value
        self.save()
        now = datetime.datetime.utcnow()
        difference = now - self.date_created
        if difference.total_seconds() / 60 > 2:
            # TODO update transactions table with a refund or a reason
            return "Cancelled but we're keeping the funds"
        return ""

    def to_json(self):
        return dict(id=self.id, created_at=self.date_created, status=self.status, products=self.products,
                    origin=self.origin_id, destination=self.destination_id)
