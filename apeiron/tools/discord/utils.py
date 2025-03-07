from discord import Client, Message


def is_client_user(client: Client, message: Message) -> bool:
    return message.author == client.user
