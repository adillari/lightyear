import lightbulb
import requests
import json


NASA_API_KEY = YOUR_NASA_TOKEN_HERE
APOD_URL = f'https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}'

bot = lightbulb.BotApp(
    token=YOUR_DISCORD_TOKEN_HERE,
    default_enabled_guilds=(YOUR_GUILD_IDS_HERE)
)

@bot.command
@lightbulb.command('ly', 'Lightyear')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def ly(context):
    pass

@ly.child
@lightbulb.command('apod_get', "Pass in date in MM/DD/YYYY format.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def formatted_help(context):
    await context.respond(apod_http_request())

@ly.child
@lightbulb.command('help', 'Show Lightyear options')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def formatted_help(context):
    await context.respond('Later, Ill be of help')

def apod_http_request():
    response = requests.get(APOD_URL)
    json_response = json.loads(response.text)
    photo_url = json_response['url']

    return photo_url

bot.run()