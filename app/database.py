from neomodel import config as neomodel_config
from .config import settings
from neo4j import GraphDatabase
from neo4j import exceptions as neo4j_exceptions
import os

# Global driver instance
_driver = None


def init_database():
    """Initialize Neo4j database connection"""
    global _driver
    
    # Compose the full connection URL with credentials
    uri = settings.neo4j_uri
    
    # If credentials are not in URI, compose them
    if "@" not in uri:
        # Extract scheme and host
        if "://" in uri:
            scheme, host = uri.split("://", 1)
            uri = f"{scheme}://{settings.neo4j_user}:{settings.neo4j_password}@{host}"
    
    neomodel_config.DATABASE_URL = uri
    
    # Initialize Neo4j driver for direct queries
    _driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password)
    )
    _ensure_driver(_driver)
    
    print(f"✓ Connected to Neo4j database")


def _ensure_driver(driver):
    """Ensure the driver connection is usable.

    Neo4j Aura connections can become defunct over time; when that happens,
    the existing driver may keep raising SessionExpired/ServiceUnavailable.
    """
    if driver is None:
        raise RuntimeError("Neo4j driver is not initialized")
    try:
        with driver.session() as session:
            session.run("RETURN 1").consume()
    except (neo4j_exceptions.ServiceUnavailable, neo4j_exceptions.SessionExpired, OSError):
        raise


def get_db():
    """Get Neo4j driver instance"""
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )
        _ensure_driver(_driver)
        return _driver

    try:
        _ensure_driver(_driver)
    except (neo4j_exceptions.ServiceUnavailable, neo4j_exceptions.SessionExpired, OSError):
        try:
            _driver.close()
        except Exception:
            pass
        _driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )
        _ensure_driver(_driver)
    return _driver


def close_database():
    """Close database connection"""
    global _driver
    if _driver:
        _driver.close()
    # neomodel handles connection pooling automatically
    pass
