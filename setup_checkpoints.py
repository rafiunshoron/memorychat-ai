from langgraph.checkpoint.postgres import PostgresSaver

from config import SUPABASE_DB_URL


def setup_checkpoint_tables() -> None:
    with PostgresSaver.from_conn_string(
        SUPABASE_DB_URL
    ) as checkpointer:
        checkpointer.setup()

    print("LangGraph checkpoint tables created successfully.")


if __name__ == "__main__":
    setup_checkpoint_tables()