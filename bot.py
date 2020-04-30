from collections import Counter
import discord
from discord.ext import commands
import yaml
import random
from datetime import datetime

from utils import get_member_name, prettify
from converters import Player

TIME_THRESOLD = 1.5 # number of hours cutoff to check previous players when choosing captains
SECS_TO_HOURS = 60**2

class Bot(commands.Bot):
    def __init__(self,command_prefix, drafting_scheme, maps, blacklist):
        """
        Constructor for Bot
            :param command_prefix: symbol to type before command. For ex, use "!" if you want to use "!<command>"
            :param drafting_scheme: list contains strings of format "<A/B><1-2>" where first char is team and 2nd char is # players
            :param maps: list of strings where each string corresponds to a map name
        """   
        commands.Bot.__init__(self,command_prefix=command_prefix)
        self.teams = {"A" : [], "B" : []}
        self.remaining = []
        self.captains = {"A" : None, "B": None}
        self.channels = {"A" : None, "B" : None}
        self.order = []
        self.blacklist = [get_member_name(f) for f in blacklist]
        self.previous_players = []
        self.previous_captains = {}
        self.previous_time = None
        self.drafting_dict = {"A" : [int(s[1]) for s in drafting_scheme if s[0] == "A"],
                              "B" : [int(s[1]) for s in drafting_scheme if s[0] == "B"]}
        self.turn = -1
        self.map_dict = {k.lower() : True for k in maps}
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
    async def get_team_embed(self):
        """
        Generates an embed for the chosen teams
        """
        embed = discord.Embed(title="Valorant 10 Man Bot",colour=discord.Colour(0x470386))
        team_a_strings = [get_member_name(m,lower=False) for m in self.teams["A"]]
        team_b_strings = [get_member_name(m,lower=False) for m in self.teams["B"]]   
        embed.add_field(name="Defenders", value="{}".format("\n".join(team_a_strings)), inline=True)
        embed.add_field(name="Attackers", value="{}".format("\n".join(team_b_strings)), inline=True)
        return embed
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
        self.previous_captains = self.captains
        self.captains = {"A" : None, "B" : None}
        self.nick_to_player = {get_member_name(p) : p for p in players}
        self.previous_players = self.remaining
        self.remaining = players.copy()
        self.turn = 1
        self.order = []
        self.map_dict = {k : True for k in self.map_dict.keys()}
        return discord.Embed(title="Valorant 10 Man Bot",
            description="New game started".format(len(players)))

    async def get_remaining_map_string(self):
        embed_string = ""
        num_available = 1
        for m in self.map_dict.keys():
                if self.map_dict[m]:
                    pretty = prettify(m)
                    embed_string += "{}. {}\n".format(num_available,pretty)
                    num_available += 1
        return embed_string

    async def ban_map(self, map_to_ban : str, caller : Player):
        """
        Remove map from pool
            :param map_to_ban: str that represents map to ban
            :param caller: discord.Member object that represents who called the command
        """   
        if caller not in self.captains.values():
            return discord.Embed(title="Valorant 10 Man Bot", description="Only captains can ban maps")
        map_to_ban = map_to_ban[0].upper() + map_to_ban[1:].lower()

        if map_to_ban.lower() in self.map_dict.keys() and self.map_dict[map_to_ban.lower()] == True:
            self.map_dict[map_to_ban.lower()] = False
            counter = Counter(self.map_dict.values())
            embed_string = ""

            if counter[False] == len(self.map_dict.keys()) - 1: # one map remaining
                embed_string = "The match will be played on {}".format(next((prettify(k) for k in self.map_dict.keys() if self.map_dict[k]), None))
            else:
                embed_string = f"{map_to_ban} has been banned\n\n The remaining maps are\n\n" + await self.get_remaining_map_string()
            return discord.Embed(title="Valorant 10 Man Bot", description=embed_string)

        elif map_to_ban.lower() not in self.map_dict.keys():
            return discord.Embed(title="Valorant 10 Man Bot", description=f"{map_to_ban} is not a valid map")

        elif not self.map_dict[map_to_ban.lower()]:
            return discord.Embed(title="Valorant 10 Man Bot", 
                                 description=f"{map_to_ban} is already banned. The remaining maps are:\n"+ await self.get_remaining_map_string()) 
    async def generate_captains(self,team_a_channel, team_b_channel):
        """
        Generates two new captains and sets them as captains
            :ret discord.Embed: embed object to display 
        """
        if len(self.remaining) != 10:
            return discord.Embed(title="Valorant 10 Man Bot",
                description="Please use the command !new and ensure you have 10 players in the channel before selecting captains")
        potential = []
        check_prev = self.previous_time and (datetime.now() - self.previous_time).seconds / SECS_TO_HOURS <= TIME_THRESOLD #seconds to hours conversion
        for p in self.remaining:
            was_captain = p in self.previous_captains.values()
            was_in_previous = not check_prev or (check_prev and p in self.previous_players)
            blacklisted = get_member_name(p) in self.blacklist
            if not was_captain and was_in_previous and not blacklisted:
                potential.append(p)

        caps = random.sample(potential, 2) # 2 captains

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
        if len(self.remaining) == 0:
            embed = await self.get_team_embed()
            self.previous_time = datetime.now()
        channel = channel_dict[team]
        await self.move_player(player,channel)

        if team == "B" and len(self.teams[team]) == sum(self.drafting_dict[team][:self.turn]) + 1: # + 1 to include captain
            self.turn += 1

        return embed