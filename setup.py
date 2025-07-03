#!/usr/bin/env python3
"""
Setup script for Design Server Discord Bot
Helps users install dependencies and configure the bot
"""

import os
import sys
import subprocess
import json

def run_command(command):
    """Run a command and return success status"""
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    if run_command("pip install -r requirements.txt"):
        print("✅ Dependencies installed successfully")
        return True
    else:
        print("❌ Failed to install dependencies")
        print("Try running: pip install -r requirements.txt manually")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = ".env"
    if os.path.exists(env_file):
        print("✅ .env file already exists")
        return True
    
    print("\n🔧 Creating .env file...")
    try:
        with open(env_file, 'w') as f:
            f.write("# Discord Bot Configuration\n")
            f.write("DISCORD_TOKEN=your_bot_token_here\n\n")
            f.write("# Optional: Override config.json settings\n")
            f.write("ORDER_ROLE_ID=1362585427621707999\n")
            f.write("TICKET_CHANNEL_ID=1390384385177554965\n")
        print("✅ .env file created")
        print("⚠️  Please edit .env file and add your bot token")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def check_config():
    """Check if bot is properly configured"""
    print("\n🔍 Checking configuration...")
    
    # Check for token
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                token = config.get('token')
        except:
            pass
    
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        print("❌ Bot token not configured")
        print("Please add your bot token to .env file or config.json")
        return False
    
    print("✅ Bot token configured")
    return True

def main():
    """Main setup function"""
    print("🎨 Design Server Discord Bot Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Create .env file
    if not create_env_file():
        return
    
    # Check configuration
    if not check_config():
        print("\n📝 Setup incomplete. Please configure your bot token and try again.")
        return
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Make sure your bot is invited to your Discord server")
    print("2. Ensure the bot has the required permissions")
    print("3. Run the bot with: python run_bot.py")
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main() 