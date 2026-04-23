from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from neo4j import GraphDatabase
import os
from .database import init_database, close_database
from .routes import (
    auth_router,
    user_router,
    farm_product_router,
    order_router,
    notification_router,
    message_router,
    review_router,
    cart_router,
    admin_router
)
from .config import settings

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="🌾 FarmFresh Connect",
    version="2.0.0",
    description="A Farm-to-Market Platform with Unified RBAC Authentication",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - Allow frontend domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://farmfresh-connect-frontend.onrender.com",  # Production frontend
        "http://localhost:5000",  # Local development
        "http://127.0.0.1:3000",  # Local development alternative
        "http://localhost:55030",  # Flutter web dev server
        "http://127.0.0.1:55030",  # Flutter web dev server alternative
        "http://localhost:62333",
        "http://localhost:58931",

    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",  # Allow any localhost port
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
    expose_headers=["*"],
    max_age=3600,
)

# ✅ Neo4j Aura Connection
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    init_database()
    print(f"🚀 {settings.app_name} v{settings.app_version} started successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    close_database()
    driver.close()
    print("👋 Application shutdown complete")

# Redirect root to Swagger docs
@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Redirect root URL to Swagger docs"""
    return RedirectResponse(url="/docs")

# ✅ SEARCH ROUTE (Updated for User model)
@app.get("/search")
def search_items(query: str = Query(...), search_type: str = Query(...)):
    """
    Search for products, sellers, or buyers by name using unified User model.
    """
    with driver.session() as session:
        if search_type == "products":
            cypher = """
            MATCH (p:FarmProduct)
            WHERE toLower(p.name) CONTAINS toLower($query)
            RETURN p.uid AS id, p.name AS name, p.price AS price, p.type AS location
            LIMIT 10
            """
        elif search_type == "sellers":
            cypher = """
            MATCH (u:User {role: 'seller'})
            WHERE toLower(u.full_name) CONTAINS toLower($query)
            RETURN u.uid AS id, u.full_name AS name, u.location AS location
            LIMIT 10
            """
        else:
            cypher = """
            MATCH (u:User {role: 'buyer'})
            WHERE toLower(u.full_name) CONTAINS toLower($query)
            RETURN u.uid AS id, u.full_name AS name, u.location AS location
            LIMIT 10
            """

        results = session.run(cypher, {"query": query})
        items = [dict(record) for record in results]
        return items

# Include routers (using unified auth routes, removed old buyer/seller routes)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(farm_product_router)
app.include_router(order_router)
app.include_router(notification_router)
app.include_router(message_router)
app.include_router(review_router)
app.include_router(cart_router)
app.include_router(admin_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
