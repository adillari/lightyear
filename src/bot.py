import hikari
import lightbulb
import constants
import requests
import json
import schedule
import threading

bot = lightbulb.BotApp(
    token = constants.DISCORD_BOT_TOKEN,
    default_enabled_guilds = constants.ENABLED_GUILDS
)

@bot.listen(hikari.StartedEvent)
async def on_started(event):
    # will want to read all old jobs and restart them
    # for lines in csv, for guild, add_job(apod, 'cron',) add_job(launch)
    print('Bot has started!')

@bot.command
@lightbulb.command('ly', 'Lightyear')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def ly(context):
    pass

@ly.child
@lightbulb.command('help', 'Show Lightyear options')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def formatted_help(context):
    await context.respond('Later, Ill be of help')


# TODO: Extract these commmands out to extension folder

@ly.child
@lightbulb.option('time', 'Time in HH:MM format (24hr CST)')
@lightbulb.option('channel_id', 'ID of channel to schedule APODs')
@lightbulb.command('apod_set', 'Add APOD job to specified channel.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def schedule_embed_apod(context):
    await bot.rest.create_message(context.options.channel_id, embed_apod())

    # schedule.every().day.at(context.options.time).do(
    schedule.every(15).seconds.do(send_embed_apod, channel_id=context.options.channel_id)
    #    send_embed_apod, channel_id=context.options.channel_id
    # ) 
    schedule.run_pending()
    await context.respond(
        f'APOD job added to {context.options.channel_id} daily at {context.options.time}.'
    )

@ly.child
@lightbulb.option('date', 'Date in YYYY-MM-DD format(Defaults to today)', required=False)
@lightbulb.command('apod_get', 'Pass in date in MM/DD/YYYY format')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def apod_get(context):
    await context.respond(embed_apod(context.options.date))

async def send_embed_apod(channel_id):
    await bot.rest.create_message(channel_id, embed=embed_apod())

def embed_apod(date=None):
    apod_json = apod_http_request(date)
    embed = hikari.Embed(
        title = apod_json['title'],
        description = apod_json['explanation']
    )
    embed.set_image(apod_json['url'])
    
    return embed

def apod_http_request(date):
    apod_url = constants.APOD_URL
    if date is not None:
        apod_url = f'{apod_url}&date={date}'

    print(apod_url)
    response = requests.get(apod_url)
    json_response = json.loads(response.text)

    return json_response

# bot.load_extensions_from('./extensions')
bot.run()
