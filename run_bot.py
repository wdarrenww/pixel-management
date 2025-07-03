#!/usr/bin/env python3
"""
Discord Bot Startup Script
Loads environment variables and starts the bot
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the bot
from main import bot

if __name__ == "__main__":
    print("Starting Design Server Discord Bot...")
    print("Make sure you have set up your bot token in config.json or DISCORD_TOKEN environment variable")
    print("Press Ctrl+C to stop the bot")
    
    try:
        bot.run(os.getenv("DISCORD_TOKEN"))
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error starting bot: {e}")
        print("Please check your configuration and try again") 