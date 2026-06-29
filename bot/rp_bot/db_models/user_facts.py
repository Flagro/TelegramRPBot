from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorDatabase

from .base_db_model import BaseDBModel
from ...models.handlers_input import Person, Context
from ..memory_utils import get_display_name, get_participant_key


class UserFacts(BaseDBModel):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db)
        self.user_facts = db.user_facts

    async def get_chat_facts(self, context: Context) -> List[Tuple[str, str]]:
        """
        Return a list of facts for the current chat as a list
        user_handle, fact
        """
        cursor = self.user_facts.find({"chat_id": context.chat_id})
        facts = []
        async for doc in cursor:
            for fact in doc["facts"]:
                facts.append((doc["user_handle"], fact))
        return facts

    async def get_user_facts(self, context: Context, person: Person) -> List[str]:
        facts = await self._find_user_facts_doc(
            context=context,
            participant_key=get_participant_key(person),
            fallback_user_handle=person.user_handle,
        )
        return facts.get("facts", []) if facts else []

    async def get_user_facts_by_participant(
        self,
        context: Context,
        participant_key: str,
        fallback_user_handle: Optional[str] = None,
    ) -> List[str]:
        facts = await self._find_user_facts_doc(
            context=context,
            participant_key=participant_key,
            fallback_user_handle=fallback_user_handle,
        )
        return facts.get("facts", []) if facts else []

    async def get_facts_for_user_handle(
        self, context: Context, user_handle: str
    ) -> List[str]:
        """Get all facts for a user handle in the current chat

        Args:
            context (Context): context of the chat
            user_handle (str): user handle to get facts for

        Returns:
            List[str]: list of facts
        """
        facts = await self.user_facts.find_one(
            {"chat_id": context.chat_id, "user_handle": user_handle}
        )
        return facts.get("facts", []) if facts else []

    async def add_fact(
        self,
        context: Context,
        facts_user_handle: str,
        fact: str,
        person: Optional[Person] = None,
        source_dialog_id: Optional[str] = None,
        created_by: str = "manual",
    ) -> None:
        filters: Dict[str, Any] = {
            "chat_id": context.chat_id,
            "user_handle": facts_user_handle,
        }
        set_on_insert: Dict[str, Any] = {
            "chat_id": context.chat_id,
            "user_handle": facts_user_handle,
        }
        set_fields: Dict[str, Any] = {}
        if person:
            participant_key = get_participant_key(person)
            filters = {"chat_id": context.chat_id, "participant_key": participant_key}
            set_on_insert["participant_key"] = participant_key
            set_on_insert["telegram_user_id"] = person.telegram_id
            set_fields["user_handle"] = person.user_handle
            set_fields["display_name"] = get_display_name(person)

        fact_item = {
            "fact_id": str(uuid4()),
            "fact": fact,
            "visibility": "chat",
            "confidence": None,
            "source_dialog_id": source_dialog_id,
            "created_by": created_by,
            "status": "active",
        }
        update: Dict[str, Any] = {
            "$setOnInsert": set_on_insert,
            "$push": {"facts": fact, "fact_items": fact_item},
        }
        if set_fields:
            update["$set"] = set_fields
        await self.user_facts.update_one(filters, update, upsert=True)

    async def clear_facts(self, context: Context, facts_user_handle: str) -> None:
        """Delete all facts associated with a user

        Args:
            context (Context): context of the chat
            facts_user_handle (str): user handle to delete facts for
        """
        await self.user_facts.delete_one(
            {"chat_id": context.chat_id, "user_handle": facts_user_handle}
        )

    async def clear_user_data(self, user_handle: str) -> None:
        await self.user_facts.delete_many({"user_handle": user_handle})

    async def _find_user_facts_doc(
        self,
        context: Context,
        participant_key: Optional[str],
        fallback_user_handle: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        if participant_key:
            facts = await self.user_facts.find_one(
                {"chat_id": context.chat_id, "participant_key": participant_key}
            )
            if facts:
                return facts
        if fallback_user_handle:
            return await self.user_facts.find_one(
                {"chat_id": context.chat_id, "user_handle": fallback_user_handle}
            )
        return None

    async def search_chat_facts(
        self,
        context: Context,
        query: Optional[str] = None,
        participant_key: Optional[str] = None,
    ) -> List[str]:
        filters: Dict[str, Any] = {"chat_id": context.chat_id}
        if participant_key:
            filters["participant_key"] = participant_key
        if query:
            filters["facts"] = {"$regex": query, "$options": "i"}

        cursor = self.user_facts.find(filters)
        facts = []
        async for doc in cursor:
            for fact in doc.get("facts", []):
                if query and query.lower() not in fact.lower():
                    continue
                facts.append(f"{doc.get('user_handle', 'unknown')}: {fact}")
        return facts
