import asyncio
from canvasapi import Canvas
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# Setup ENV vars
load_dotenv()
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CANVAS_URL = os.getenv("CANVAS_API_URL")
CANVAS_TOKEN = os.getenv("CANVAS_API_TOKEN")

assert BOT_TOKEN is not None
assert CANVAS_URL is not None
assert CANVAS_TOKEN is not None

# Create a Canvas instance
canvas = Canvas(CANVAS_URL, CANVAS_TOKEN)

# Instantiate an intents object that our bot client will use.
# Intents are data that the bot can access when in a server such as message history or 
bot_intents = discord.Intents.default()

# Create a Discord bot instance.
# discord.commands.Bot is a subclass of discord.Client
bot = commands.Bot(command_prefix='^', intents=bot_intents, help_command=None)


# Embed utility function to create and format and return an embedded message object, rather than using a plain text message
def createMessageEmbed(title: str, description: str): 
    return discord.Embed(
        title=title,
        description=description,
        color=discord.Color.blue(),
    )


# Utility Function to GET and return all Canvas courses the user is enrolled in
def get_canvas_courses():
    global canvas
    user = canvas.get_current_user()
    course_list = []
    for course in user.get_courses(enrollment_state="active"):
        course_list.append(f"{course.name} ({course.id})")
    return "\n".join(course_list)


# Utility function to GET and return all Canvas assignments the user is enrolled in,
# given an arguement of the course ID
def get_canvas_assignments(course_id):
    global canvas
    course = canvas.get_course(course_id)
    assignments = []
    for assignment in course.get_assignments():
        assignments.append(f"{assignment} DUE AT - {assignment.due_at}")
    return "\n".join(assignments)


# Application (or Slash Command) that the bot will respond
# with all Canvas courses the user is enrolled in
# and their respective course ID
@bot.tree.command(
    name="canvas-courses", description="Get Canvas courses from this user."
)
async def canvas_courses(interaction: discord.Interaction):
    try:
        courses = get_canvas_courses()
        await interaction.response.send_message(
            embed=createMessageEmbed(
                title="Available Canvas Courses", description=courses
            ),
            ephemeral=True,
        )
    except Exception as e:
        await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)


# Application (or Slash Command) that the bot will respond
# with all Canvas assignemnts for a course the user is enrolled in
# given an arguement for the respective course ID
@bot.tree.command(
    name="canvas-assignments", description="Get Canvas assignments for a course."
)
async def canvas_assignments(interaction: discord.Interaction, course_id: int):
    try:
        assignments = get_canvas_assignments(course_id)
        await interaction.response.send_message(
            embed=createMessageEmbed(
                title='Canvas', 
                description=assignments)
            )
    
    except Exception as e:
        await interaction.response.send_message('Error')


# Setup event when the bot's cache has been fully loaded and is ready for all command use
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        # Sync the command tree to ensure slash commands are registered
        commandtree = await bot.tree.sync()
        print(f"Synced {len(commandtree)} application command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")


async def main() -> None:
    # Run other async tasks
    # Use async task groups to do multiple tasks at a single time for easy parallel processing
    # https://docs.python.org/3/library/asyncio-task.html#task-groups

    # Start the bot
    try:
        async with bot:
            await bot.start(BOT_TOKEN)
    except:
        print("Invalid Token")
        exit(1)

asyncio.run(main())
