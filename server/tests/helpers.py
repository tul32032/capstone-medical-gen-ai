from authentication.constants import ACCESS_TOKEN_COOKIE
from authentication.utils import generate_tokens_for_user


def attach_access_cookie(client, user):
    access_token, _ = generate_tokens_for_user(user)
    client.cookies[ACCESS_TOKEN_COOKIE] = str(access_token)
    return client
