# 10 Man Bot
This is a bot that facilitates a 10 man lobby (for Valorant or other games) with auto moving features.

It requires a config.yaml file with the fields `team_a`, `team_b`,`lobby`, `scheme`, and `maps`, which signify the channel names for each team, drafting scheme, and map pool.

You must also save your Discord Bot API key in the `DISCORD_KEY` environment variable.

## Installation

Verify that you have Python 3.7 or later and run the following

```python -m pip install -r requirements.txt```

and then run the bot with

```python main.py```

## Setup

If you would like to prevent any user from being captain, simply add their name to `blacklist.txt`.

You should configure the maps and channel names in config.yaml if the provided ones do not match your channel setup.

## Commands

`!help` : Lists all commands

`!new`  : Starts new game, but does not select captain

`!nc`    : Starts new game and selects captains

`!setcaps @<cap1> @<cap2>` : Manually sets the captains to specified users

`!ban <map_name>` : Bans provided map from map pool

`!draft @<player_name>` : Drafts user to your team (you must be captain to use this command)
