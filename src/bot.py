import hikari
import lightbulb
import constants
import requests
import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from hikari.colors import Color

scheduler = AsyncIOScheduler()
scheduler.start()

bot = lightbulb.BotApp(
    token = constants.DISCORD_BOT_TOKEN,
    default_enabled_guilds = constants.ENABLED_GUILDS
)

@bot.listen(hikari.StartedEvent)
async def on_started(event):
    # todo: restart jobs in store
    print('Lightyear has started!')

@bot.command
@lightbulb.option('date', 'Date in YYYY-MM-DD format(Defaults to today)', required=False)
@lightbulb.command('apod', 'Get embed APOD card')
@lightbulb.implements(lightbulb.SlashCommand)
async def apod_get(context):
    await context.respond(embed_apod(context.options.date))

@bot.command
@lightbulb.option('date', 'Date in YYYY-MM-DD format(Defaults to today)', required=False)
@lightbulb.command('apod_json', 'Retrieve raw JSON data for an APOD')
@lightbulb.implements(lightbulb.SlashCommand)
async def apod_json(context):
    pretty_json = json.dumps(apod_http_request(context.options.date), indent=2)
    await context.respond(f'```{pretty_json}```')

@bot.command
@lightbulb.option('time', 'Time in HH:MM format (24hr CST)')
@lightbulb.option('channel_id', 'ID of channel to schedule APODs')
@lightbulb.command('apod_set', 'Add scheduled APOD job to specified channel.')
@lightbulb.implements(lightbulb.SlashCommand)
async def schedule_embed_apod(context):
    time = context.options.time.split(':')
    hour = time[0]
    minute = time[1]

    scheduler.add_job(
        send_embed_apod,
        trigger='cron',
        args=[context.options.channel_id],
        hour=hour,
        minute=minute,
        id=f'apod_{context.options.channel_id}'
    )
    
    await context.respond(
        f'APOD job added to {context.options.channel_id} daily at {context.options.time}.'
    )

async def send_embed_apod(channel_id):
    await bot.rest.create_message(channel_id, embed=embed_apod())

def embed_apod(date=None):
    apod_json = apod_http_request(date)
    embed = hikari.Embed(
        title = apod_json['title'],
        description = apod_json['explanation'],
        color = hikari.Color(0xff2e65)
    )
    embed.set_image(apod_json['url'])
    embed.set_footer(f"APOD for {apod_json['date']}")
    
    return embed

def apod_http_request(date):
    apod_url = constants.APOD_URL
    if date is not None:
        apod_url = f'{apod_url}&date={date}'

    print(apod_url)
    response = requests.get(apod_url)
    json_response = json.loads(response.text)
    print(json_response)

    return json_response

bot.run()
