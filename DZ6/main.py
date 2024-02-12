import sqlalchemy
import databases
from fastapi import FastAPI
import aiosqlite
import logging
from pydantic import BaseModel, Field
from typing import List
from random import randint, choice


DATABASE_URL = "sqlite:///seminar6.db"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()
users = sqlalchemy.Table(
"users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("first_name", sqlalchemy.String(32)),
    sqlalchemy.Column("second_name", sqlalchemy.String(32)),
    sqlalchemy.Column("email", sqlalchemy.String(32)),
    sqlalchemy.Column("password", sqlalchemy.String(32)),
)

products = sqlalchemy.Table(
"products",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(32)),
    sqlalchemy.Column("description", sqlalchemy.String(2000)),
    sqlalchemy.Column("price", sqlalchemy.Integer),
)

orders = sqlalchemy.Table(
"orders",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("users_table_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id")),
    sqlalchemy.Column("products_table_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("products.id")),

    # sqlalchemy.Column("users_table_id", sqlalchemy.Integer),
    # sqlalchemy.Column("products_table_id", sqlalchemy.Integer),
    sqlalchemy.Column("order_date", sqlalchemy.String(32)),
    sqlalchemy.Column("order_status", sqlalchemy.String(32)),
)

engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


# Пользователи
class User(BaseModel):
    first_name: str = Field(max_length=32)
    second_name: str = Field(max_length=32)
    email: str = Field(max_length=32)
    password: str = Field(max_length=32)


class UserId(User):
    id: int



@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/fake_users/{count}")
async def create_users(count: int):
    for i in range(count):
        query = users.insert().values(
            first_name=f'first_name{i}',
            second_name=f'second_name{i}',
            email=f'mail{i}@mail.ru',
            password=f'password{i}')
        await database.execute(query)
    return {'message': f'{count} fake users create'}




@app.get("/users/", response_model=List[User])
async def read_users():
    query = users.select()
    return await database.fetch_all(query)


@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, new_user: User):
    query = users.update().where(users.c.id == user_id).values(**new_user.dict())
    await database.execute(query)
    return {**new_user.dict(), "id": user_id}


@app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int):
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)



@app.post("/users/", response_model=UserId)
async def create_user(user: User):
    query = users.insert().values(**user.model_dump())
    last_record_id = await database.execute(query)
    return {**user.model_dump(), "id": last_record_id}


@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return {"message": "User deleted"}


# Товары
class Products(BaseModel):
    name: str = Field(max_length=32)
    description: str = Field(max_length=2000)
    price: int


class ProductsId(Products):
    id: int

@app.get("/fake_products/{count}")
async def create_products(count: int):
    for i in range(count):
        query = products.insert().values(
            name=f'name{i}',
            description=f'description',
            price=f'{randint(1,100)}')
        await database.execute(query)
    return {'message': f'{count} fake products create'}




@app.get("/products/", response_model=List[Products])
async def read_products():
    query = products.select()
    return await database.fetch_all(query)


@app.put("/products/{products_id}", response_model=Products)
async def update_products(products_id: int, new_products: Products):
    query = products.update().where(products.c.id == products_id).values(**new_products.dict())
    await database.execute(query)
    return {**new_products.dict(), "id": products_id}


@app.get("/products/{products_id}", response_model=Products)
async def read_product(products_id: int):
    query = products.select().where(products.c.id == products_id)
    return await database.fetch_one(query)



@app.post("/products/", response_model=ProductsId)
async def create_products(product: Products):
    query = products.insert().values(**product.model_dump())
    last_record_id = await database.execute(query)
    return {**product.model_dump(), "id": last_record_id}


@app.delete("/products/{products_id}")
async def delete_product(products_id: int):
    query = products.delete().where(products.c.id == products_id)
    await database.execute(query)
    return {"message": "Product deleted"}


# Заказы
class Orders(BaseModel):
    order_date: str = Field(max_length=32)
    order_status: str = Field(max_length=32)
    users_table_id: int
    products_table_id: int

class OrdersId(Orders):
    id: int



@app.get("/fake_orders/{count}")
async def create_orders(count: int):
    for i in range(count):
        query = orders.insert().values(
            users_table_id=2,
            products_table_id=1,
            order_date=f'2024-01-{randint(1,31)}',
            order_status=choice(['В работе', 'Готово']))
        await database.execute(query)
    return {'message': f'{count} fake orders create'}




@app.get("/orders/", response_model=List[Orders])
async def read_orders():
    query = orders.select()
    return await database.fetch_all(query)


@app.put("/orders/{orders_id}", response_model=Orders)
async def update_orders(orders_id: int, new_orders: Orders):
    query = orders.update().where(orders.c.id == orders).values(**new_orders.dict())
    await database.execute(query)
    return {**new_orders.dict(), "id": orders_id}


@app.get("/orders/{orders_id}", response_model=Orders)
async def read_orders(orders_id: int):
    query = orders.select().where(orders.c.id == orders_id)
    return await database.fetch_one(query)



@app.post("/orders/", response_model=OrdersId)
async def create_orders(order: Orders):
    query = orders.insert().values(**order.model_dump())
    last_record_id = await database.execute(query)
    return {**order.model_dump(), "id": last_record_id}


@app.delete("/orders/{orders_id}")
async def delete_order(orders_id: int):
    query = orders.delete().where(orders.c.id == orders_id)
    await database.execute(query)
    return {"message": "Orders deleted"}
