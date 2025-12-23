# importing necessary modules from SQLAlchemy
from sqlalchemy import Column, Table, create_engine, String, ForeignKey, Integer, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
import os

# Remove existing database to start fresh
if os.path.exists('shop.db'):
    os.remove('shop.db')

# Creating an engine and base
engine = create_engine('sqlite:///shop.db')
class Base(DeclarativeBase):
    pass
Session = sessionmaker(bind=engine)
session = Session()

# Enable foreign key constraints for SQLite
from sqlalchemy import event
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Defining the User model
class User(Base):
    __tablename__ = 'Users'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    
    # Defining the relationship with the order model: One-to-Many
    orders: Mapped[list['Order']] = relationship(back_populates='user')
    
# Defining the product model
class Product(Base):
    __tablename__ = 'Products'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Defining the relationship with the order model: Many-to-Many
    order_products: Mapped[list['OrderProduct']] = relationship(back_populates='product')

# Defining the order model
class Order(Base):
    __tablename__ = 'Orders'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('Users.id'), nullable=True)

    # Defining the relationship with the user model: Many-to-One
    user: Mapped['User'] = relationship(back_populates='orders')
    # Defining the relationship with the product model: Many-to-Many
    order_products: Mapped[list['OrderProduct']] = relationship(back_populates='order', cascade='all, delete-orphan')

# Association model for many-to-many between Order and Product
class OrderProduct(Base):
    __tablename__ = 'order_product'
    order_id: Mapped[int] = mapped_column(ForeignKey('Orders.id', ondelete='CASCADE'), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('Products.id'), primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    order: Mapped['Order'] = relationship(back_populates='order_products')
    product: Mapped['Product'] = relationship(back_populates='order_products')
    
# Creating the tables
Base.metadata.create_all(engine)

# adding new users to the database
new_user_1 = User(name='Richard', email='richardsemail@email.com')
new_user_2 = User(name='Regina', email='meangirls@email.com')
session.add(new_user_1)
session.add(new_user_2)

# adding new products to the database
new_product_1 = Product(name='Laptop', price=1200)
new_product_2 = Product(name='Smartphone', price=800)
new_product_3 = Product(name='Tablet', price=600)
session.add(new_product_1)
session.add(new_product_2)
session.add(new_product_3)

# adding new orders to the database
new_order_1 = Order(user_id=1)
new_order_2 = Order(user_id=2)
new_order_3 = Order(user_id=1)
new_order_4 = Order(user_id=2)
session.add_all([new_order_1, new_order_2, new_order_3, new_order_4])
session.commit()

# adding order-product associations
op1 = OrderProduct(order_id=1, product_id=1, quantity=1)
op2 = OrderProduct(order_id=2, product_id=2, quantity=3)
op3 = OrderProduct(order_id=3, product_id=3, quantity=4)
op4 = OrderProduct(order_id=4, product_id=1, quantity=2)
session.add_all([op1, op2, op3, op4])
session.commit()

# Querying the database to retrieve all users
query = select(User)
users = session.execute(query).scalars().all()

# Printing the retrieved users
for user in users:
    print(f"NAME: {user.name} EMAIL: {user.email}")
    
# Querying the database to retrieve all products
query = select(Product)
products = session.execute(query).scalars().all()

# Printing the retrieved products
for product in products:
    print(f"{product.name}: ${product.price}")
    
# Querying the database to retrieve all order-product associations
query = select(OrderProduct)
order_products = session.execute(query).scalars().all()

# Printing the retrieved order details
for op in order_products:
    print(f"User {op.order.user.name} purchased {op.quantity} of product {op.product.name}")

# updating the price of product 2
query = select(Product).where(Product.id == 2)
product = session.execute(query).scalars().first()
product.price = 750
session.commit()

# Deleting user 1 from the database
query = select(User).where(User.id == 1)
user = session.execute(query).scalars().first()
session.delete(user)
session.commit()


# closing the session
session.close()