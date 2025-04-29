import discord
from discord.ext import commands
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

# Google Sheets API setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

sheet = client.open("HabitTracker")  # change if your sheet has a different name
habits_sheet = sheet.worksheet("Habits")
log_sheet = sheet.worksheet("Log")

# === Discord Bot Setup ===
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# === Command: !habit done HabitName ===
@bot.command()
async def habit(ctx, action=None, *, habit_name=None):
    username = str(ctx.author.name)

    if action == "done" and habit_name:
        today = datetime.now().strftime("%Y-%m-%d")

        # Check if user has this habit
        habits = habits_sheet.get_all_records()
        user_habits = [h["Habit"] for h in habits if h["User"] == username]

        if habit_name not in user_habits:
            await ctx.send(f"You don't have a habit named **{habit_name}**.")
            return

        # Add to Log sheet
        log_sheet.append_row([today, username, habit_name])
        await ctx.send(f"✅ Marked **{habit_name}** as done today!")

    else:
        await ctx.send("Usage: `!habit done HabitName`")

# === Run Bot ===
bot.run("MTM2Njc2NjM0MTUzNjYxNjYwMQ.GLMBgV.Kdqre_Vi2987XHMPKKEr5ppMApzU5aLgs64LwM")
