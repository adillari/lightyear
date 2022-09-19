import hikari
import lightbulb
import requests
import json
import constants

plugin = lightbulb.Plugin('APOD')

# @plugin.command
@ly.child
@lightbulb.command('apod_get', "Pass in date in MM/DD/YYYY format.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def formatted_help(context):
    await context.respond(apod_http_request())

def apod_http_request():
    response = requests.get(constants.APOD_URL)
    json_response = json.loads(response.text)
    photo_url = json_response['url']

    return photo_url

def load(bot):
    bot.add_plugin(plugin)
