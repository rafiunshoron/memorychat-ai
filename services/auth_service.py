from supabase import Client, create_client

from config import APP_URL, SUPABASE_ANON_KEY, SUPABASE_URL


def create_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def register_user(
    full_name: str,
    email: str,
    password: str,
    phone: str,
):
    client = create_supabase_client()

    return client.auth.sign_up(
        {
            "email": email.strip().lower(),
            "password": password,
            "options": {
                "data": {
                    "full_name": full_name.strip(),
                    "phone": phone.strip(),
                },
                "email_redirect_to": APP_URL,
            },
        }
    )


def login_user(email: str, password: str):
    client = create_supabase_client()

    return client.auth.sign_in_with_password(
        {
            "email": email.strip().lower(),
            "password": password,
        }
    )


def restore_session(access_token: str, refresh_token: str):
    client = create_supabase_client()
    return client.auth.set_session(access_token, refresh_token)


def logout_user(access_token: str, refresh_token: str) -> None:
    client = create_supabase_client()
    client.auth.set_session(access_token, refresh_token)
    client.auth.sign_out()