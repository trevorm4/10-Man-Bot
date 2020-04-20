import discord
from discord.ext import commands
import yaml
import random
from utils import get_member_name

class Bot(commands.Bot):
    def __init__(self,command_prefix):
        commands.Bot.__init__(self,command_prefix=command_prefix)
        self.teams = {"A" : [], "B" : []}
        self.ready_dict = {}
        self.nick_to_player = {}
        self.ready_dict = {}
        self.remaining = []
        self.captains = {"A" : None, "B": None}
        self.channels = {"A" : None, "B" : None}
        self.order = []
    async def set_captain(self,cap,team):
        """
        Sets captain for specified team
            :param cap: discord.Member object representing user that is now captain
            :param team: string for team name ("A" or "B")
        """
        if type(cap) == str:
            cap = self.nick_to_player[get_member_name(cap)]
        self.captains[team.upper()] = cap
        await self.add_to_team(cap,team)
        self.order.append(cap)
    async def add_to_team(self,player,team):
        """
        Adds player to team
            :param player: Discord.Member representing player member
            :param team: string representing team name
            :return discord.Embed: embed message to display
        """
        if get_member_name(player) not in self.nick_to_player.keys():
            self.nick_to_player[get_member_name(player)] = player
        if player in self.remaining:
            self.teams[team].append(player)
            self.remaining.remove(player)
            return discord.Embed(title="Valorant 10 Man Bot",description="You have drafted {}".format(get_member_name(player,lower=False)))
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
        self.ready_dict = {p : False for p in players}
        self.remaining = players.copy()
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
            #self.remaining.remove(caps[i])
        return discord.Embed(title="Valorant 10 Man Bot",
            description="The captains are @{} and @{}".format(get_member_name(caps[0],lower=False),get_member_name(caps[1],lower=False)))
    async def get_remaining(self):
        """
        Gets remaining players
        :ret: list of remaining players of type Discord.Member
        """   
        return self.remaining
    async def ready_up(self,player):
        """
        Sets status of player to ready
            :param player: discord.Member object representing player
            :return discord.Embed: embed object to display
        """   
        self.ready_dict[player] = True
        return discord.Embed(title="Valorant 10 Man Bot",description="{} is now ready".format(get_member_name(player)))
    async def move_player(self,player,channel):
        """
        Moves player to specified channel
            :param player: discord.Member object that represents player
            :param channel: discord.VoiceChannel object representing channel to move to
        """
        await player.move_to(channel)
    async def draft_player(self, captain, player, channel_dict):
        """
        Drafts a player according to 1-2-1-1-1-1-1-1-1 schema
            :param captain: discord.Member object representing captain
            :param player:  discord.Member object representing player
        """
        if (type(player) == str and get_member_name(player) not in self.nick_to_player.keys()) \
            or (type(player) == discord.Member and player not in self.nick_to_player.values()):
            return discord.Embed(title="Valorant 10 Man Bot",description="{} is not a valid player".format(player))
        elif captain not in self.captains.values():
            return discord.Embed(title="Valorant 10 Man Bot",description="{} is not a captain".format(get_member_name(captain)))
            
        player_obj = self.nick_to_player[get_member_name(player)] if type(player) == str else player
        team = "A" if captain == self.captains["A"] else "B"
        opp = "B" if team == "A" else "A"

        if len(self.teams[team]) == 0 and len(self.teams[opp]) == 0 and self.order[0] != captain:
            return discord.Embed(title="Valorant 10 Man bot",description="The other captain gets to draft first, sorry!")
        elif len(self.teams[team]) > len(self.teams[opp]):
            return discord.Embed(title="Valorant 10 Man bot",description="You've already drafted this turn, please wait for the other captain")

        embed = await self.add_to_team(player_obj, team)
        channel = channel_dict[team]
        await self.move_player(player_obj,channel)
        return embed
        