# 10 Man Bot
This is a bot that facilitates a 10 man lobby (for Valorant or other games) with auto moving features.

It requires a config.yaml file with the fields `team_a`, `team_b`,`lobby`, `scheme`, and `maps`, which signify the channel names for each team, drafting scheme, and map pool.

You must also save your Discord Bot API key in the `DISCORD_KEY` environment variable.

## Installation

Verify that you have Python 3.7 or later and run the following

```python3.7 -m pip install -r requirements.txt```

and then run the bot with

```python3.7 main.py```
