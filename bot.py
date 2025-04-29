import discord
from discord.ext import commands
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
BOT_TOKEN = os.getenv("TOKEN")

# Google Sheets API setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

sheet = client.open("HabitTracker")  # Change if your sheet has a different name
habits_sheet = sheet.worksheet("Habits")
log_sheet = sheet.worksheet("Log")

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def habit(ctx, action=None, *, habit_name=None):
    username = str(ctx.author.name)

    if action == "done" and habit_name:
        today = datetime.now().strftime("%Y-%m-%d")
        habits = habits_sheet.get_all_records()
        user_habits = [h["Habit"] for h in habits if h["User"] == username]

        if habit_name not in user_habits:
            await ctx.send(f"You don't have a habit named **{habit_name}**.")
            return

        log_sheet.append_row([today, username, habit_name])
        await ctx.send(f"✅ Marked **{habit_name}** as done today!")

    elif action == "add" and habit_name:
        habits = habits_sheet.get_all_records()
        for habit in habits:
            if habit["User"] == username and habit["Habit"].lower() == habit_name.lower():
                await ctx.send("This habit already exists.")
                return
        habits_sheet.append_row([username, habit_name])
        await ctx.send(f"➕ Added new habit **{habit_name}**.")

    elif action == "delete" and habit_name:
        cell = habits_sheet.find(habit_name)
        row = cell.row
        record = habits_sheet.row_values(row)
        if record[0] != username:
            await ctx.send("You can only delete your own habits.")
            return
        habits_sheet.delete_rows(row)
        await ctx.send(f"🗑️ Deleted habit **{habit_name}**.")

    elif action == "list":
        habits = habits_sheet.get_all_records()
        user_habits = [h["Habit"] for h in habits if h["User"] == username]
        if not user_habits:
            await ctx.send("You have no habits tracked yet.")
        else:
            await ctx.send(f"📋 Your habits:\n" + "\n".join(f"- {h}" for h in user_habits))

    elif action == "report":
        logs = log_sheet.get_all_records()
        user_logs = [log for log in logs if log["User"] == username]
        if not user_logs:
            await ctx.send("You have no completed habits yet.")
        else:
            summary = {}
            for log in user_logs:
                habit = log["Habit"]
                summary[habit] = summary.get(habit, 0) + 1
            report_lines = [f"**{habit}**: {count} day(s)" for habit, count in summary.items()]
            await ctx.send("📊 Habit Report:\n" + "\n".join(report_lines))

    else:
        await ctx.send(
            "Usage:\n"
            "`!habit add HabitName`\n"
            "`!habit delete HabitName`\n"
            "`!habit done HabitName`\n"
            "`!habit list`\n"
            "`!habit report`"
        )

# Run Bot
bot.run("" + BOT_TOKEN)
