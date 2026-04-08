#Backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
from app.routers import order_item
from app.routers.chat import router as chat_router
from app.routers.chat_ws import router as chat_ws_router
from app.core.logging import setup_logging
from app.database.engine import SessionLocal
from pathlib import Path
from app.routers import (
    users,
    products,
    product_variants,
    inventory,
    orders,
    upload,
    category,
    auth,
    reports,
    cart
)

setup_logging()
app = FastAPI(title="Web Bán Quần Áo Backend")
BASE_DIR = Path(__file__).resolve().parent
app.mount(
    "/static/uploads",
    StaticFiles(directory="static/uploads"),
    name="uploads"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(category.router)
app.include_router(products.router)
app.include_router(product_variants.router)
app.include_router(inventory.router)
app.include_router(orders.router)
app.include_router(cart.router)
app.include_router(order_item.router)
app.include_router(chat_router)
app.include_router(chat_ws_router)
#app.include_router(upload.router)
app.include_router(reports.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Clothing Store API"}
