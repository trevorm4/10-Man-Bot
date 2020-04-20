import discord
from discord.ext import commands
import yaml
import random
from utils import get_member_name
from converters import Player

class Bot(commands.Bot):
    def __init__(self,command_prefix, drafting_scheme):
        """
        Constructor for Bot
            :param command_prefix: symbol to type before command. For ex, use "!" if you want to use "!<command>"
            :param drafting_scheme: list contains strings of format "<A/B><1-2>" where first char is team and 2nd char is # players
        """   
        commands.Bot.__init__(self,command_prefix=command_prefix)
        self.teams = {"A" : [], "B" : []}
        self.remaining = []
        self.captains = {"A" : None, "B": None}
        self.channels = {"A" : None, "B" : None}
        self.order = []
        self.drafting_dict = {"A" : [int(s[1]) for s in drafting_scheme if s[0] == "A"],
                              "B" : [int(s[1]) for s in drafting_scheme if s[0] == "B"]}
        self.turn = -1
        self.remove_command("help") # we make a custom help command
    async def set_captain(self, cap : Player, team):
        """
        Sets captain for specified team
            :param cap: discord.Member object representing user that is now captain
            :param team: string for team name ("A" or "B")
        """
        self.captains[team.upper()] = cap
        await self.add_to_team(cap,team)
        self.order.append(cap)
    async def add_to_team(self, player : Player, team):
        """
        Adds player to team
            :param player: Discord.Member representing player member
            :param team: string representing team name
            :return discord.Embed: embed message to display
        """
        if player in self.remaining:
            self.teams[team].append(player)
            self.remaining.remove(player)
            return discord.Embed(title="Valorant 10 Man Bot",
                description="{} has been drafted to team {}".format(get_member_name(player,lower=False), ":a:" if team == "A" else ":b:"))
        else:
            return discord.Embed(title="Valorant 10 Man Bot",description="Sorry, {} is already drafted".format(get_member_name(player)))
    async def new_game(self, players):
        """
        Clears instance variables in preperation for new game
            :param players: list of Discord.Member variables representing players
        """   
        if len(players) != 10:
            return discord.Embed(title="Valorant 10 Man Bot",
            description="You cannot start a game with only {} players".format(len(players)))
        self.teams = {"A": [], "B" : []}
        self.captains = {"A" : None, "B" : None}
        self.nick_to_player = {get_member_name(p) : p for p in players}
        self.remaining = players.copy()
        self.turn = 1
        self.order = []
        return discord.Embed(title="Valorant 10 Man Bot",
            description="New game started".format(len(players)))
    async def generate_captains(self,team_a_channel, team_b_channel):
        """
        Generates two new captains and sets them as captains
            :ret discord.Embed: embed object to display 
        """
        if len(self.remaining) != 10:
            return discord.Embed(title="Valorant 10 Man Bot",
                description="Please use the command !new and ensure you have 10 players in the channel before selecting captains")
        caps = random.sample(self.remaining, 2) # 2 captains
        for i,team in enumerate(self.captains.keys()):
            await self.set_captain(caps[i],team)
        return discord.Embed(title="Valorant 10 Man Bot",
            description="The captains are @{} (1st pick) and @{} (2nd pick)".format(get_member_name(caps[0],lower=False),get_member_name(caps[1],lower=False)))
    async def get_remaining(self):
        """
        Gets remaining players
        :ret: list of remaining players of type Discord.Member
        """   
        return self.remaining
    async def move_player(self, player : Player, channel):
        """
        Moves player to specified channel
            :param player: discord.Member object that represents player
            :param channel: discord.VoiceChannel object representing channel to move to
        """
        await player.move_to(channel)
    async def draft_player(self, captain : Player, player : Player, channel_dict):
        """
        Drafts a player according to 1-2-1-1-1-1-1-1-1 schema
            :param captain: discord.Member object representing captain
            :param player:  discord.Member object representing player
        """
        if player not in self.remaining:
            return discord.Embed(title="Valorant 10 Man Bot",description="{} is not a valid player or they have been drafted already".format(player))
        elif captain not in self.captains.values():
            return discord.Embed(title="Valorant 10 Man Bot",description="{} is not a captain".format(get_member_name(captain)))
            
        team = "A" if captain == self.captains["A"] else "B"
        opp = "B" if team == "A" else "A"

        if len(self.teams[team]) == 0 and len(self.teams[opp]) == 0 and self.order[0] != captain: 
            return discord.Embed(title="Valorant 10 Man bot",description="The other captain gets to draft first, sorry!")
        elif len(self.teams[team]) > len(self.teams[opp]) \
                or len(self.teams[team]) >= sum(self.drafting_dict[team][:self.turn]) + 1: # + 1 to include captain
            return discord.Embed(title="Valorant 10 Man bot",description="You've already drafted this turn, please wait for the other captain")
        
        embed = await self.add_to_team(player, team)
        channel = channel_dict[team]
        await self.move_player(player,channel)

        if team == "B" and len(self.teams[team]) == sum(self.drafting_dict[team][:self.turn]) + 1: # + 1 to include captain
            self.turn += 1

        return embed
        