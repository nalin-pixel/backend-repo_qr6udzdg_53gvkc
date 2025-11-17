import os
from typing import Any, Dict, List, Optional
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

# Database connection using environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "app_db")

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


def get_db() -> AsyncIOMotorDatabase:
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(DATABASE_URL)
        _db = _client[DATABASE_NAME]
    return _db


async def create_document(collection_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    db = get_db()
    now = datetime.utcnow()
    payload = {**data, "created_at": now, "updated_at": now}
    result = await db[collection_name].insert_one(payload)
    payload["_id"] = str(result.inserted_id)
    return payload


async def get_documents(
    collection_name: str,
    filter_dict: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None,
    sort: Optional[List] = None,
) -> List[Dict[str, Any]]:
    db = get_db()
    cursor = db[collection_name].find(filter_dict or {})
    if sort:
        cursor = cursor.sort(sort)
    if limit:
        cursor = cursor.limit(limit)
    docs = []
    async for doc in cursor:
        doc["_id"] = str(doc.get("_id"))
        docs.append(doc)
    return docs


async def get_one(collection_name: str, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    db = get_db()
    doc = await db[collection_name].find_one(filter_dict)
    if doc:
        doc["_id"] = str(doc.get("_id"))
    return doc


async def upsert_one(collection_name: str, filter_dict: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
    db = get_db()
    now = datetime.utcnow()
    update_doc = {"$set": {**data, "updated_at": now}, "$setOnInsert": {"created_at": now}}
    await db[collection_name].update_one(filter_dict, update_doc, upsert=True)
    return await get_one(collection_name, filter_dict)
