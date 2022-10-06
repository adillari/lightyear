import hikari
import lightbulb
import constants
import requests
import json
from hikari.colors import Color
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore

bot = lightbulb.BotApp(
    token = constants.DISCORD_BOT_TOKEN,
    default_enabled_guilds = constants.ENABLED_GUILDS
)
scheduler = AsyncIOScheduler(jobstores={'mongo': MongoDBJobStore()})

@bot.listen(hikari.StartedEvent)
async def on_started(event):
    scheduler.start()
    print('Lightyear has started!')

@bot.command
@lightbulb.option('date', 'Date in YYYY-MM-DD format(Defaults to today)', required=False)
@lightbulb.command('apod', 'Get embed APOD card')
@lightbulb.implements(lightbulb.SlashCommand)
async def apod_get(ctx):
    pending = await ctx.respond('Fetching your APOD!')
    await send_embed_apod(ctx.channel_id, ctx.options.date)
    await pending.delete()

@bot.command
@lightbulb.option('date', 'Date in YYYY-MM-DD format(Defaults to today)', required=False)
@lightbulb.command('apod_json', 'Retrieve raw JSON data for an APOD')
@lightbulb.implements(lightbulb.SlashCommand)
async def apod_json(ctx):
    pretty_json = json.dumps(apod_http_request(ctx.options.date), indent=2)
    await ctx.respond(f'```{pretty_json}```')

@bot.command
@lightbulb.option('channel_id', 'Channel to remove job from')
@lightbulb.command('apod_remove', 'Remove scheduled APOD job')
@lightbulb.implements(lightbulb.SlashCommand)
async def apod_remove(ctx):
    job_id = f'{ctx.guild_id}:{ctx.options.channel_id}'

    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        await ctx.respond('Job removed successfully')
    else:
        await ctx.respond('Invalid channel id')


@bot.command
@lightbulb.command('show_jobs', 'Show running APOD jobs')
@lightbulb.implements(lightbulb.SlashCommand)
async def show_jobs(ctx):
    jobs = scheduler.get_jobs(jobstore='mongo')
    await ctx.respond(jobs)

@bot.command
@lightbulb.option('time', 'Time in HH:MM format (24hr CST)')
@lightbulb.option('channel_id', 'ID of channel to schedule APODs')
@lightbulb.command('apod_set', 'Add scheduled APOD job to specified channel.')
@lightbulb.implements(lightbulb.SlashCommand)
async def schedule_embed_apod(ctx):
    time = ctx.options.time.split(':')
    hour = time[0]
    minute = time[1]

    job_id = f'{ctx.guild_id}:{ctx.options.channel_id}'
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        
    scheduler.add_job(
        send_embed_apod,
        trigger='cron',
        args=[ctx.options.channel_id],
        hour=hour,
        minute=minute,
        jobstore='mongo',
        id=job_id
    )
    
    await ctx.respond(
        f'APOD job added to {ctx.options.channel_id} daily at {ctx.options.time}.'
    )
 
async def send_embed_apod(channel_id, date=None):
    apod = embed_apod(date)
    
    if apod['extras']:
        await bot.rest.create_message(channel_id, apod['extras'])
    
    await bot.rest.create_message(channel_id, embed=apod['embed'])

def embed_apod(date):
    json = apod_http_request(date)
    extras = None
    embed = hikari.Embed(
        title = json['title'],
        description = json['explanation'],
        color = hikari.Color(0xff2e65)
    )

    match json['media_type']:
        case 'image':
            if 'hdurl' in json:
                embed.set_image(json['hdurl'])
            else:
                embed.set_image(json['url'])
        case 'video':
            if 'youtube' in json['url']:
                extras = f"https://www.youtube.com/watch?v={json['url'][30:]}"
            else:
                extras = json['url'] 
        case _:
            extras = f"New API behavior. Log for future: media_type = {json['media_type']}"

    footer = f"APOD for {json['date']}"
    if 'copyright' in json:
        footer += f" • {json['media_type'].capitalize()} by {json['copyright']}"

    embed.set_footer(footer)
    
    return { 'embed': embed, 'extras': extras }

def apod_http_request(date):
    apod_url = constants.APOD_URL
    if date:
        apod_url = f'{apod_url}&date={date}'

    response = requests.get(apod_url)
    json_response = json.loads(response.text)

    return json_response

bot.run()
