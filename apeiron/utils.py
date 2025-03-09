import discord


def parse_feature_gates(feature_gates_str: str) -> dict[str, bool]:
    """Parse feature gates from a string into a dictionary."""
    feature_gates_dict = {}
    for feature_gate in feature_gates_str.split(","):
        feature_gate = feature_gate.strip()
        if feature_gate:
            feature_gates_dict[feature_gate] = True
    return feature_gates_dict


def create_thread_id(message: discord.Message):
    """Create a thread ID from a Discord message."""
    if message.guild is None:
        return "/".join(
            [
                "guild",
                "__private__",
                "channel",
                str(message.author.id),
            ]
        )
    if message.thread is None:
        return "/".join(
            [
                "guild",
                str(message.guild.id),
                "channel",
                str(message.channel.id),
            ]
        )
    return "/".join(
        [
            "guild",
            str(message.guild.id),
            "channel",
            str(message.channel.id),
            "thread",
            str(message.thread.id),
        ]
    )
