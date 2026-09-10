from uuid import uuid4

from services.auth_service import create_supabase_client


def get_authenticated_client(
    access_token: str,
    refresh_token: str,
):
    client = create_supabase_client()
    client.auth.set_session(access_token, refresh_token)
    return client


def create_conversation(
    access_token: str,
    refresh_token: str,
    user_id: str,
    title: str = "New conversation",
) -> dict:
    client = get_authenticated_client(access_token, refresh_token)
    conversation_id = str(uuid4())

    response = (
        client.table("conversations")
        .insert(
            {
                "id": conversation_id,
                "user_id": user_id,
                "title": title,
            }
        )
        .execute()
    )

    return response.data[0]


def list_conversations(
    access_token: str,
    refresh_token: str,
    user_id: str,
) -> list[dict]:
    client = get_authenticated_client(access_token, refresh_token)

    response = (
        client.table("conversations")
        .select("id, title, created_at, updated_at")
        .eq("user_id", user_id)
        .order("updated_at", desc=True)
        .execute()
    )

    return response.data


def rename_conversation(
    access_token: str,
    refresh_token: str,
    user_id: str,
    conversation_id: str,
    title: str,
) -> None:
    client = get_authenticated_client(access_token, refresh_token)

    (
        client.table("conversations")
        .update({"title": title.strip()})
        .eq("id", conversation_id)
        .eq("user_id", user_id)
        .execute()
    )


def delete_conversation(
    access_token: str,
    refresh_token: str,
    user_id: str,
    conversation_id: str,
) -> None:
    client = get_authenticated_client(access_token, refresh_token)

    (
        client.table("conversations")
        .delete()
        .eq("id", conversation_id)
        .eq("user_id", user_id)
        .execute()
    )