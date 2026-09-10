import logging
from functools import lru_cache

from mem0 import MemoryClient

from config import MEM0_API_KEY


logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_memory_client() -> MemoryClient:
    return MemoryClient(api_key=MEM0_API_KEY)


def search_user_memories(
    user_id: str,
    query: str,
    limit: int = 5,
) -> list[str]:
    try:
        client = get_memory_client()

        response = client.search(
            query=query,
            filters={"user_id": str(user_id)},
            top_k=limit,
            threshold=0.2,
        )

        return [
            result["memory"]
            for result in response.get("results", [])
            if result.get("memory")
        ]

    except Exception:
        logger.exception("Unable to retrieve memories from Mem0.")
        return []


def save_memory_turn(
    user_id: str,
    run_id: str,
    user_message: str,
    assistant_message: str,
) -> None:
    try:
        client = get_memory_client()

        client.add(
            messages=[
                {
                    "role": "user",
                    "content": user_message,
                },
                {
                    "role": "assistant",
                    "content": assistant_message,
                },
            ],
            user_id=str(user_id),
            run_id=str(run_id),
            metadata={
                "source": "memorychat",
                "conversation_id": str(run_id),
            },
            infer=True,
        )

    except Exception:
        # Mem0 being unavailable should not stop the normal chatbot.
        logger.exception("Unable to save the conversation turn to Mem0.")