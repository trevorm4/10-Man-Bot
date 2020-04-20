import discord
def get_member_name(member, lower=True):
    if type(member) == str:
        if lower:
            return member.lower()
        return member
    if member.nick:
        if lower:
            return member.nick.lower()
        return member.nick
    if lower:
        return member.name.lower()
    return member.name
