import discord

def get_member_name(member):
    if member.nick:
        return member.nick
    return member.name