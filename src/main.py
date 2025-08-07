import discord
from discord.ext import commands
import asyncio
import json
import os
import random
from datetime import datetime, timedelta
from discord import app_commands
import math

# Global variables for order status management
order_status_message_id = None
order_status_data = {
    "Logo Design": "open",
    "Clothing Design": "open",
    "Livery": "open",
    "ELS": "open",
    "Banner and Graphics": "open",
    "Full Discord Server Design": "open",
    "Professional Photography": "open"
}

# Configuration constants
ORDER_ROLE_ID = 1362585427621707999
TICKET_CHANNEL_ID = 1362585428510642325
CLAIM_ROLE_ID = 1362585427168592018
CLOSE_ROLE_ID = 1362585427550146618
MANAGER_ROLE_ID = 1362585427550146618
LOGGING_CHANNEL_ID = 1362585429706019031
PAYMENT_LOG_CHANNEL_ID = 1390420651504042115
WELCOME_CHANNEL_ID = 1362585428850638903
REVIEW_CHANNEL_ID = 1362585428850638900
REVIEW_ROLE_ID = 1391506674896080926

# Support system constants
SUPPORT_ROLE_ID = 1362585427168592022
EXECUTIVE_ROLE_ID = 1362585427621707999
HIGH_RANK_ROLE_ID = 1362585427550146618
SUPPORT_GENERAL_CATEGORY_ID = 1362585430024781936
SUPPORT_HIGH_RANK_CATEGORY_ID = 1362585430024781937
EXECUTIVE_CHANNEL_ID = 1362585430024781938

# Package claim system constants
PACKAGE_CLAIM_CHANNEL_ID = 1396080308381683815
PACKAGE_CLAIM_CATEGORY_ID = 1396130790114590851
PACKAGE_CLAIM_ENABLED = True  # Global flag to control package claim availability

# Consolidated role lists
MANAGER_ROLE_IDS = [
    1362585427621707999,  # Original ORDER_ROLE_ID
    1362585427621707998,  # Original ADDITIONAL_ROLE_IDS[2]
    1362585427550146618,  # Original MANAGER_ROLE_ID
    1362585427550146617,  # New manager role
    1362585427550146616,  # New manager role
    1362585427550146615   # New manager role
]

DESIGNER_ROLE_IDS = [
    1362585427168592018,  # Original CLAIM_ROLE_ID
    1362585427168592017,  # New designer role
    1362585427168592016,  # New designer role
    1362585427168592015,  # New designer role
    1362585427135168653,  # New designer role
    1362585427135168652   # New designer role
]

SUPPORT_ROLE_IDS = [
    1362585427168592022,  # Support role
]

EXECUTIVE_ROLE_IDS = [
    1362585427621707999,  # Executive role
]

HIGH_RANK_ROLE_IDS = [
    1362585427550146618,  # High rank role
    1389024033408024647,  # Manager role
]

# Store order details for payment logging
order_details = {}  # channel_id -> {designer, customer, products, price, completion_time}

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='-', intents=intents)

# Slash command choices
service_choices = [
    app_commands.Choice(name="Logo Design", value="Logo Design"),
    app_commands.Choice(name="Clothing Design", value="Clothing Design"),
    app_commands.Choice(name="Livery", value="Livery"),
    app_commands.Choice(name="ELS", value="ELS"),
    app_commands.Choice(name="Banner and Graphics", value="Banner and Graphics"),
    app_commands.Choice(name="Full Discord Server Design", value="Full Discord Server Design"),
    app_commands.Choice(name="Professional Photography", value="Professional Photography")
]

status_choices = [
    app_commands.Choice(name="Open", value="open"),
    app_commands.Choice(name="Delayed", value="delayed"),
    app_commands.Choice(name="Closed", value="closed")
]

completion_time_choices = [
    app_commands.Choice(name="1-2 days", value="1-2 days"),
    app_commands.Choice(name="3-4 days", value="3-4 days"),
    app_commands.Choice(name="1 week", value="1 week"),
    app_commands.Choice(name="1-2 weeks", value="1-2 weeks"),
    app_commands.Choice(name="2-3 weeks", value="2-3 weeks"),
    app_commands.Choice(name="1 month", value="1 month"),
    app_commands.Choice(name="Custom", value="custom")
]

rating_choices = [
    app_commands.Choice(name="1 Star", value=1),
    app_commands.Choice(name="2 Stars", value=2),
    app_commands.Choice(name="3 Stars", value=3),
    app_commands.Choice(name="4 Stars", value=4),
    app_commands.Choice(name="5 Stars", value=5)
]

# Category IDs for different service types
CATEGORY_IDS = {
    "Clothing Design": 1362585429227995179,
    "Livery": 1362585429227995178,
    "Banner and Graphics": 1362585429227995180,
    "Logo Design": 1362585429227995180,  # Same as Banner and Graphics
    "Full Discord Server Design": 1362585429227995181,
    "Professional Photography": 1362585429227995180,  # Same as Banner and Graphics
    "ELS": 1380555774429888644
}

# Design ticket category IDs (for -de command)
DESIGN_CATEGORY_IDS = [
    1362585429227995179,  # Clothing Design
    1362585429227995178,  # Livery
    1362585429227995180,  # Banner and Graphics
    1362585429227995181,  # Full Discord Server Design
    1380555774429888644   # ELS
]

# Designer role pings for different services
DESIGNER_ROLE_PINGS = {
    "Clothing Design": 1362585427093229718,  # clothing
    "Livery": 1362585427135168644,           # livery
    "Banner and Graphics": 1362585427093229717,  # graphic
    "Logo Design": 1362585427093229717,      # graphic (same as banner and graphics)
    "Full Discord Server Design": 1362585427093229716,  # discord servers/layouts
    "Professional Photography": 1379672017711661066,  # photography
    "ELS": 1362585427093229715               # els
}

class ServiceSelectionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Remove timeout for persistence
        # Add the service selection dropdown
        self.add_item(ServiceSelect())
    
    custom_id = "service_selection_view"

class ServiceSelect(discord.ui.Select):
    def __init__(self):
        # Create options for the dropdown
        options = []
        
        # Define all services with their status - using exact names from order_status_data
        services = [
            ("Logo Design", "logo_design", "🎨 Professional logo creation"),
            ("Clothing Design", "clothing_design", "👕 Complete uniform designs"),
            ("Livery", "livery", "🚗 Vehicle livery designs"),
            ("ELS", "els", "🚨 Emergency lighting systems"),
            ("Banner and Graphics", "banner_graphics", "🖼️ Banner and graphic designs"),
            ("Full Discord Server Design", "discord_layout", "💬 Full Discord server design"),
            ("Professional Photography", "photography", "📸 Professional photography")
        ]
        
        for service_name, service_id, description in services:
            # Check if service is closed
            status = order_status_data.get(service_name, "open")
            if status == "closed":
                options.append(
                    discord.SelectOption(
                        label=f"{service_name} (Closed)",
                        description=f"{description} - Currently unavailable",
                        value=service_id,
                        emoji="🔒",
                        default=False
                    )
                )
            else:
                emoji = "✅" if status == "open" else "⚠️"
                options.append(
                    discord.SelectOption(
                        label=service_name,
                        description=description,
                        value=service_id,
                        emoji=emoji,
                        default=False
                    )
                )
        
        super().__init__(
            placeholder="Select a service...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="service_select"
        )
    
    async def callback(self, interaction: discord.Interaction):
        try:
            # Map the selected value to service name - using exact names from order_status_data
            service_mapping = {
                "logo_design": "Logo Design",
                "clothing_design": "Clothing Design",
                "livery": "Livery",
                "els": "ELS",
                "banner_graphics": "Banner and Graphics",
                "discord_layout": "Full Discord Server Design",
                "photography": "Professional Photography"
            }
            
            selected_service = service_mapping.get(self.values[0])
            
            if not selected_service:
                await interaction.response.send_message("Invalid service selected.", ephemeral=True)
                return
            
            # Check if service is closed
            if order_status_data.get(selected_service, "open") == "closed":
                embed = discord.Embed(
                    title="Service Temporarily Unavailable",
                    description=(
                        f"We apologize, but **{selected_service}** is currently closed for new orders.\n\n"
                        f"**Why is this service closed?**\n"
                        f"• We may be at full capacity for this service type\n"
                        f"• Our team is focusing on existing orders\n"
                        f"• We're temporarily restructuring our workflow\n\n"
                        f"**What can you do?**\n"
                        f"• Check back later for availability updates\n"
                        f"• Consider our other available services\n"
                        f"• Contact our team for custom arrangements\n\n"
                        f"Thank you for your understanding! 🙏"
                    ),
                    color=0x8E6B6B,
                    timestamp=datetime.utcnow()
                )
                embed.set_footer(text=".pixel Design Services • We'll be back soon!")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Create the ticket
            await self.create_ticket(interaction, selected_service)
        except Exception as e:
            print(f"Error in ServiceSelect callback: {e}")
            await interaction.response.send_message("An error occurred while processing your selection. Please try again.", ephemeral=True)
    
    async def create_ticket(self, interaction: discord.Interaction, service_type: str):
        try:
            guild = interaction.guild
            user = interaction.user
            
            # Check if user already has an open ticket
            existing_unclaimed = discord.utils.get(guild.channels, name=f"unclaimed-{user.name.lower()}")
            existing_claimed = discord.utils.get(guild.channels, name=f"claimed-{user.name.lower()}")
            existing_finished = discord.utils.get(guild.channels, name=f"finished-{user.name.lower()}")
            
            if existing_unclaimed or existing_claimed or existing_finished:
                existing_ticket = existing_unclaimed or existing_claimed or existing_finished
                await interaction.response.send_message(
                    f"You already have an open ticket: {existing_ticket.mention}",
                    ephemeral=True
                )
                return
            
            # Get category
            category_id = CATEGORY_IDS.get(service_type)
            if not category_id:
                await interaction.response.send_message("Error: Category not found for this service.", ephemeral=True)
                return
            category = guild.get_channel(category_id)
            if not category:
                await interaction.response.send_message("Error: Category not found.", ephemeral=True)
                return
            
            # Create ticket channel
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
            }
            order_role = guild.get_role(ORDER_ROLE_ID)
            if order_role:
                overwrites[order_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            ticket_channel = await guild.create_text_channel(
                f"unclaimed-{user.name}",
                category=category,
                overwrites=overwrites,
                topic=f"{service_type} order ticket for {user.mention}"
            )
            await self.send_welcome_message(ticket_channel, user, service_type)
            await interaction.response.send_message(
                f"Your {service_type} ticket has been created: {ticket_channel.mention}!",
                ephemeral=True
            )
        except Exception as e:
            print(f"Error creating ticket: {e}")
            await interaction.response.send_message("An error occurred while creating your ticket. Please try again or contact support.", ephemeral=True)

    async def send_welcome_message(self, channel, user, service_type):
        try:
            banner_urls = {
                "Logo Design": "https://media.discordapp.net/attachments/1103870377211465818/1390404759684518020/pixelgraphics.png?ex=686822d7&is=6866d157&hm=fd9fb49a7196bad292b54329022df2526a958d4d04a0c44cf1241f1141a7af0a&=&format=webp&quality=lossless&width=2050&height=684",
                "Clothing Design": "https://cdn.discordapp.com/attachments/1103870377211465818/1390404812062855441/pixelclothing.png?ex=686822e3&is=6866d163&hm=db3b2c0ed0041dfd253c525f366221c2df9a40707d6621b2d71b694d268e2f6d&",
                "Livery": "https://media.discordapp.net/attachments/1103870377211465818/1390404760003416135/pixelliveries.png?ex=686822d7&is=6866d157&hm=eb1fda01e9743ef2f5ab19571c3920d10d55687b11a54bde21bc2584d85f5e58&=&format=webp&quality=lossless&width=2050&height=684",
                "ELS": "https://media.discordapp.net/attachments/1103870377211465818/1390404759391043765/pixelels.png?ex=686822d7&is=6866d157&hm=66f156b4b222235c543ba34ff531dbb86f6c5cc7f8daa0ea8127a6d9dd4dce89&=&format=webp&quality=lossless&width=2050&height=684",
                "Banner and Graphics": "https://media.discordapp.net/attachments/1103870377211465818/1390404759684518020/pixelgraphics.png?ex=686822d7&is=6866d157&hm=fd9fb49a7196bad292b54329022df2526a958d4d04a0c44cf1241f1141a7af0a&=&format=webp&quality=lossless&width=2050&height=684",
                "Full Discord Server Design": "https://media.discordapp.net/attachments/1103870377211465818/1390404812373495979/pixeldiscord.png?ex=686822e3&is=6866d163&hm=78d99a12f6715acb0faea5d36d249ff0a96d93cf83b2ec96501202cead3b46dd&=&format=webp&quality=lossless&width=2050&height=684",
                "Professional Photography": "https://media.discordapp.net/attachments/1103870377211465818/1390404846238044262/pixelphotos.png?ex=686822eb&is=6866d16b&hm=5fbdd76fe7dad1d586572a80362f61488a670be7301b9681ddfb0651d5fcaddc&=&format=webp&quality=lossless&width=2050&height=684"
            }
            banner_url = banner_urls.get(service_type, "https://example.com/default_banner.png")
            
            # Get designer role ping
            designer_role_id = DESIGNER_ROLE_PINGS.get(service_type)
            designer_role_mention = ""
            if designer_role_id:
                designer_role = channel.guild.get_role(designer_role_id)
                if designer_role:
                    designer_role_mention = designer_role.mention
            
            embed = discord.Embed(
                title=f"Welcome to your custom {service_type} order ticket!",
                description=(
                    f"Thank you for choosing .pixel, {user.mention}! 🎨\n\n"
                    f"We're excited to bring your vision to life with our professional {service_type.lower()} services.\n\n"
                    f"**To start, please fill out the form below and provide these details:**\n\n"
                    f"**📋 Type:** (e.g., PD for liveries, server logo for graphics)\n"
                    f"**🎨 Customizations:** Detailed description including colors, style preferences, and specific requirements\n"
                    f"**📸 Reference(s):** Any images or examples that inspire your vision\n"
                    f"**💰 Budget Range:** (Optional) Your preferred budget range\n\n"
                    f"**Please reply with these details to begin your order process!**\n\n"
                    f"Our team will review your requirements and get back to you shortly."
                ),
                color=0x1B75BD,
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=f".pixel Design Services • Professional Quality • Ticket ID: {channel.id}")
            
            # Add banner as embed image if available
            if banner_url != "https://example.com/default_banner.png":
                embed.set_image(url=banner_url)
            
            # Create ticket management view
            ticket_view = TicketManagementView()
            
            # Send pings first
            ping_message = f"Hey {user.mention}"
            if designer_role_mention:
                ping_message += f", {designer_role_mention} will be with you soon!"
            else:
                ping_message += ", our team will be with you soon!"
            
            await channel.send(ping_message)
            
            # Send embed with banner and management buttons
            await channel.send(embed=embed, view=ticket_view)
            
            # Log ticket creation
            await self.log_ticket_creation(channel, user, service_type)
        except Exception as e:
            print(f"Error sending welcome message: {e}")
            # Try to send a simple message if the embed fails
            try:
                await channel.send(f"Welcome {user.mention}! Please provide your order details.")
            except:
                pass
    
    async def log_ticket_creation(self, channel, user, service_type):
        """Log ticket creation to the logging channel"""
        try:
            logging_channel = channel.guild.get_channel(LOGGING_CHANNEL_ID)
            if logging_channel:
                embed = discord.Embed(
                    title="🎫 New Ticket Created",
                    description=f"A new ticket has been created for {service_type}",
                    color=0x6B8E6B,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="User", value=f"{user.mention} ({user.name})", inline=True)
                embed.add_field(name="Service", value=service_type, inline=True)
                embed.add_field(name="Channel", value=channel.mention, inline=True)
                embed.add_field(name="Status", value="🟡 Unclaimed", inline=True)
                embed.set_footer(text=f"Ticket ID: {channel.id}")
                
                await logging_channel.send(embed=embed)
        except Exception as e:
            print(f"Error logging ticket creation: {e}")
            # Don't fail the main interaction if logging fails

class TicketManagementView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Claim Ticket", style=discord.ButtonStyle.success, custom_id="claim_ticket")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has designer role
        if not has_designer_role(interaction.user):
            await interaction.response.send_message("You don't have permission to claim tickets.", ephemeral=True)
            return
        
        channel = interaction.channel
        
        # Check if ticket is already claimed
        if channel.name.startswith("claimed-"):
            await interaction.response.send_message("This ticket has already been claimed.", ephemeral=True)
            return
        
        # Rename channel
        try:
            await channel.edit(name=f"claimed-{interaction.user.name}")
            
            # Send claim message
            embed = discord.Embed(
                title="Ticket Claimed Successfully!",
                description=f"{interaction.user.mention} has claimed this ticket!",
                color=0x6B8E6B,
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=".pixel Design Services")
            
            await channel.send(embed=embed)
            
            # Log claim
            await self.log_ticket_claim(channel, interaction.user)
            
            # Disable claim button
            button.disabled = True
            button.label = "Claimed"
            await interaction.response.edit_message(view=self)
            
        except Exception as e:
            await interaction.response.send_message(f"Error claiming ticket: {e}", ephemeral=True)
    
    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has close privilege (designer or manager roles)
        if not has_privileged_role(interaction.user):
            await interaction.response.send_message("You don't have permission to close tickets.", ephemeral=True)
            return
        # Create confirmation view
        confirm_view = CloseConfirmationView()
        embed = discord.Embed(
            title="⚠️ Confirm Ticket Closure",
            description="Are you sure you want to close this ticket? This action cannot be undone.",
            color=0x8E6B6B,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Click 'Confirm Close' to proceed")
        await interaction.response.send_message(embed=embed, view=confirm_view, ephemeral=True)
    
    async def log_ticket_claim(self, channel, user):
        """Log ticket claim to the logging channel"""
        try:
            logging_channel = channel.guild.get_channel(LOGGING_CHANNEL_ID)
            if logging_channel:
                embed = discord.Embed(
                    title="🎯 Ticket Claimed",
                    description=f"A ticket has been claimed by a team member",
                    color=0x6B8E6B,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Claimed By", value=f"{user.mention} ({user.name})", inline=True)
                embed.add_field(name="Channel", value=channel.mention, inline=True)
                embed.add_field(name="Status", value="🟢 Claimed", inline=True)
                embed.set_footer(text=f"Ticket ID: {channel.id}")
                
                await logging_channel.send(embed=embed)
        except Exception as e:
            print(f"Error logging ticket claim: {e}")

class CloseConfirmationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Confirm Close", style=discord.ButtonStyle.danger, custom_id="confirm_close")
    async def confirm_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has close privilege (designer or manager roles)
        if not has_privileged_role(interaction.user):
            await interaction.response.send_message("You don't have permission to close tickets.", ephemeral=True)
            return
        channel = interaction.channel
        
        try:
            # Send closing message
            embed = discord.Embed(
                title="🔒 Ticket Closing",
                description="This ticket will be closed in 10 seconds...",
                color=0x8E6B6B,
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=".pixel Design Services")
            await channel.send(embed=embed)
            
            # Send DM notification to ticket opener
            await send_ticket_closure_dm(channel, interaction.user, "design ticket")
            
            # Log closure
            await self.log_ticket_close(channel, interaction.user)
            await interaction.response.send_message("Ticket will be closed in 10 seconds.", ephemeral=True)
            
            # Close after delay
            await asyncio.sleep(10)
            
            # Delete the channel with error handling
            try:
                await channel.delete()
                print(f"Successfully deleted design ticket channel: {channel.name}")
            except discord.Forbidden:
                print(f"Permission denied when trying to delete design ticket channel: {channel.name}")
                # Try to send a message to the channel instead
                try:
                    await channel.send("❌ **Error**: Unable to delete this channel due to insufficient permissions. Please contact an administrator.")
                except:
                    pass
            except discord.NotFound:
                print(f"Design ticket channel already deleted: {channel.name}")
            except Exception as e:
                print(f"Error deleting design ticket channel {channel.name}: {e}")
                # Try to send a message to the channel instead
                try:
                    await channel.send(f"❌ **Error**: Unable to delete this channel. Error: {str(e)}")
                except:
                    pass
                    
        except Exception as e:
            print(f"Error in design ticket close process: {e}")
            await interaction.response.send_message(f"An error occurred while closing the ticket: {str(e)}", ephemeral=True)
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, custom_id="cancel_close")
    async def cancel_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ticket closure cancelled.", ephemeral=True)
    
    async def log_ticket_close(self, channel, user):
        """Log ticket closure to the logging channel"""
        try:
            logging_channel = channel.guild.get_channel(LOGGING_CHANNEL_ID)
            if logging_channel:
                embed = discord.Embed(
                    title="🔒 Ticket Closed",
                    description=f"A ticket has been closed by a team member",
                    color=0x8E6B6B,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Closed By", value=f"{user.mention} ({user.name})", inline=True)
                embed.add_field(name="Channel", value=f"#{channel.name}", inline=True)
                embed.add_field(name="Status", value="🔴 Closed", inline=True)
                embed.set_footer(text=f"Ticket ID: {channel.id}")
                
                await logging_channel.send(embed=embed)
        except Exception as e:
            print(f"Error logging ticket close: {e}")

class PaymentLogView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Paid Out", style=discord.ButtonStyle.success, custom_id="paid_out")
    async def paid_out(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has manager role (only managers should mark as paid out)
        if not has_manager_role(interaction.user):
            await interaction.response.send_message("You don't have permission to mark payments as paid out.", ephemeral=True)
            return
        
        # Disable the button and change its appearance
        button.disabled = True
        button.label = "✅ Paid Out"
        button.style = discord.ButtonStyle.secondary
        
        # Update the embed to show it's been paid out
        embed = interaction.message.embeds[0]
        embed.color = 0x6B8E6B  # Muted green color
        embed.add_field(
            name="Payment Status",
            value=f"✅ **Paid Out** by {interaction.user.mention}",
            inline=False
        )
        
        # Update the message
        await interaction.message.edit(embed=embed, view=self)
        
        # Send confirmation
        await interaction.response.send_message("Payment marked as paid out successfully!", ephemeral=True)
        
        # Log the payment completion
        await self.log_payment_completion(interaction.message, interaction.user)
    
    async def log_payment_completion(self, message, user):
        """Log payment completion to the logging channel"""
        try:
            logging_channel = message.guild.get_channel(LOGGING_CHANNEL_ID)
            if logging_channel:
                embed = discord.Embed(
                    title="💰 Payment Completed",
                    description=f"A payment has been marked as paid out",
                    color=0x6B8E6B,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Marked By", value=f"{user.mention} ({user.name})", inline=True)
                embed.add_field(name="Payment Log", value=message.jump_url, inline=True)
                embed.set_footer(text="Payment processing complete")
                
                await logging_channel.send(embed=embed)
        except Exception as e:
            print(f"Error logging payment completion: {e}")

class WelcomeView(discord.ui.View):
    def __init__(self, member_count: int):
        super().__init__(timeout=None)
        self.member_count = member_count
    
    @discord.ui.button(label="📋 Server Information", style=discord.ButtonStyle.primary, custom_id="server_info")
    async def server_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "📋 **Server Information**\n\n"
            "Welcome to .pixel! Here you'll find everything you need to know about our design services.\n\n"
            "**Quick Links:**\n"
            "• <#1362585428183613587> - Server information and rules\n"
            "• <#1362585428510642325> - Order our design services\n"
            "• <#1362585429706019031> - View our work and updates\n\n"
            "Feel free to explore and ask any questions!",
            ephemeral=True
        )
    
    @discord.ui.button(label="👥 Member Count", style=discord.ButtonStyle.secondary, custom_id="member_count")
    async def member_count(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            f"👥 **Current Member Count:** {self.member_count:,} members\n\n"
            f"Thanks for being part of our growing community! 🎉",
            ephemeral=True
        )

class TicketOrderView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Order Now", style=discord.ButtonStyle.primary, custom_id="order_now")
    async def order_now(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user already has an open ticket
        guild = interaction.guild
        user = interaction.user
        
        existing_ticket = discord.utils.get(guild.channels, 
                                          name=f"unclaimed-{user.name.lower()}")
        if existing_ticket:
            await interaction.response.send_message(
                f"You already have an open ticket: {existing_ticket.mention}",
                ephemeral=True
            )
            return
        
        # Check if all services are closed
        open_services = [service for service, status in order_status_data.items() if status != "closed"]
        if not open_services:
            embed = discord.Embed(
                title="All Services Temporarily Closed",
                description=(
                    "We apologize, but all our design services are currently closed for new orders.\n\n"
                    "**Why are services closed?**\n"
                    f"• We're at full capacity across all service types\n"
                    f"• Our team is focusing on existing orders\n"
                    f"• We're temporarily restructuring our workflow\n\n"
                    f"**What can you do?**\n"
                    f"• Check back later for availability updates\n"
                    f"• Contact our team for custom arrangements\n"
                    f"• Follow our status updates for reopening announcements\n\n"
                    f"Thank you for your understanding! 🙏"
                ),
                color=0x8E6B6B,
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=".pixel Design Services • We'll be back soon!")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Show service selection
        embed = discord.Embed(
            title="Select Your Service",
            description="Please choose the type of design service you'd like to order:",
            color=0x1B75BD,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=".pixel Design Services • Choose your service")
        
        await interaction.response.send_message(
            embed=embed,
            view=ServiceSelectionView(),
            ephemeral=True
        )
    
    @discord.ui.button(label="Order Info & Pricing", style=discord.ButtonStyle.secondary, custom_id="order_info")
    async def order_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="Design Services Information & Base Pricing",
            description="Comprehensive design solutions tailored to your needs. Base pricing is the flat rate, and additional fees may apply for complex projects!",
            color=0x1B75BD,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="Logo Design",
            value="**Starting at 200 RBX per**\nProfessional logo creation with experienced designers!",
            inline=False
        )
        
        embed.add_field(
            name="Clothing Design",
            value="**Starting at 95 RBX per item**\nComplete professional uniforms for your entire server!",
            inline=False
        )
        
        embed.add_field(
            name="Livery",
            value="**Starting at 170 RBX per livery**\nProfessional livery and ELS design for your entire fleet!",
            inline=False
        )
        
        embed.add_field(
            name="ELS",
            value="**Starting at 170 RBX per ELS**\nProfessional ELS design for your entire fleet!",
            inline=False
        )
        
        embed.add_field(
            name="Banner and Graphics",
            value="**Starting at 100 RBX per banner**\nProfessional banner and graphics design masterfully crafted!",
            inline=False
        )
        
        embed.add_field(
            name="Photography",
            value="**Starting at 50 RBX per photo**\nHigh quality photography for your entire server!",
            inline=False
        )
                
        embed.add_field(
            name="What's Included with Every Order",
            value="• Professional consultation\n• Multiple design concepts\n• Unlimited revisions\n• Full usage rights\n• Ongoing support",
            inline=False
        )
        
        embed.add_field(
            name="Estimated Times",
            value="• Standard: 2-3 days\n• Complex projects: 4-6 days",
            inline=False
        )
        
        embed.set_footer(text="All prices in RBX • Custom quotes available for large projects")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guild(s)')
    
    # Set rich presence
    activity = discord.Activity(type=discord.ActivityType.watching, name=".pixel")
    await bot.change_presence(activity=activity)
    print("Rich presence set to: Watching over .pixel")
    
    # Register the persistent views
    bot.add_view(TicketOrderView())
    bot.add_view(TicketManagementView())
    bot.add_view(CloseConfirmationView())
    bot.add_view(PaymentLogView())
    bot.add_view(WelcomeView(0))  # Will be updated with actual member count
    bot.add_view(ServiceSelectionView())  # Add ServiceSelectionView to persistent views
    bot.add_view(SupportTicketOrderView())  # Add SupportTicketOrderView to persistent views
    bot.add_view(SupportSelectionView())  # Add SupportSelectionView to persistent views
    bot.add_view(SupportTicketView())  # Add SupportTicketView to persistent views
    bot.add_view(SupportCloseConfirmationView())  # Add SupportCloseConfirmationView to persistent views
    bot.add_view(EscalationView())  # Add EscalationView to persistent views
    
    # Sync slash commands to specific guild for faster propagation
    GUILD_ID = 1362585427093229709
    
    try:
        # Get the specific guild
        guild = bot.get_guild(GUILD_ID)
        if not guild:
            print(f"Guild with ID {GUILD_ID} not found!")
            return
        
        print(f"Syncing commands to guild: {guild.name} ({guild.id})")
        
        # Clear all existing commands first
        bot.tree.clear_commands(guild=guild)
        print("Cleared existing commands")
        
        # Debug: List all commands in the tree before syncing
        print(f"Commands in tree before sync: {len(bot.tree.get_commands())}")
        for cmd in bot.tree.get_commands():
            print(f"  - /{cmd.name}: {cmd.description}")
        
        # Sync commands to the specific guild
        try:
            synced = await bot.tree.sync()
            print(f"Successfully synced {len(synced)} command(s) to guild: {guild.name}")
            
            # List synced commands for verification
            print("Synced commands:")
            for cmd in synced:
                print(f"  - /{cmd.name}: {cmd.description}")
                
        except discord.Forbidden as e:
            print(f"Permission error during sync: {e}")
            print("Bot may not have 'applications.commands' scope or proper permissions")
        except discord.HTTPException as e:
            print(f"HTTP error during sync: {e}")
            print(f"Status code: {e.status}, Response: {e.response}")
        except Exception as e:
            print(f"Unexpected error during sync: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"Failed to sync commands: {e}")
        # Fallback to global sync if guild sync fails
        try:
            print("Attempting global sync as fallback...")
            synced = await bot.tree.sync()
            print(f"Global sync completed: {len(synced)} command(s)")
        except Exception as fallback_error:
            print(f"Global sync also failed: {fallback_error}")

@bot.event
async def on_member_join(member):
    """send new welcome message"""
    try:
        welcome_channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
        if not welcome_channel:
            print(f"Welcome channel {WELCOME_CHANNEL_ID} not found")
            return
        
        member_count = member.guild.member_count
        
        welc_messages = [
            f"{member.mention}, welcome to .pixel! We're excited to have you here!",
            f"{member.mention}, welcome to .pixel! Ready to create something amazing?",
            f"{member.mention}, welcome to .pixel! We hope you enjoy your time here!",
        ]
        
        welcome_text = random.choice(welc_messages)
        
        embed = discord.Embed(
            title="Welcome to .pixel!",
            description=welcome_text,
            color=0x1B75BD,
        )
        embed.set_footer(text=".pixel Design Services • Professional Quality")
        
        welcome_view = WelcomeView(member_count)
        
        await welcome_channel.send(embed=embed, view=welcome_view)
                
    except Exception as e:
        print(f"Error sending welcome message: {e}")

@bot.command(name='oe')
async def create_order_embed(ctx):
    """Create the order embed (only for users with specific role)"""
    # Check if user has the required role
    if not has_privileged_role(ctx.author):
        await ctx.message.delete()
        await ctx.send("You don't have permission to use this command.", delete_after=5)
        return
    
    # Check if command is used in the correct channel
    if ctx.channel.id != TICKET_CHANNEL_ID:
        await ctx.message.delete()
        await ctx.send("This command can only be used in the designated channel.", delete_after=5)
        return
    
    # Delete the command message
    await ctx.message.delete()
    
    # Create the main order embed
    embed = discord.Embed(
        title=".pixel Design Services",
        description=(
            "Transform your vision into stunning reality with .pixel! \n\n"
            "<:intern:1388542339600875622> **Why Choose .pixel?**\n\n"
            "• **Professional Quality**: Incredibly quality designs that stand out\n"
            "• **Custom Solutions**: Tailored to your unique server and requirements\n"
            "• **Fast Turnaround**: Quick delivery without compromising quality\n"
            "• **Ongoing Support**: We're here to help even after project completion\n"
            "• **Competitive Pricing**: Premium quality at affordable rates\n\n"
            "**Ready to get started with .pixel?** \n\nClick the buttons below to place your order or learn more about our services and pricing."
        ),
        color=0x1B75BD,
    )
    
    embed.add_field(
        name="<:Designer:1388542315370643519> Our Expertise",
        value="Logo Design • Clothing Design • Livery and ELS design • Banner and Graphics • Full Discord Server Design • Professional Photography",
        inline=False
    )
    
    # Generate order status field
    status_text = ""
    for service, status in order_status_data.items():
        if status == "open":
            status_text += f"• {service} <:Open1:1385136250406572154><:Open2:1385136269604159520>\n"
        elif status == "delayed":
            status_text += f"• {service} <:Delayed1:1385141081926275233><:Delayed2:1385141097340338216><:Delayed3:1385141115614789774>\n"
        elif status == "closed":
            status_text += f"• {service} <:Closed1:1385149425436983296><:Closed2:1385149450485370880><:Closed3:1385149473927467028>\n"
    
    embed.add_field(
        name="**Order Status**",
        value=status_text,
        inline=False
    )
    
    embed.add_field(
        name="Client Satisfaction",
        value="4.8/5.0 Rating • 100% Satisfaction Guarantee",
        inline=False
    )
    
    embed.set_footer(text="Professional Design Services • Quality Guaranteed")
    
    # Add main ordering image
    embed.set_image(url="https://cdn.discordapp.com/attachments/1103870377211465818/1390403855019409528/pixeldiscordorder.png?ex=686821ff&is=6866d07f&hm=d76f95b0cb1cc72a5be4e86243b44b7504c6bbecd2c275c2b96ae0b94a939354")
    
    # Send the embed with buttons and store the message ID
    message = await ctx.send(embed=embed, view=TicketOrderView())
    global order_status_message_id
    order_status_message_id = message.id

@bot.command(name='update-order-status')
async def update_order_status(ctx, *, args: str):
    """Update the order status of a specific service (only for users with specific role)"""
    global order_status_data
    
    # Check if user has the required role
    if not has_privileged_role(ctx.author):
        await ctx.message.delete()
        await ctx.send("You don't have permission to use this command.", delete_after=5)
        return
    
    # Check if command is used in the correct channel
    if ctx.channel.id != TICKET_CHANNEL_ID:
        await ctx.message.delete()
        await ctx.send("This command can only be used in the designated channel.", delete_after=5)
        return
    
    # Parse arguments (format: "service status")
    try:
        # Split by the last space to separate service name from status
        parts = args.rsplit(' ', 1)
        if len(parts) != 2:
            await ctx.message.delete()
            await ctx.send("Invalid format. Use: `-update-order-status service status`\n\nExamples:\n`-update-order-status graphics open`\n`-update-order-status clothing closed`\n`-update-order-status logo delayed`", delete_after=8)
            return
        
        service_input = parts[0].strip().lower()
        status = parts[1].strip().lower()
        
        if not service_input or not status:
            await ctx.message.delete()
            await ctx.send("Invalid format. Use: `-update-order-status service status`", delete_after=5)
            return
            
    except Exception:
        await ctx.message.delete()
        await ctx.send("Invalid format. Use: `-update-order-status service status`", delete_after=5)
        return
    
    # Validate status
    if status not in ['open', 'delayed', 'closed']:
        await ctx.message.delete()
        await ctx.send("Invalid status. Use 'open', 'delayed', or 'closed'.", delete_after=5)
        return
    
    # Service name mapping for user-friendly aliases
    service_aliases = {
        # Graphics/Banner related
        'graphics': 'Banner and Graphics',
        'banner': 'Banner and Graphics',
        'banners': 'Banner and Graphics',
        'banner and graphics': 'Banner and Graphics',
        'banners and graphics': 'Banner and Graphics',
        
        # Logo related
        'logo': 'Logo Design',
        'logos': 'Logo Design',
        'logo design': 'Logo Design',
        
        # Clothing related
        'clothing': 'Clothing Design',
        'clothes': 'Clothing Design',
        'uniforms': 'Clothing Design',
        'clothing design': 'Clothing Design',
        
        # Livery related
        'livery': 'Livery',
        'liveries': 'Livery',
        'livery and els': 'Livery and ELS design',
        'livery and els design': 'Livery and ELS design',
        
        # ELS related
        'els': 'ELS',
        'els only': 'ELS',
        
        # Discord related
        'discord': 'Full Discord Server Design',
        'discord layout': 'Full Discord Server Design',
        'discord server': 'Full Discord Server Design',
        'full discord server design': 'Full Discord Server Design',
        
        # Photography related
        'photography': 'Professional Photography',
        'photo': 'Professional Photography',
        'photos': 'Professional Photography',
        'professional photography': 'Professional Photography'
    }
    
    # Try to find the service using aliases
    service = service_aliases.get(service_input)
    
    # If not found in aliases, try exact match (case-insensitive)
    if not service:
        for actual_service in order_status_data.keys():
            if actual_service.lower() == service_input:
                service = actual_service
                break
    
    # Validate service
    if not service or service not in order_status_data:
        await ctx.message.delete()
        available_services = "\n".join([f"• {s}" for s in order_status_data.keys()])
        await ctx.send(f"Invalid service. Available services:\n{available_services}\n\nYou can also use shortcuts like: graphics, logo, clothing, livery, els, discord, photography", delete_after=10)
        return
    
    # Check if status is already set to the requested value
    current_status = order_status_data.get(service, "open")
    if current_status == status.lower():
        embed = discord.Embed(
            title="Status Already Set",
            description=(
                f"**{service}** is already set to **{status.lower()}** status.\n\n"
                f"**Current Status:** {current_status.title()}\n"
                f"**Requested Status:** {status.title()}\n\n"
                f"No changes were made to the order status."
            ),
            color=0xFFA500,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=".pixel Design Services • Status Management")
        await ctx.send(embed=embed, delete_after=5)
        return
    
    # Update the status
    old_status = order_status_data.get(service, "open")
    order_status_data[service] = status.lower()
    
    # Delete the command message
    await ctx.message.delete()
    
    # Send status change confirmation
    embed = discord.Embed(
        title="Status Updated Successfully",
        description=(
            f"**{service}** status has been updated.\n\n"
            f"**Previous Status:** {old_status.title()}\n"
            f"**New Status:** {status.title()}\n\n"
            f"The order embed has been updated to reflect this change."
        ),
        color=0x6B8E6B,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text=".pixel Design Services • Status Management")
    await ctx.send(embed=embed, delete_after=5)
    
    # Update the embed if it exists
    if order_status_message_id:
        try:
            message = await ctx.channel.fetch_message(order_status_message_id)
            
            # Create updated embed
            embed = discord.Embed(
                title=".pixel Design Services",
                description=(
                    "Transform your vision into stunning reality with .pixel! \n\n"
                    "<:intern:1388542339600875622> **Why Choose .pixel?**\n\n"
                    "• **Professional Quality**: Incredibly quality designs that stand out\n"
                    "• **Custom Solutions**: Tailored to your unique server and requirements\n"
                    "• **Fast Turnaround**: Quick delivery without compromising quality\n"
                    "• **Ongoing Support**: We're here to help even after project completion\n"
                    "• **Competitive Pricing**: Premium quality at affordable rates\n\n"
                    "**Ready to get started with .pixel?** \n\nClick the buttons below to place your order or learn more about our services and pricing."
                ),
                color=0x1B75BD,
            )
            
            embed.add_field(
                name="<:Designer:1388542315370643519> Our Expertise",
                value="Logo Design • Clothing Design • Livery and ELS design • Banner and Graphics • Full Discord Server Design • Professional Photography",
                inline=False
            )
            
            # Generate updated order status field
            status_text = ""
            for service_name, service_status in order_status_data.items():
                if service_status == "open":
                    status_text += f"• {service_name} <:Open1:1385136250406572154><:Open2:1385136269604159520>\n"
                elif service_status == "delayed":
                    status_text += f"• {service_name} <:Delayed1:1385141081926275233><:Delayed2:1385141097340338216><:Delayed3:1385141115614789774>\n"
                elif service_status == "closed":
                    status_text += f"• {service_name} <:Closed1:1385149425436983296><:Closed2:1385149450485370880><:Closed3:1385149473927467028>\n"
            
            embed.add_field(
                name="**Order Status**",
                value=status_text,
                inline=False
            )
            
            embed.add_field(
                name="Client Satisfaction",
                value="4.8/5.0 Rating • 100% Satisfaction Guarantee",
                inline=False
            )
            
            embed.set_footer(text="Professional Design Services • Quality Guaranteed")
            
            # Add main ordering image
            embed.set_image(url="https://cdn.discordapp.com/attachments/1103870377211465818/1390403855019409528/pixeldiscordorder.png?ex=686821ff&is=6866d07f&hm=d76f95b0cb1cc72a5be4e86243b44b7504c6bbecd2c275c2b96ae0b94a939354")
            
            # Edit the message with updated embed
            await message.edit(embed=embed, view=TicketOrderView())
            
            # Send confirmation
            await ctx.send(f"Updated {service} status to {status.lower()} successfully!", delete_after=3)
            
        except discord.NotFound:
            embed = discord.Embed(
                title="Order Embed Not Found",
                description=(
                    "The order status embed could not be found.\n\n"
                    "**Solution:** Please recreate the order embed using `-oe` or `/create-order-embed`\n\n"
                    "The status has been updated in the system, but the display embed needs to be refreshed."
                ),
                color=0xFFA500,
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=".pixel Design Services • Status Management")
            await ctx.send(embed=embed, delete_after=10)
        except Exception as e:
            embed = discord.Embed(
                title="Error Updating Status",
                description=(
                    f"An error occurred while updating the order status display.\n\n"
                    f"**Error:** {str(e)}\n\n"
                    f"The status has been updated in the system, but the display may not reflect the change."
                ),
                color=0x8E6B6B,
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=".pixel Design Services • Status Management")
            await ctx.send(embed=embed, delete_after=10)
    else:
        embed = discord.Embed(
            title="No Order Embed Found",
            description=(
                "No order status embed has been created yet.\n\n"
                "**Solution:** Please create an order embed first using `-oe` or `/create-order-embed`\n\n"
                "The status has been updated in the system and will be displayed when the embed is created."
            ),
            color=0xFFA500,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=".pixel Design Services • Status Management")
        await ctx.send(embed=embed, delete_after=10)

@bot.command(name='order-status')
async def show_order_status(ctx):
    """Show current order status for all services"""
    # Check if user has the required role
    if not has_privileged_role(ctx.author):
        await ctx.message.delete()
        await ctx.send("You don't have permission to use this command.", delete_after=5)
        return
    
    # Delete the command message
    await ctx.message.delete()
    
    embed = discord.Embed(
        title="Current Order Status",
        description="Status of all .pixel design services",
        color=0x1B75BD,
        timestamp=datetime.utcnow()
    )
    
    for service, status in order_status_data.items():
        if status == "open":
            embed.add_field(
                name=f"✅ - {service}",
                value="<:Open1:1385136250406572154><:Open2:1385136269604159520> **Open for Orders**",
                inline=True
            )
        elif status == "delayed":
            embed.add_field(
                name=f"⚠️ - {service}",
                value="<:Delayed1:1385141081926275233><:Delayed2:1385141097340338216><:Delayed3:1385141115614789774> **Currently Delayed**",
                inline=True
            )
        elif status == "closed":
            embed.add_field(
                name=f"❌ {service}",
                value="<:Closed1:1385149425436983296><:Closed2:1385149450485370880><:Closed3:1385149473927467028> **Currently Closed**",
                inline=True
            )
        elif status == "closed":
            embed.add_field(
                name=f"❌ {service}",
                value="<:Closed1:1385149425436983296><:Closed2:1385149450485370880><:Closed3:1385149473927467028> **Currently Closed**",
                inline=True
            )
    
    embed.set_footer(text="Use -update-order-status <service> <open/delayed/closed> to update")
    
    await ctx.send(embed=embed, delete_after=10)

# Slash Commands
@bot.tree.command(name="create-order-embed", description="Create the order embed (role restricted)")
async def slash_create_order_embed(interaction: discord.Interaction):
    """Slash command version of -oe"""
    # Check if user has the required role
    if not has_privileged_role(interaction.user):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return
    
    # Check if command is used in the correct channel
    if interaction.channel.id != TICKET_CHANNEL_ID:
        await interaction.response.send_message("This command can only be used in the designated channel.", ephemeral=True)
        return
    
    # Create the main order embed
    embed = discord.Embed(
        title=".pixel Design Services",
        description=(
            "Transform your vision into stunning reality with .pixel! \n\n"
            "<:intern:1388542339600875622> **Why Choose .pixel?**\n\n"
            "• **Professional Quality**: Incredibly quality designs that stand out\n"
            "• **Custom Solutions**: Tailored to your unique server and requirements\n"
            "• **Fast Turnaround**: Quick delivery without compromising quality\n"
            "• **Ongoing Support**: We're here to help even after project completion\n"
            "• **Competitive Pricing**: Premium quality at affordable rates\n\n"
            "**Ready to get started with .pixel?** \n\nClick the buttons below to place your order or learn more about our services and pricing."
        ),
        color=0x1B75BD,
    )
    
    embed.add_field(
        name="<:Designer:1388542315370643519> Our Expertise",
        value="Logo Design • Clothing Design • Livery and ELS design • Banner and Graphics • Full Discord Server Design • Professional Photography",
        inline=False
    )
    
    # Generate order status field
    status_text = ""
    for service, status in order_status_data.items():
        if status == "open":
            status_text += f"• {service} <:Open1:1385136250406572154><:Open2:1385136269604159520>\n"
        elif status == "delayed":
            status_text += f"• {service} <:Delayed1:1385141081926275233><:Delayed2:1385141097340338216><:Delayed3:1385141115614789774>\n"
        elif status == "closed":
            status_text += f"• {service} <:Closed1:1385149425436983296><:Closed2:1385149450485370880><:Closed3:1385149473927467028>\n"
    
    embed.add_field(
        name="**Order Status**",
        value=status_text,
        inline=False
    )
    
    embed.add_field(
        name="Client Satisfaction",
        value="4.8/5.0 Rating • 100% Satisfaction Guarantee",
        inline=False
    )
    
    embed.set_footer(text="Professional Design Services • Quality Guaranteed")
    
    # Add main ordering image
    embed.set_image(url="https://cdn.discordapp.com/attachments/1103870377211465818/1390403855019409528/pixeldiscordorder.png?ex=686821ff&is=6866d07f&hm=d76f95b0cb1cc72a5be4e86243b44b7504c6bbecd2c275c2b96ae0b94a939354")
    
    # Send the embed with buttons and store the message ID
    await interaction.response.send_message(embed=embed, view=TicketOrderView())
    message = await interaction.original_response()
    global order_status_message_id
    order_status_message_id = message.id

@bot.tree.command(name="update-order-status", description="Update the order status of a specific service (role restricted)")
@app_commands.describe(
    service="The service to update",
    status="The new status (open, delayed, or closed)"
)
@app_commands.choices(service=service_choices, status=status_choices)
async def slash_update_order_status(interaction: discord.Interaction, service: str, status: str):
    """Slash command version of -update-order-status"""
    global order_status_data
    
    # Check if user has the required role
    if not has_privileged_role(interaction.user):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return
    
    # Check if command is used in the correct channel
    if interaction.channel.id != TICKET_CHANNEL_ID:
        await interaction.response.send_message("This command can only be used in the designated channel.", ephemeral=True)
        return
    
    # Check if status is already set to the requested value
    current_status = order_status_data.get(service, "open")
    if current_status == status.lower():
        embed = discord.Embed(
            title="Status Already Set",
            description=(
                f"**{service}** is already set to **{status.lower()}** status.\n\n"
                f"**Current Status:** {current_status.title()}\n"
                f"**Requested Status:** {status.title()}\n\n"
                f"No changes were made to the order status."
            ),
            color=0xFFA500,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=".pixel Design Services • Status Management")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Update the status
    old_status = order_status_data.get(service, "open")
    order_status_data[service] = status.lower()
    
    # Send status change confirmation
    embed = discord.Embed(
        title="Status Updated Successfully",
        description=(
            f"**{service}** status has been updated.\n\n"
            f"**Previous Status:** {old_status.title()}\n"
            f"**New Status:** {status.title()}\n\n"
            f"The order embed has been updated to reflect this change."
        ),
        color=0x6B8E6B,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text=".pixel Design Services • Status Management")
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # Update the embed if it exists
    if order_status_message_id:
        try:
            message = await interaction.channel.fetch_message(order_status_message_id)
            
            # Create updated embed
            embed = discord.Embed(
                title=".pixel Design Services",
                description=(
                    "Transform your vision into stunning reality with .pixel! \n\n"
                    "<:intern:1388542339600875622> **Why Choose .pixel?**\n\n"
                    "• **Professional Quality**: Incredibly quality designs that stand out\n"
                    "• **Custom Solutions**: Tailored to your unique server and requirements\n"
                    "• **Fast Turnaround**: Quick delivery without compromising quality\n"
                    "• **Ongoing Support**: We're here to help even after project completion\n"
                    "• **Competitive Pricing**: Premium quality at affordable rates\n\n"
                    "**Ready to get started with .pixel?** \n\nClick the buttons below to place your order or learn more about our services and pricing."
                ),
                color=0x1B75BD,
            )
            
            embed.add_field(
                name="<:Designer:1388542315370643519> Our Expertise",
                value="Logo Design • Clothing Design • Livery and ELS design • Banner and Graphics • Full Discord Server Design • Professional Photography",
                inline=False
            )
            
            # Generate updated order status field
            status_text = ""
            for service_name, service_status in order_status_data.items():
                if service_status == "open":
                    status_text += f"• {service_name} <:Open1:1385136250406572154><:Open2:1385136269604159520>\n"
                elif service_status == "delayed":
                    status_text += f"• {service_name} <:Delayed1:1385141081926275233><:Delayed2:1385141097340338216><:Delayed3:1385141115614789774>\n"
                elif service_status == "closed":
                    status_text += f"• {service_name} <:Closed1:1385149425436983296><:Closed2:1385149450485370880><:Closed3:1385149473927467028>\n"
            
            embed.add_field(
                name="**Order Status**",
                value=status_text,
                inline=False
            )
            
            embed.add_field(
                name="Client Satisfaction",
                value="4.8/5.0 Rating • 100% Satisfaction Guarantee",
                inline=False
            )
            
            embed.set_footer(text="Professional Design Services • Quality Guaranteed")
            
            # Add main ordering image
            embed.set_image(url="https://cdn.discordapp.com/attachments/1103870377211465818/1390403855019409528/pixeldiscordorder.png?ex=686821ff&is=6866d07f&hm=d76f95b0cb1cc72a5be4e86243b44b7504c6bbecd2c275c2b96ae0b94a939354")
            
            # Edit the message with updated embed
            await message.edit(embed=embed, view=TicketOrderView())
            
            # Send confirmation
            await interaction.response.send_message(f"Updated {service} status to {status.lower()} successfully!", ephemeral=True)
            
        except discord.NotFound:
            embed = discord.Embed(
                title="Order Embed Not Found",
                description=(
                    "The order status embed could not be found.\n\n"
                    "**Solution:** Please recreate the order embed using `/create-order-embed`\n\n"
                    "The status has been updated in the system, but the display embed needs to be refreshed."
                ),
                color=0xFFA500,
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=".pixel Design Services • Status Management")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="Error Updating Status",
                description=(
                    f"An error occurred while updating the order status display.\n\n"
                    f"**Error:** {str(e)}\n\n"
                    f"The status has been updated in the system, but the display may not reflect the change."
                ),
                color=0x8E6B6B,
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=".pixel Design Services • Status Management")
            await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            title="No Order Embed Found",
            description=(
                "No order status embed has been created yet.\n\n"
                "**Solution:** Please create an order embed first using `/create-order-embed`\n\n"
                "The status has been updated in the system and will be displayed when the embed is created."
            ),
            color=0xFFA500,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=".pixel Design Services • Status Management")
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="design-reminder", description="Send a design format reminder (role restricted)")
async def slash_design_reminder(interaction: discord.Interaction):
    """Slash command version of -de"""
    # Check if user has the required role
    if not has_privileged_role(interaction.user):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return
    
    # Check if command is used in a design ticket category
    if not interaction.channel.category or interaction.channel.category.id not in DESIGN_CATEGORY_IDS:
        await interaction.response.send_message("This command can only be used in design ticket categories.", ephemeral=True)
        return
    
    # Check if this is a ticket channel
    if not (interaction.channel.name.startswith('unclaimed-') or interaction.channel.name.startswith('claimed-')):
        await interaction.response.send_message("This command can only be used in ticket channels.", ephemeral=True)
        return
    
    # Create the design format reminder embed
    embed = discord.Embed(
        title="📋 Design Format Reminder",
        description=(
            "Hello! 👋 We noticed you haven't provided the required details for your order yet.\n\n"
            "**To help us create exactly what you envision, please provide the following information:**\n\n"
            "**📋 Type:** (e.g., PD for liveries, server logo for graphics)\n"
            "**🎨 Customizations:** Detailed description including colors, style preferences, and specific requirements\n"
            "**📸 Reference(s):** Any images or examples that inspire your vision\n"
            "**💰 Budget Range:** (Optional) Your preferred budget range\n\n"
            "**Please reply with these details so we can get started on your order!** 🚀\n\n"
            "If you have any questions or need clarification, feel free to ask!"
        ),
        color=0x1B75BD,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text=".pixel Design Services • We're here to help!")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="order-start", description="Start an order and send order details (role restricted)")
@app_commands.describe(
    designer="The designer working on this order",
    customer="The customer for this order",
    products="The products/services being ordered",
    price="The agreed upon price",
    completion_time="Estimated completion time"
)
@app_commands.choices(completion_time=completion_time_choices)
async def order_start(interaction: discord.Interaction, designer: discord.Member, customer: discord.Member, products: str, price: str, completion_time: str):
    """Start an order and send order details"""
    # Check if user has the required role
    if not has_privileged_role(interaction.user):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return
    
    # Check if command is used in a design ticket category
    if not interaction.channel.category or interaction.channel.category.id not in DESIGN_CATEGORY_IDS:
        await interaction.response.send_message("This command can only be used in design ticket categories.", ephemeral=True)
        return
    
    # Check if this is a ticket channel
    if not (interaction.channel.name.startswith('unclaimed-') or interaction.channel.name.startswith('claimed-')):
        await interaction.response.send_message("This command can only be used in ticket channels.", ephemeral=True)
        return
    
    # Handle custom completion time
    if completion_time == "custom":
        # For now, we'll use a placeholder. In a full implementation, you might want to use a modal
        completion_time = "Custom (to be specified)"
    
    # Create the order start embed
    embed = discord.Embed(
        title="🚀 Order Started!",
        description=(
            f"**Your order has been officially started!** 🎉\n\n"
            f"We're excited to begin working on your project and will keep you updated throughout the process.\n\n"
            f"**📋 Order Details:**\n"
            f"• **Designer:** {designer.mention}\n"
            f"• **Customer:** {customer.mention}\n"
            f"• **Products/Services:** {products}\n"
            f"• **Agreed Price:** {price}\n"
            f"• **Estimated Completion:** {completion_time}\n\n"
            f"**📞 Communication:**\n"
            f"• Your designer will keep you updated on progress\n"
            f"• Feel free to ask questions or provide additional details\n"
            f"• We'll notify you when your order is ready for review\n\n"
            f"**⏰ Next Steps:**\n"
            f"• Your designer will begin working on your project\n"
            f"• You'll receive progress updates and previews\n"
            f"• Final delivery will be provided within the estimated timeframe\n\n"
            f"Thank you for choosing .pixel! We're committed to delivering exceptional quality. ✨"
        ),
        color=0x00FF00,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text=".pixel Design Services • Professional Quality Guaranteed")
    
    await interaction.response.send_message(embed=embed)
    
    # Store order details for payment logging
    order_details[interaction.channel.id] = {
        'designer': designer,
        'customer': customer,
        'products': products,
        'price': price,
        'completion_time': completion_time
    }
    
    # Log the order start
    await log_order_start(interaction.channel, designer, customer, products, price, completion_time)

async def log_order_start(channel, designer, customer, products, price, completion_time):
    """Log order start to the logging channel"""
    try:
        logging_channel = channel.guild.get_channel(LOGGING_CHANNEL_ID)
        if logging_channel:
            embed = discord.Embed(
                title="🚀 Order Started",
                description=f"An order has been officially started",
                color=0x00FF00,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Designer", value=f"{designer.mention} ({designer.name})", inline=True)
            embed.add_field(name="Customer", value=f"{customer.mention} ({customer.name})", inline=True)
            embed.add_field(name="Channel", value=channel.mention, inline=True)
            embed.add_field(name="Products", value=products, inline=False)
            embed.add_field(name="Price", value=price, inline=True)
            embed.add_field(name="Est. Completion", value=completion_time, inline=True)
            embed.set_footer(text=f"Ticket ID: {channel.id}")
            
            await logging_channel.send(embed=embed)
    except Exception as e:
        print(f"Error logging order start: {e}")

@bot.tree.command(name="order-status", description="Show current order status for all services (role restricted)")
async def slash_show_order_status(interaction: discord.Interaction):
    """Slash command version of -order-status"""
    # Check if user has the required role
    if not has_privileged_role(interaction.user):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="Current Order Status",
        description="Status of all .pixel design services",
        color=0x1B75BD,
        timestamp=datetime.utcnow()
    )
    
    for service, status in order_status_data.items():
        if status == "open":
            embed.add_field(
                name=f"✅ - {service}",
                value="<:Open1:1385136250406572154><:Open2:1385136269604159520> **Open for Orders**",
                inline=True
            )
        elif status == "delayed":
            embed.add_field(
                name=f"⚠️ - {service}",
                value="<:Delayed1:1385141081926275233><:Delayed2:1385141097340338216><:Delayed3:1385141115614789774> **Currently Delayed**",
                inline=True
            )
    
    embed.set_footer(text="Use /update-order-status to update service status")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.command(name='de')
async def design_reminder(ctx):
    """Send a design format reminder (only for design ticket categories)"""
    # Check if user has the required role
    if not has_privileged_role(ctx.author):
        await ctx.message.delete()
        await ctx.send("You don't have permission to use this command.", delete_after=5)
        return
    
    # Check if command is used in a design ticket category
    if not ctx.channel.category or ctx.channel.category.id not in DESIGN_CATEGORY_IDS:
        await ctx.message.delete()
        await ctx.send("This command can only be used in design ticket categories.", delete_after=5)
        return
    
    # Check if this is a ticket channel
    if not (ctx.channel.name.startswith('unclaimed-') or ctx.channel.name.startswith('claimed-')):
        await ctx.message.delete()
        await ctx.send("This command can only be used in ticket channels.", delete_after=5)
        return
    
    # Delete the command message
    await ctx.message.delete()
    
    # Create the design format reminder embed
    embed = discord.Embed(
        title="📋 Design Format Reminder",
        description=(
            "Hello! 👋 We noticed you haven't provided the required details for your order yet.\n\n"
            "**To help us create exactly what you envision, please provide the following information:**\n\n"
            "**📋 Type:** (e.g., PD for liveries, server logo for graphics)\n"
            "**🎨 Customizations:** Detailed description including colors, style preferences, and specific requirements\n"
            "**📸 Reference(s):** Any images or examples that inspire your vision\n"
            "**💰 Budget Range:** (Optional) Your preferred budget range\n\n"
            "**Please reply with these details so we can get started on your order!** 🚀\n\n"
            "If you have any questions or need clarification, feel free to ask!"
        ),
        color=0x1B75BD,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text=".pixel Design Services • We're here to help!")
    
    await ctx.send(embed=embed)

@bot.command(name='os')
async def order_start_prefix(ctx, designer: discord.Member, customer: discord.Member, *, details: str):
    """Start an order using prefix command (only for design ticket categories)"""
    # Check if user has the required role
    if not has_privileged_role(ctx.author):
        await ctx.message.delete()
        await ctx.send("You don't have permission to use this command.", delete_after=5)
        return
    
    # Check if command is used in a design ticket category
    if not ctx.channel.category or ctx.channel.category.id not in DESIGN_CATEGORY_IDS:
        await ctx.message.delete()
        await ctx.send("This command can only be used in design ticket categories.", delete_after=5)
        return
    
    # Check if this is a ticket channel
    if not (ctx.channel.name.startswith('unclaimed-') or ctx.channel.name.startswith('claimed-')):
        await ctx.message.delete()
        await ctx.send("This command can only be used in ticket channels.", delete_after=5)
        return
    
    # Parse details (format: "products | price | completion_time")
    try:
        parts = details.split('|')
        if len(parts) < 3:
            await ctx.send("Please provide details in format: `products | price | completion_time`", delete_after=10)
            return
        
        products = parts[0].strip()
        price = parts[1].strip()
        completion_time = parts[2].strip()
        
        if not products or not price or not completion_time:
            await ctx.send("Please provide all required details: products, price, and completion time.", delete_after=10)
            return
            
    except Exception:
        await ctx.send("Please provide details in format: `products | price | completion_time`", delete_after=10)
        return
    
    # Delete the command message
    await ctx.message.delete()
    
    # Create the order start embed
    embed = discord.Embed(
        title="🚀 Order Started!",
        description=(
            f"**Your order has been officially started!** 🎉\n\n"
            f"We're excited to begin working on your project and will keep you updated throughout the process.\n\n"
            f"**📋 Order Details:**\n"
            f"• **Designer:** {designer.mention}\n"
            f"• **Customer:** {customer.mention}\n"
            f"• **Products/Services:** {products}\n"
            f"• **Agreed Price:** {price}\n"
            f"• **Estimated Completion:** {completion_time}\n\n"
            f"**📞 Communication:**\n"
            f"• Your designer will keep you updated on progress\n"
            f"• Feel free to ask questions or provide additional details\n"
            f"• We'll notify you when your order is ready for review\n\n"
            f"**⏰ Next Steps:**\n"
            f"• Your designer will begin working on your project\n"
            f"• You'll receive progress updates and previews\n"
            f"• Final delivery will be provided within the estimated timeframe\n\n"
            f"Thank you for choosing .pixel! We're committed to delivering exceptional quality."
        ),
        color=0x00FF00,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text=".pixel Design Services • Professional Quality Guaranteed")
    
    await ctx.send(embed=embed)
    
    # Store order details for payment logging
    order_details[ctx.channel.id] = {
        'designer': designer,
        'customer': customer,
        'products': products,
        'price': price,
        'completion_time': completion_time
    }
    
    # Log the order start
    await log_order_start(ctx.channel, designer, customer, products, price, completion_time)

@bot.command(name='sync')
async def sync_commands(ctx):
    """Manually sync slash commands (admin only)"""
    if not has_privileged_role(ctx.author):
        await ctx.send("You don't have permission to use this command.", delete_after=5)
        return
    
    await ctx.message.delete()
    
    try:
        # Get the specific guild
        guild = ctx.guild
        print(f"Manual sync requested for guild: {guild.name} ({guild.id})")
        
        # Clear all existing commands first
        bot.tree.clear_commands(guild=guild)
        print("Cleared existing commands")
        
        # Debug: List all commands in the tree before syncing
        print(f"Commands in tree before sync: {len(bot.tree.get_commands())}")
        for cmd in bot.tree.get_commands():
            print(f"  - /{cmd.name}: {cmd.description}")
        
        # Sync commands to the specific guild
        try:
            synced = await bot.tree.sync()
            print(f"Successfully synced {len(synced)} command(s) to guild: {guild.name}")
            
            # List synced commands for verification
            print("Synced commands:")
            for cmd in synced:
                print(f"  - /{cmd.name}: {cmd.description}")
                
        except discord.Forbidden as e:
            print(f"Permission error during sync: {e}")
            print("Bot may not have 'applications.commands' scope or proper permissions")
            raise e
        except discord.HTTPException as e:
            print(f"HTTP error during sync: {e}")
            print(f"Status code: {e.status}, Response: {e.response}")
            raise e
        except Exception as e:
            print(f"Unexpected error during sync: {e}")
            import traceback
            traceback.print_exc()
            raise e
        
        embed = discord.Embed(
            title="✅ - Commands Synced Successfully",
            description=f"Successfully synced {len(synced)} command(s) to {guild.name}",
            color=0x6B8E6B,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Synced Commands", value="\n".join([f"• /{cmd.name}" for cmd in synced]), inline=False)
        embed.set_footer(text=".pixel Design Services • Command Sync")
        
        await ctx.send(embed=embed, delete_after=10)
        
    except Exception as e:
        print(f"Manual sync failed: {e}")
        embed = discord.Embed(
            title="❌ Sync Failed",
            description=f"Failed to sync commands: {str(e)}",
            color=0x8E6B6B,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=".pixel Design Services • Command Sync")
        await ctx.send(embed=embed, delete_after=10)

@bot.command(name='check-perms')
async def check_permissions(ctx):
    """Check bot permissions (admin only)"""
    if not has_privileged_role(ctx.author):
        await ctx.send("You don't have permission to use this command.", delete_after=5)
        return
    
    await ctx.message.delete()
    
    guild = ctx.guild
    bot_member = guild.get_member(bot.user.id)
    
    embed = discord.Embed(
        title="🤖 Bot Permission Check",
        description=f"Checking permissions for {bot.user.name} in {guild.name}",
        color=0x1B75BD,
        timestamp=datetime.utcnow()
    )
    
    # Check key permissions
    key_permissions = [
        'send_messages',
        'use_slash_commands',
        'manage_channels',
        'manage_messages',
        'embed_links',
        'attach_files',
        'read_message_history',
        'add_reactions'
    ]
    
    for perm in key_permissions:
        has_perm = getattr(bot_member.guild_permissions, perm, False)
        status = "✅" if has_perm else "❌"
        embed.add_field(name=f"{status} {perm.replace('_', ' ').title()}", value="Yes" if has_perm else "No", inline=True)
    
    # Check if bot has applications.commands scope
    embed.add_field(name="🔧 Applications Commands", value="Check bot invite URL", inline=False)
    
    # Generate proper invite URL
    invite_url = f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands"
    embed.add_field(name="📋 Proper Invite URL", value=f"```{invite_url}```", inline=False)
    
    embed.set_footer(text=".pixel Design Services • Permission Check")
    
    await ctx.send(embed=embed, delete_after=30)

@bot.command(name='close')
async def close_ticket(ctx):
    """Close the current ticket channel (privileged only)"""
    if not ctx.channel.name.startswith('ticket-'):
        await ctx.send("This command can only be used in ticket channels.")
        return
    # Check if user has close privilege (designer or manager roles)
    if not has_privileged_role(ctx.author):
        await ctx.send("You don't have permission to close this ticket.", delete_after=5)
        return
    
    try:
        embed = discord.Embed(
            title="Ticket Closing",
            description="This ticket will be closed in 10 seconds...",
            color=0x8E6B6B,
            timestamp=datetime.utcnow()
        )
        await ctx.send(embed=embed)
        await asyncio.sleep(10)
        
        # Delete the channel with error handling
        try:
            await ctx.channel.delete()
            print(f"Successfully deleted ticket channel: {ctx.channel.name}")
        except discord.Forbidden:
            print(f"Permission denied when trying to delete ticket channel: {ctx.channel.name}")
            await ctx.send("❌ **Error**: Unable to delete this channel due to insufficient permissions. Please contact an administrator.")
        except discord.NotFound:
            print(f"Ticket channel already deleted: {ctx.channel.name}")
        except Exception as e:
            print(f"Error deleting ticket channel {ctx.channel.name}: {e}")
            await ctx.send(f"❌ **Error**: Unable to delete this channel. Error: {str(e)}")
            
    except Exception as e:
        print(f"Error in close ticket command: {e}")
        await ctx.send(f"An error occurred while closing the ticket: {str(e)}")

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    else:
        await ctx.send(f"An error occurred: {error}")

@bot.tree.command(name="finished", description="Mark the order as finished and thank the client (privileged only)")
async def finished_order(interaction: discord.Interaction):
    """Mark the order as finished, rename the channel, and send a thank you embed."""
    # Privilege check: designer or manager roles
    if not has_privileged_role(interaction.user):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    channel = interaction.channel
    # Only allow in ticket channels
    if not (channel.name.startswith('unclaimed-') or channel.name.startswith('claimed-') or channel.name.startswith('finished-')):
        await interaction.response.send_message("This command can only be used in ticket channels.", ephemeral=True)
        return

    # Get order details to find the customer
    customer = None
    if channel.id in order_details:
        customer = order_details[channel.id]['customer']
    
    # Rename the channel to finished-username
    username = channel.name.split('-', 1)[-1]
    new_name = f"finished-{username}"
    try:
        await channel.edit(name=new_name)
    except Exception as e:
        await interaction.response.send_message(f"Failed to rename channel: {e}", ephemeral=True)
        return

    # Assign customer role if customer is found
    if customer:
        try:
            customer_role = channel.guild.get_role(REVIEW_ROLE_ID)  # Using REVIEW_ROLE_ID as customer role
            if customer_role and customer_role not in customer.roles:
                await customer.add_roles(customer_role)
                role_assigned = True
            else:
                role_assigned = False
        except Exception as e:
            print(f"Error assigning customer role: {e}")
            role_assigned = False
    else:
        role_assigned = False

    # Send thank you embed
    embed = discord.Embed(
        title="🎉 Order Complete!",
        description=(
            f"Thank you for choosing .pixel for your design needs!\n\n"
            f"Your order is now **finished** and we hope you love the results.\n\n"
            f"If you have any feedback, questions, or need further assistance, please let us know.\n\n"
            f"We appreciate your business and look forward to working with you again!"
        ),
        color=0x1B75BD,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text=".pixel Design Services • Thank you for your order!")
    await channel.send(embed=embed)

    # Send role assignment notification if applicable
    if customer and role_assigned:
        role_embed = discord.Embed(
            title="✅ Customer Role Assigned",
            description=f"{customer.mention} has been assigned the customer role and can now submit reviews!",
            color=0x6B8E6B,
            timestamp=datetime.utcnow()
        )
        role_embed.set_footer(text=".pixel Design Services • Review System")
        await channel.send(embed=role_embed)

    # Log the completion
    try:
        logging_channel = channel.guild.get_channel(LOGGING_CHANNEL_ID)
        if logging_channel:
            log_embed = discord.Embed(
                title="Order Finished Successfully!",
                description=f"A ticket has been marked as finished.",
                color=0x1B75BD,
                timestamp=datetime.utcnow()
            )
            log_embed.add_field(name="Channel", value=channel.mention, inline=True)
            log_embed.add_field(name="Finished By", value=f"{interaction.user.mention} ({interaction.user.name})", inline=True)
            if customer:
                log_embed.add_field(name="Customer", value=f"{customer.mention} ({customer.name})", inline=True)
                log_embed.add_field(name="Role Assigned", value="✅ Yes" if role_assigned else "❌ No", inline=True)
            log_embed.set_footer(text=f"Ticket ID: {channel.id}")
            await logging_channel.send(embed=log_embed)
    except Exception as e:
        print(f"Error logging order finish: {e}")

    await interaction.response.send_message(f"Order marked as finished and channel renamed to {new_name}.", ephemeral=True)

@bot.command(name='we')
async def workload_explanation(ctx):
    """Send a friendly delay/workload explanation embed (privileged only)"""
    if not has_privileged_role(ctx.author):
        await ctx.message.delete()
        await ctx.send("You don't have permission to use this command.", delete_after=5)
        return
    await ctx.message.delete()
    embed = discord.Embed(
        title="⏳ Order Update: Thank You for Your Patience!",
        description=(
            "We wanted to let you know that your order is still in our queue.\n\n"
            "Due to a high volume of orders or current team workload, there may be a delay in claiming or completing your request.\n\n"
            "**Why might this happen?**\n"
            "• Our designers are working hard on existing projects\n"
            "• We're experiencing a temporary surge in demand\n"
            "• Your order is waiting to be claimed by a team member\n\n"
            "**What can you do?**\n"
            "• Rest assured, your order is important to us!\n"
            "• You can ask for an update at any time\n"
            "• We'll notify you as soon as your order is claimed or started\n\n"
            "Thank you for your patience and understanding. We appreciate your business and are committed to delivering the best possible results!"
        ),
        color=0x1B75BD,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text=".pixel Design Services • We appreciate your patience!")
    await ctx.send(embed=embed)

@bot.command(name='se')
async def create_support_embed(ctx):
    """Create the support embed (only for users with specific role)"""
    # Check if user has the required role
    if not has_support_privileged_role(ctx.author):
        await ctx.message.delete()
        await ctx.send("You don't have permission to use this command.", delete_after=5)
        return
    
    # Check if command is used in the correct channel
    if ctx.channel.id != 1362585428183613589:
        await ctx.message.delete()
        await ctx.send("This command can only be used in the designated channel.", delete_after=5)
        return
    
    # Delete the command message
    await ctx.message.delete()
    
    # Create the main support embed
    embed = discord.Embed(
        title="🎫 .pixel Support Center",
        description=(
            "Need help? We're here to assist you! \n\n"
            "🔧 **Our Support Team**\n\n"
            "• **Professional Support Staff**: Experienced team ready to help\n"
            "• **Multiple Support Levels**: From general questions to complex issues\n"
            "• **Quick Response Times**: We prioritize your concerns\n"
            "• **Comprehensive Solutions**: We work to resolve issues completely\n"
            "• **24/7 Availability**: Support when you need it\n\n"
            "**Ready to get help?** \n\nClick the buttons below to create a support ticket or learn more about our support system."
        ),
        color=0x1B75BD,
    )
    
    embed.add_field(
        name="🔧 Support Types",
        value="General Support • High Rank Support • Executive Support",
        inline=False
    )
    
    embed.add_field(
        name="📋 What We Help With",
        value="• Account issues and questions\n• Product problems and errors\n• Service inquiries and clarifications\n• Policy and management concerns",
        inline=False
    )
    
    embed.add_field(
        name="💡 Tips for Faster Support",
        value="• Be specific about your issue\n• Add relevant screenshots when possible",
        inline=False
    )
    
    embed.set_footer(text="Professional Support Services • We're here to help!")
    
    # Send the embed with buttons
    await ctx.send(embed=embed, view=SupportTicketOrderView())

@bot.command(name='pe')
async def create_package_claim_embed(ctx):
    """Create the package claim embed (only for users with specific role)"""
    # Check if user has the required role
    if not has_support_privileged_role(ctx.author):
        await ctx.message.delete()
        await ctx.send("You don't have permission to use this command.", delete_after=5)
        return
    
    # Check if command is used in the correct channel
    if ctx.channel.id != PACKAGE_CLAIM_CHANNEL_ID:
        await ctx.message.delete()
        await ctx.send("This command can only be used in the designated channel.", delete_after=5)
        return
    
    # Delete the command message
    await ctx.message.delete()
    
    # Create the main package claim embed
    if PACKAGE_CLAIM_ENABLED:
        embed = discord.Embed(
            title="📦 .pixel Package Claims",
            description=(
                "Ready to claim your purchased package? We're here to help! \n\n"
                "🎁 **Package Claim Process**\n\n"
                "• **Easy Claim Process**: Simple and straightforward package claiming\n"
                "• **Professional Support**: Our team will assist you with your claim\n"
                "• **Quick Processing**: We prioritize your package claims\n"
                "• **Secure Verification**: We ensure your purchase is verified\n"
                "• **Friendly Service**: Professional and helpful staff\n\n"
                "**Ready to claim your package?** \n\nClick the button below to start your package claim process."
            ),
            color=0x1B75BD,
        )
        
        embed.add_field(
            name="📋 What You'll Need",
            value="• Proof of purchase (screenshot/receipt)\n• Package details\n• Any additional requirements",
            inline=False
        )
        
        embed.add_field(
            name="💡 Tips for Faster Processing",
            value="• Ensure proof of purchase is clear and readable\n• Include your username/email if not visible\n• Be specific about which package you purchased",
            inline=False
        )
        
        embed.set_footer(text="Professional Package Claims • We're here to help!")
    else:
        embed = discord.Embed(
            title="📦 .pixel Package Claims - Temporarily Unavailable",
            description=(
                "**Package Orders Currently Unavailable**\n\n"
                "We regret to inform you that we are currently unable to handle package orders at this time.\n\n"
                "**What this means:**\n"
                "• Package claiming functionality is temporarily suspended\n"
                "• We are unable to process new package claims\n"
                "• Existing package claims remain unaffected\n\n"
                "**When will packages reopen?**\n"
                "• Packages will reopen at a later date\n"
                "• We will announce the reopening through our official channels\n"
                "• Please stay tuned for updates\n\n"
                "**We appreciate your understanding and patience.**\n"
                "Thank you for your continued support!"
            ),
            color=0xFF6B6B,
        )
        
        embed.add_field(
            name="⏰ Status Update",
            value="• Package orders temporarily suspended\n• Reopening date to be announced\n• Stay tuned for official updates",
            inline=False
        )
        
        embed.add_field(
            name="📞 Support",
            value="• For urgent matters, please contact support\n• Existing claims will be processed as usual\n• We apologize for any inconvenience",
            inline=False
        )
        
        embed.set_footer(text="Professional Package Claims • Temporarily Unavailable")
    
    # Send the embed with buttons
    view = PackageClaimView()
    if not PACKAGE_CLAIM_ENABLED:
        # Disable the button when packages aren't available
        for child in view.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
                child.label = "Packages Temporarily Unavailable"
                child.style = discord.ButtonStyle.secondary
    await ctx.send(embed=embed, view=view)

@bot.command(name='disable-package-claims')
async def disable_package_claims(ctx):
    """Disable package claim functionality (role restricted)"""
    global PACKAGE_CLAIM_ENABLED
    
    # Check if user has the required role
    if not has_support_privileged_role(ctx.author):
        await ctx.message.delete()
        await ctx.send("You don't have permission to use this command.", delete_after=5)
        return
    
    # Check if command is used in the correct channel
    if ctx.channel.id != PACKAGE_CLAIM_CHANNEL_ID:
        await ctx.message.delete()
        await ctx.send("This command can only be used in the designated channel.", delete_after=5)
        return
    
    # Delete the command message
    await ctx.message.delete()
    
    # Disable package claims
    PACKAGE_CLAIM_ENABLED = False
    
    # Create confirmation embed
    embed = discord.Embed(
        title="📦 Package Claims Disabled",
        description=(
            f"Package claim functionality has been **disabled** by {ctx.author.mention}.\n\n"
            "**What this means:**\n"
            "• Users can no longer create package claim tickets\n"
            "• The 'Claim Package' button will show a 'temporarily unavailable' message\n"
            "• Existing tickets remain unaffected\n\n"
            "**To re-enable:** Use `-enable-package-claims` or `/enable-package-claims`"
        ),
        color=0xFF6B6B,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text=".pixel Package Claims • Management")
    
    await ctx.send(embed=embed, delete_after=10)

@bot.command(name='enable-package-claims')
async def enable_package_claims(ctx):
    """Enable package claim functionality (role restricted)"""
    global PACKAGE_CLAIM_ENABLED
    
    # Check if user has the required role
    if not has_support_privileged_role(ctx.author):
        await ctx.message.delete()
        await ctx.send("You don't have permission to use this command.", delete_after=5)
        return
    
    # Check if command is used in the correct channel
    if ctx.channel.id != PACKAGE_CLAIM_CHANNEL_ID:
        await ctx.message.delete()
        await ctx.send("This command can only be used in the designated channel.", delete_after=5)
        return
    
    # Delete the command message
    await ctx.message.delete()
    
    # Enable package claims
    PACKAGE_CLAIM_ENABLED = True
    
    # Create confirmation embed
    embed = discord.Embed(
        title="📦 Package Claims Enabled",
        description=(
            f"Package claim functionality has been **enabled** by {ctx.author.mention}.\n\n"
            "**What this means:**\n"
            "• Users can now create package claim tickets\n"
            "• The 'Claim Package' button is fully functional\n"
            "• Package claims are now live! 🎉\n\n"
            "**To disable:** Use `-disable-package-claims` or `/disable-package-claims`"
        ),
        color=0x6B8E6B,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text=".pixel Package Claims • Management")
    
    await ctx.send(embed=embed, delete_after=10)

def has_manager_role(user):
    """Check if user has any manager/executive role"""
    user_role_ids = [role.id for role in user.roles]
    return (user.guild_permissions.administrator or 
            any(role_id in user_role_ids for role_id in MANAGER_ROLE_IDS))

def has_designer_role(user):
    """Check if user has any designer role"""
    user_role_ids = [role.id for role in user.roles]
    return any(role_id in user_role_ids for role_id in DESIGNER_ROLE_IDS)

def has_privileged_role(user):
    """Check if user has any manager or designer role"""
    return has_manager_role(user) or has_designer_role(user)

@bot.tree.command(name="payment-log", description="Log payment information for completed order (designer only)")
async def payment_log(interaction: discord.Interaction):
    """Log payment information for a completed order"""
    # Check if user has designer role
    if not has_designer_role(interaction.user):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return
    
    channel = interaction.channel
    
    # Check if this is a ticket channel
    if not (channel.name.startswith('unclaimed-') or channel.name.startswith('claimed-') or channel.name.startswith('finished-')):
        await interaction.response.send_message("This command can only be used in ticket channels.", ephemeral=True)
        return
    
    # Get order details
    if channel.id not in order_details:
        await interaction.response.send_message("No order details found for this channel. Please ensure the order was started with /order-start or -os.", ephemeral=True)
        return
    
    order_info = order_details[channel.id]
    
    # Create payment log embed
    embed = discord.Embed(
        title="💰 Payment Log",
        description="Order completed - payment information logged",
        color=0x6B8E6B,
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(name="Designer", value=f"{order_info['designer'].mention} ({order_info['designer'].name})", inline=True)
    embed.add_field(name="Customer", value=f"{order_info['customer'].mention} ({order_info['customer'].name})", inline=True)
    embed.add_field(name="Channel", value=channel.mention, inline=True)
    embed.add_field(name="Products/Services", value=order_info['products'], inline=False)
    embed.add_field(name="Agreed Price", value=order_info['price'], inline=True)
    embed.add_field(name="Est. Completion", value=order_info['completion_time'], inline=True)
    embed.add_field(name="Logged By", value=f"{interaction.user.mention} ({interaction.user.name})", inline=True)
    embed.set_footer(text=f"Order ID: {channel.id}")
    
    # Send to payment log channel
    try:
        payment_channel = channel.guild.get_channel(PAYMENT_LOG_CHANNEL_ID)
        if payment_channel:
            payment_view = PaymentLogView()
            await payment_channel.send(embed=embed, view=payment_view)
            await interaction.response.send_message("✅ - Payment information logged successfully!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ - Payment log channel not found.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ - Error logging payment: {str(e)}", ephemeral=True)

@bot.command(name='pl')
async def payment_log_prefix(ctx):
    """Log payment information for completed order (designer only) - prefix version"""
    # Check if user has designer role
    if not has_designer_role(ctx.author):
        await ctx.message.delete()
        await ctx.send("You don't have permission to use this command.", delete_after=5)
        return
    
    channel = ctx.channel
    
    # Check if this is a ticket channel
    if not (channel.name.startswith('unclaimed-') or channel.name.startswith('claimed-') or channel.name.startswith('finished-')):
        await ctx.message.delete()
        await ctx.send("This command can only be used in ticket channels.", delete_after=5)
        return
    
    # Get order details
    if channel.id not in order_details:
        await ctx.message.delete()
        await ctx.send("No order details found for this channel. Please ensure the order was started with /order-start or -os.", delete_after=10)
        return
    
    order_info = order_details[channel.id]
    
    # Create payment log embed
    embed = discord.Embed(
        title="💰 Payment Log",
        description="Order completed - payment information logged",
        color=0x6B8E6B,
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(name="Designer", value=f"{order_info['designer'].mention} ({order_info['designer'].name})", inline=True)
    embed.add_field(name="Customer", value=f"{order_info['customer'].mention} ({order_info['customer'].name})", inline=True)
    embed.add_field(name="Channel", value=channel.mention, inline=True)
    embed.add_field(name="Products/Services", value=order_info['products'], inline=False)
    embed.add_field(name="Agreed Price", value=order_info['price'], inline=True)
    embed.add_field(name="Est. Completion", value=order_info['completion_time'], inline=True)
    embed.add_field(name="Logged By", value=f"{ctx.author.mention} ({ctx.author.name})", inline=True)
    embed.set_footer(text=f"Order ID: {channel.id}")
    
    # Delete the command message
    await ctx.message.delete()
    
    # Send to payment log channel
    try:
        payment_channel = channel.guild.get_channel(PAYMENT_LOG_CHANNEL_ID)
        if payment_channel:
            payment_view = PaymentLogView()
            await payment_channel.send(embed=embed, view=payment_view)
            await ctx.send("✅ - Payment information logged successfully!", delete_after=5)
        else:
            await ctx.send("❌ - Payment log channel not found.", delete_after=5)
    except Exception as e:
        await ctx.send(f"❌ - Error logging payment: {str(e)}", delete_after=10)

@bot.tree.command(name="tax", description="Calculate the amount needed to account for Roblox's 70% cut")
@app_commands.describe(amount="The desired payout amount in RBX")
async def slash_calculate_tax(interaction: discord.Interaction, amount: int):
    """Slash command version of tax calculation"""
    if amount <= 0:
        await interaction.response.send_message("Please provide a positive amount.", ephemeral=True)
        return
    
    # Calculate the amount needed to get the desired payout after 70% cut
    required_amount = math.ceil(amount / 0.7)
    
    embed = discord.Embed(
        title="💰 Tax Calculator",
        description="Calculate amount needed to account for Roblox's 70% cut",
        color=0x1B75BD,
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(
        name="Desired Payout",
        value=f"**{amount:,} RBX**",
        inline=True
    )
    
    embed.add_field(
        name="Required Amount",
        value=f"**{required_amount:,} RBX**",
        inline=True
    )
    
    embed.add_field(
        name="Roblox Cut (30%)",
        value=f"**{required_amount - amount:,} RBX**",
        inline=True
    )
    
    embed.add_field(
        name="Your Payout (70%)",
        value=f"**{amount:,} RBX**",
        inline=True
    )
    
    embed.add_field(
        name="Calculation",
        value=f"`{amount} ÷ 0.7 = {required_amount}` (rounded up)",
        inline=False
    )
    
    embed.set_footer(text=".pixel Design Services • Tax Calculator")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.command(name='tax')
async def calculate_tax(ctx, amount: int):
    """Calculate the amount needed to account for Roblox's 70% cut"""
    if amount <= 0:
        await ctx.send("Please provide a positive amount.", delete_after=5)
        return
    
    # Calculate the amount needed to get the desired payout after 70% cut
    # Formula: desired_amount / 0.7 (since Roblox takes 30%, you keep 70%)
    required_amount = math.ceil(amount / 0.7)
    
    embed = discord.Embed(
        title="💰 Tax Calculator",
        description="Calculate amount needed to account for Roblox's 70% cut",
        color=0x1B75BD,
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(
        name="Desired Payout",
        value=f"**{amount:,} RBX**",
        inline=True
    )
    
    embed.add_field(
        name="Required Amount",
        value=f"**{required_amount:,} RBX**",
        inline=True
    )
    
    embed.add_field(
        name="Roblox Cut (30%)",
        value=f"**{required_amount - amount:,} RBX**",
        inline=True
    )
    
    embed.add_field(
        name="Your Payout (70%)",
        value=f"**{amount:,} RBX**",
        inline=True
    )
    
    embed.add_field(
        name="Calculation",
        value=f"`{amount} ÷ 0.7 = {required_amount}` (rounded up)",
        inline=False
    )
    
    embed.set_footer(text=".pixel Design Services • Tax Calculator")
    
    await ctx.send(embed=embed)

@bot.tree.command(name="review", description="Submit a review for a designer (role restricted)")
@app_commands.describe(
    designer="The designer to review",
    product="The product or service being reviewed",
    rating="Rating out of 5 stars",
    remarks="Additional remarks about the experience"
)
@app_commands.choices(rating=rating_choices)
async def review_command(interaction: discord.Interaction, designer: discord.Member, product: str, rating: int, remarks: str):
    """Submit a review for a designer"""
    # Check if user has the required role
    user_role_ids = [role.id for role in interaction.user.roles]
    if REVIEW_ROLE_ID not in user_role_ids:
        await interaction.response.send_message("You don't have permission to submit reviews.", ephemeral=True)
        return
    
    # Validate designer selection
    if designer.bot:
        await interaction.response.send_message("You cannot review a bot.", ephemeral=True)
        return
    
    if designer == interaction.user:
        await interaction.response.send_message("You cannot review yourself.", ephemeral=True)
        return
    
    # Check if designer has any designer role
    if not has_designer_role(designer):
        await interaction.response.send_message("You can only review team members with designer roles.", ephemeral=True)
        return
    
    # Validate product length
    if len(product) < 3 or len(product) > 100:
        await interaction.response.send_message("Product/Service must be between 3 and 100 characters.", ephemeral=True)
        return
    
    # Validate remarks length
    if len(remarks) < 10 or len(remarks) > 1000:
        await interaction.response.send_message("Remarks must be between 10 and 1000 characters.", ephemeral=True)
        return
    
    # Create stars display
    stars = "<:pixelstar:1391507348618612766>" * rating
    empty_stars = "⭐" * (5 - rating)
    full_stars_display = stars + empty_stars
    
    # Create review embed
    embed = discord.Embed(
        title="⭐ Customer Review",
        description=f"A new review has been submitted for {designer.mention}",
        color=0x1B75BD,
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(
        name="Designer",
        value=f"{designer.mention} ({designer.name})",
        inline=True
    )
    
    embed.add_field(
        name="Product/Service",
        value=product,
        inline=True
    )
    
    embed.add_field(
        name="Rating",
        value=f"{full_stars_display} ({rating}/5)",
        inline=True
    )
    
    embed.add_field(
        name="Reviewer",
        value=f"{interaction.user.mention} ({interaction.user.name})",
        inline=True
    )
    
    embed.add_field(
        name="Remarks",
        value=remarks,
        inline=False
    )
    
    embed.set_footer(text=f"Review ID: {interaction.id}")
    
    # Send to review channel
    try:
        review_channel = interaction.guild.get_channel(REVIEW_CHANNEL_ID)
        if review_channel:
            await review_channel.send(embed=embed)
            await interaction.response.send_message("✅ Review submitted successfully!", ephemeral=True)
            
            # Log the review
            await log_review_submission_slash(interaction, designer, product, rating)
        else:
            await interaction.response.send_message("❌ Review channel not found.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error submitting review: {str(e)}", ephemeral=True)

async def log_review_submission_slash(interaction, designer, product, rating):
    """Log review submission to the logging channel (slash version)"""
    try:
        logging_channel = interaction.guild.get_channel(LOGGING_CHANNEL_ID)
        if logging_channel:
            embed = discord.Embed(
                title="⭐ Review Submitted",
                description=f"A new customer review has been submitted",
                color=0x1B75BD,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Designer", value=f"{designer.mention} ({designer.name})", inline=True)
            embed.add_field(name="Product", value=product, inline=True)
            embed.add_field(name="Rating", value=f"{rating}/5", inline=True)
            embed.add_field(name="Reviewer", value=f"{interaction.user.mention} ({interaction.user.name})", inline=True)
            embed.set_footer(text=f"Review ID: {interaction.id}")
            
            await logging_channel.send(embed=embed)
    except Exception as e:
        print(f"Error logging review submission: {e}")



@bot.command(name='review')
async def review_prefix(ctx, designer: discord.Member, rating: int, *, remarks: str):
    """Submit a review for a designer using prefix command"""
    # Check if user has the required role
    user_role_ids = [role.id for role in ctx.author.roles]
    if REVIEW_ROLE_ID not in user_role_ids:
        await ctx.message.delete()
        await ctx.send("You don't have permission to submit reviews.", delete_after=5)
        return
    
    # Validate rating
    if rating < 1 or rating > 5:
        await ctx.message.delete()
        await ctx.send("Rating must be between 1 and 5.", delete_after=5)
        return
    
    # Validate designer selection
    if designer.bot:
        await ctx.message.delete()
        await ctx.send("You cannot review a bot.", delete_after=5)
        return
    
    if designer == ctx.author:
        await ctx.message.delete()
        await ctx.send("You cannot review yourself.", delete_after=5)
        return
    
    # Check if designer has any designer role
    if not has_designer_role(designer):
        await ctx.message.delete()
        await ctx.send("You can only review team members with designer roles.", delete_after=5)
        return
    
    # Validate remarks length
    if len(remarks) < 10:
        await ctx.message.delete()
        await ctx.send("Remarks must be at least 10 characters long.", delete_after=5)
        return
    
    # Delete the command message
    await ctx.message.delete()
    
    # Create stars display
    stars = "<:pixelstar:1391507348618612766>" * rating
    empty_stars = "⭐" * (5 - rating)
    full_stars_display = stars + empty_stars
    
    # Create review embed
    embed = discord.Embed(
        title="⭐ Customer Review",
        description=f"A new review has been submitted for {designer.mention}",
        color=0x1B75BD,
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(
        name="Designer",
        value=f"{designer.mention} ({designer.name})",
        inline=True
    )
    
    embed.add_field(
        name="Rating",
        value=f"{full_stars_display} ({rating}/5)",
        inline=True
    )
    
    embed.add_field(
        name="Reviewer",
        value=f"{ctx.author.mention} ({ctx.author.name})",
        inline=True
    )
    
    embed.add_field(
        name="Remarks",
        value=remarks,
        inline=False
    )
    
    embed.set_footer(text=f"Review ID: {ctx.message.id}")
    
    # Send to review channel
    try:
        review_channel = ctx.guild.get_channel(REVIEW_CHANNEL_ID)
        if review_channel:
            await review_channel.send(embed=embed)
            await ctx.send("✅ Review submitted successfully!", delete_after=5)
            
            # Log the review
            await log_review_submission_prefix(ctx, designer, rating)
        else:
            await ctx.send("❌ Review channel not found.", delete_after=5)
    except Exception as e:
        await ctx.send(f"❌ Error submitting review: {str(e)}", delete_after=10)

async def log_review_submission_prefix(ctx, designer, rating):
    """Log review submission to the logging channel (prefix version)"""
    try:
        logging_channel = ctx.guild.get_channel(LOGGING_CHANNEL_ID)
        if logging_channel:
            embed = discord.Embed(
                title="⭐ Review Submitted",
                description=f"A new customer review has been submitted",
                color=0x1B75BD,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Designer", value=f"{designer.mention} ({designer.name})", inline=True)
            embed.add_field(name="Rating", value=f"{rating}/5", inline=True)
            embed.add_field(name="Reviewer", value=f"{ctx.author.mention} ({ctx.author.name})", inline=True)
            embed.set_footer(text=f"Review ID: {ctx.message.id}")
            
            await logging_channel.send(embed=embed)
    except Exception as e:
        print(f"Error logging review submission: {e}")

class WelcomeView(discord.ui.View):
    def __init__(self, member_count: int):
        super().__init__(timeout=None)
        self.member_count = member_count
    
    @discord.ui.button(label="📋 Server Information", style=discord.ButtonStyle.primary, custom_id="server_info")
    async def server_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "📋 **Server Information**\n\n"
            "Welcome to .pixel! Here you'll find everything you need to know about our design services.\n\n"
            "**Quick Links:**\n"
            "• <#1362585428183613587> - Server information and rules\n"
            "• <#1362585428510642325> - Order our design services\n"
            "• <#1362585429706019031> - View our work and updates\n\n"
            "Feel free to explore and ask any questions!",
            ephemeral=True
        )
    
    @discord.ui.button(label="👥 Member Count", style=discord.ButtonStyle.secondary, custom_id="member_count")
    async def member_count(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            f"👥 **Current Member Count:** {self.member_count:,} members\n\n"
            f"Thanks for being part of our growing community! 🎉",
            ephemeral=True
        )

class SupportSelectionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SupportTypeSelect())
    
    custom_id = "support_selection_view"

class SupportTypeSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="General Support",
                description="General questions, account issues, or basic assistance",
                value="general",
                emoji="🔧",
                default=False
            ),
            discord.SelectOption(
                label="High Rank Support",
                description="Complex issues, technical problems, or escalated matters",
                value="high_rank",
                emoji="⚡",
                default=False
            )
        ]
        
        super().__init__(
            placeholder="Select support type...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="support_type_select"
        )
    
    async def callback(self, interaction: discord.Interaction):
        try:
            support_type = self.values[0]
            await self.create_support_ticket(interaction, support_type)
        except Exception as e:
            print(f"Error in SupportTypeSelect callback: {e}")
            await interaction.response.send_message("An error occurred while processing your selection. Please try again.", ephemeral=True)
    
    async def create_support_ticket(self, interaction: discord.Interaction, support_type: str):
        try:
            guild = interaction.guild
            user = interaction.user
            
            # Check if user already has an open support ticket
            existing_unclaimed = discord.utils.get(guild.channels, name=f"unclaimed-{user.name.lower()}")
            existing_claimed = discord.utils.get(guild.channels, name=f"claimed-{user.name.lower()}")
            existing_resolved = discord.utils.get(guild.channels, name=f"resolved-{user.name.lower()}")
            
            if existing_unclaimed or existing_claimed or existing_resolved:
                existing_ticket = existing_unclaimed or existing_claimed or existing_resolved
                await interaction.response.send_message(
                    f"You already have an open ticket: {existing_ticket.mention}",
                    ephemeral=True
                )
                return
            
            # Determine category based on support type
            if support_type == "general":
                category_id = SUPPORT_GENERAL_CATEGORY_ID
                category_name = "General Support"
            else:  # high_rank
                category_id = SUPPORT_HIGH_RANK_CATEGORY_ID
                category_name = "High Rank Support"
            
            category = guild.get_channel(category_id)
            if not category:
                await interaction.response.send_message("Error: Support category not found.", ephemeral=True)
                return
            
            # Create ticket channel
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
            }
            
            # Add support role permissions
            support_role = guild.get_role(SUPPORT_ROLE_ID)
            if support_role:
                overwrites[support_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            
            # Add executive role permissions
            executive_role = guild.get_role(EXECUTIVE_ROLE_ID)
            if executive_role:
                overwrites[executive_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            
            # Add high rank role permissions
            high_rank_role = guild.get_role(HIGH_RANK_ROLE_ID)
            if high_rank_role:
                overwrites[high_rank_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            
            ticket_channel = await guild.create_text_channel(
                f"unclaimed-{user.name}",
                category=category,
                overwrites=overwrites,
                topic=f"{category_name} ticket for {user.mention}"
            )
            
            await self.send_support_welcome_message(ticket_channel, user, support_type)
            await interaction.response.send_message(
                f"Your {category_name} ticket has been created: {ticket_channel.mention}!",
                ephemeral=True
            )
        except Exception as e:
            print(f"Error creating support ticket: {e}")
            await interaction.response.send_message("An error occurred while creating your ticket. Please try again or contact support.", ephemeral=True)

    async def send_support_welcome_message(self, channel, user, support_type):
        try:
            # Get appropriate role mentions
            support_role_mention = ""
            if support_type == "general":
                support_role = channel.guild.get_role(SUPPORT_ROLE_ID)
                if support_role:
                    support_role_mention = support_role.mention
            else:  # high_rank
                high_rank_role = channel.guild.get_role(HIGH_RANK_ROLE_ID)
                if high_rank_role:
                    support_role_mention = high_rank_role.mention
            
            embed = discord.Embed(
                title=f"🎫 Welcome to your Support Ticket!",
                description=(
                    f"Hello {user.mention}! 👋\n\n"
                    f"**Welcome to your support ticket!**\n\n"
                    f"**📋 What happens next?**\n"
                    f"• Our support team will be with you shortly\n"
                    f"• Please describe your issue in detail\n"
                    f"• Include any relevant information or screenshots\n"
                    f"• We'll work to resolve your issue as quickly as possible\n\n"
                    f"**💡 Tips for faster support:**\n"
                    f"• Be specific about your issue\n"
                    f"• Provide any error messages or codes\n"
                    f"• Include steps to reproduce the problem\n"
                    f"• Be patient - we'll get to you as soon as possible\n\n"
                    f"**Support Type:** {support_type.replace('_', ' ').title()}\n\n"
                    f"Thank you for reaching out to us! 🙏"
                ),
                color=0x1B75BD,
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=f".pixel Support • Ticket ID: {channel.id}")
            
            # Create support ticket management view
            support_view = SupportTicketView()
            
            # Send pings first
            ping_message = f"Hey {user.mention}"
            if support_role_mention:
                ping_message += f", {support_role_mention} will be with you soon!"
            else:
                ping_message += ", our support team will be with you soon!"
            
            await channel.send(ping_message)
            
            # Send embed with management buttons
            await channel.send(embed=embed, view=support_view)
            
            # Log ticket creation
            await self.log_support_ticket_creation(channel, user, support_type)
        except Exception as e:
            print(f"Error sending support welcome message: {e}")
            try:
                await channel.send(f"Welcome {user.mention}! Please describe your issue.")
            except:
                pass
    
    async def log_support_ticket_creation(self, channel, user, support_type):
        """Log support ticket creation to the logging channel"""
        try:
            logging_channel = channel.guild.get_channel(LOGGING_CHANNEL_ID)
            if logging_channel:
                embed = discord.Embed(
                    title="🎫 New Support Ticket Created",
                    description=f"A new support ticket has been created",
                    color=0x6B8E6B,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="User", value=f"{user.mention} ({user.name})", inline=True)
                embed.add_field(name="Support Type", value=support_type.replace('_', ' ').title(), inline=True)
                embed.add_field(name="Channel", value=channel.mention, inline=True)
                embed.add_field(name="Status", value="🟡 Unclaimed", inline=True)
                embed.set_footer(text=f"Ticket ID: {channel.id}")
                
                await logging_channel.send(embed=embed)
        except Exception as e:
            print(f"Error logging support ticket creation: {e}")

class SupportTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Claim Ticket", style=discord.ButtonStyle.success, custom_id="claim_support_ticket")
    async def claim_support_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has support role
        if not has_support_role(interaction.user):
            await interaction.response.send_message("You don't have permission to claim support tickets.", ephemeral=True)
            return
        
        channel = interaction.channel
        
        # Check if ticket is already claimed
        if channel.name.startswith("claimed-"):
            await interaction.response.send_message("This ticket has already been claimed.", ephemeral=True)
            return
        
        # Rename channel
        try:
            await channel.edit(name=f"claimed-{interaction.user.name}")
            
            # Send claim message
            embed = discord.Embed(
                title="Ticket Claimed Successfully!",
                description=f"{interaction.user.mention} has claimed this support ticket!",
                color=0x6B8E6B,
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=".pixel Support")
            
            await channel.send(embed=embed)
            
            # Log claim
            await self.log_support_ticket_claim(channel, interaction.user)
            
            # Disable claim button
            button.disabled = True
            button.label = "Claimed"
            await interaction.response.edit_message(view=self)
            
        except Exception as e:
            await interaction.response.send_message(f"Error claiming ticket: {e}", ephemeral=True)
    
    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, custom_id="close_support_ticket")
    async def close_support_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has close privilege (support, high rank, or executive roles)
        if not has_support_privileged_role(interaction.user):
            await interaction.response.send_message("You don't have permission to close support tickets.", ephemeral=True)
            return
        
        # Create confirmation view
        confirm_view = SupportCloseConfirmationView()
        embed = discord.Embed(
            title="⚠️ Confirm Ticket Closure",
            description="Are you sure you want to close this support ticket? This action cannot be undone.",
            color=0x8E6B6B,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Click 'Confirm Close' to proceed")
        await interaction.response.send_message(embed=embed, view=confirm_view, ephemeral=True)
    
    @discord.ui.button(label="Escalate", style=discord.ButtonStyle.primary, custom_id="escalate_support_ticket")
    async def escalate_support_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has support role
        if not has_support_role(interaction.user):
            await interaction.response.send_message("You don't have permission to escalate support tickets.", ephemeral=True)
            return
        
        # Create escalation view
        escalation_view = EscalationView()
        embed = discord.Embed(
            title="📈 Escalate Ticket",
            description="Select where to escalate this ticket:",
            color=0x1B75BD,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Choose escalation destination")
        await interaction.response.send_message(embed=embed, view=escalation_view, ephemeral=True)
    
    async def log_support_ticket_claim(self, channel, user):
        """Log support ticket claim to the logging channel"""
        try:
            logging_channel = channel.guild.get_channel(LOGGING_CHANNEL_ID)
            if logging_channel:
                embed = discord.Embed(
                    title="🎯 Support Ticket Claimed",
                    description=f"A support ticket has been claimed by a team member",
                    color=0x6B8E6B,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Claimed By", value=f"{user.mention} ({user.name})", inline=True)
                embed.add_field(name="Channel", value=channel.mention, inline=True)
                embed.add_field(name="Status", value="🟢 Claimed", inline=True)
                embed.set_footer(text=f"Ticket ID: {channel.id}")
                
                await logging_channel.send(embed=embed)
        except Exception as e:
            print(f"Error logging support ticket claim: {e}")

class SupportCloseConfirmationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Confirm Close", style=discord.ButtonStyle.danger, custom_id="confirm_close_support")
    async def confirm_close_support(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has close privilege (support, high rank, or executive roles)
        if not has_support_privileged_role(interaction.user):
            await interaction.response.send_message("You don't have permission to close support tickets.", ephemeral=True)
            return
        
        channel = interaction.channel
        
        try:
            # Send closing message
            embed = discord.Embed(
                title="🔒 Support Ticket Closing",
                description="This support ticket will be closed in 10 seconds...",
                color=0x8E6B6B,
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=".pixel Support")
            await channel.send(embed=embed)
            
            # Send DM notification to ticket opener
            await send_ticket_closure_dm(channel, interaction.user, "support ticket")
            
            # Log closure
            await self.log_support_ticket_close(channel, interaction.user)
            await interaction.response.send_message("Support ticket will be closed in 10 seconds.", ephemeral=True)
            
            # Close after delay
            await asyncio.sleep(10)
            
            # Delete the channel with error handling
            try:
                await channel.delete()
                print(f"Successfully deleted support ticket channel: {channel.name}")
            except discord.Forbidden:
                print(f"Permission denied when trying to delete support ticket channel: {channel.name}")
                # Try to send a message to the channel instead
                try:
                    await channel.send("❌ **Error**: Unable to delete this channel due to insufficient permissions. Please contact an administrator.")
                except:
                    pass
            except discord.NotFound:
                print(f"Support ticket channel already deleted: {channel.name}")
            except Exception as e:
                print(f"Error deleting support ticket channel {channel.name}: {e}")
                # Try to send a message to the channel instead
                try:
                    await channel.send(f"❌ **Error**: Unable to delete this channel. Error: {str(e)}")
                except:
                    pass
                    
        except Exception as e:
            print(f"Error in support ticket close process: {e}")
            await interaction.response.send_message(f"An error occurred while closing the support ticket: {str(e)}", ephemeral=True)
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, custom_id="cancel_close_support")
    async def cancel_close_support(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Support ticket closure cancelled.", ephemeral=True)
    
    async def log_support_ticket_close(self, channel, user):
        """Log support ticket closure to the logging channel"""
        try:
            logging_channel = channel.guild.get_channel(LOGGING_CHANNEL_ID)
            if logging_channel:
                embed = discord.Embed(
                    title="🔒 Support Ticket Closed",
                    description=f"A support ticket has been closed by a team member",
                    color=0x8E6B6B,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Closed By", value=f"{user.mention} ({user.name})", inline=True)
                embed.add_field(name="Channel", value=f"#{channel.name}", inline=True)
                embed.add_field(name="Status", value="🔴 Closed", inline=True)
                embed.set_footer(text=f"Ticket ID: {channel.id}")
                
                await logging_channel.send(embed=embed)
        except Exception as e:
            print(f"Error logging support ticket close: {e}")

class EscalationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(EscalationSelect())
    
    custom_id = "escalation_view"

class EscalationSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="High Rank Support",
                description="Escalate to high rank support team",
                value="high_rank",
                emoji="⚡",
                default=False
            ),
            discord.SelectOption(
                label="Executive",
                description="Escalate to executive team",
                value="executive",
                emoji="👑",
                default=False
            )
        ]
        
        super().__init__(
            placeholder="Select escalation destination...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="escalation_select"
        )
    
    async def callback(self, interaction: discord.Interaction):
        try:
            escalation_type = self.values[0]
            await self.escalate_ticket(interaction, escalation_type)
        except Exception as e:
            print(f"Error in EscalationSelect callback: {e}")
            await interaction.response.send_message("An error occurred while processing escalation. Please try again.", ephemeral=True)
    
    async def escalate_ticket(self, interaction: discord.Interaction, escalation_type: str):
        try:
            channel = interaction.channel
            guild = channel.guild
            
            # Determine new category and role mentions
            if escalation_type == "high_rank":
                new_category_id = SUPPORT_HIGH_RANK_CATEGORY_ID
                role_id = HIGH_RANK_ROLE_ID
                escalation_name = "High Rank Support"
                ping_message = "⚡ High Rank Support has been notified!"
            else:  # executive
                new_category_id = EXECUTIVE_CHANNEL_ID
                role_id = EXECUTIVE_ROLE_ID
                escalation_name = "Executive"
                ping_message = "👑 Executive team has been notified!"
            
            # Get new category
            new_category = guild.get_channel(new_category_id)
            if not new_category:
                await interaction.response.send_message("Error: Escalation category not found.", ephemeral=True)
                return
            
            # Move channel to new category
            await channel.edit(category=new_category)
            
            # Get role for pinging
            role = guild.get_role(role_id)
            role_mention = role.mention if role else ""
            
            # Send escalation notification
            embed = discord.Embed(
                title="📈 Ticket Escalated",
                description=(
                    f"This ticket has been escalated to **{escalation_name}**.\n\n"
                    f"**Escalated by:** {interaction.user.mention}\n"
                    f"**New category:** {new_category.name}\n\n"
                    f"Please provide additional assistance as needed."
                ),
                color=0xFFA500,
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=".pixel Support • Escalation")
            
            # Send ping and embed
            if role_mention:
                await channel.send(f"{role_mention} {ping_message}")
            await channel.send(embed=embed)
            
            # Log escalation
            await self.log_ticket_escalation(channel, interaction.user, escalation_type)
            
            await interaction.response.send_message(f"Ticket escalated to {escalation_name} successfully!", ephemeral=True)
            
        except Exception as e:
            print(f"Error escalating ticket: {e}")
            await interaction.response.send_message(f"Error escalating ticket: {str(e)}", ephemeral=True)
    
    async def log_ticket_escalation(self, channel, user, escalation_type):
        """Log ticket escalation to the logging channel"""
        try:
            logging_channel = channel.guild.get_channel(LOGGING_CHANNEL_ID)
            if logging_channel:
                embed = discord.Embed(
                    title="📈 Support Ticket Escalated",
                    description=f"A support ticket has been escalated",
                    color=0xFFA500,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Escalated By", value=f"{user.mention} ({user.name})", inline=True)
                embed.add_field(name="Channel", value=channel.mention, inline=True)
                embed.add_field(name="Escalation Type", value=escalation_type.replace('_', ' ').title(), inline=True)
                embed.set_footer(text=f"Ticket ID: {channel.id}")
                
                await logging_channel.send(embed=embed)
        except Exception as e:
            print(f"Error logging ticket escalation: {e}")

class SupportTicketOrderView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Create Support Ticket", style=discord.ButtonStyle.primary, custom_id="create_support_ticket")
    async def create_support_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user already has an open ticket
        guild = interaction.guild
        user = interaction.user
        
        existing_ticket = discord.utils.get(guild.channels, 
                                          name=f"unclaimed-{user.name.lower()}")
        if existing_ticket:
            await interaction.response.send_message(
                f"You already have an open ticket: {existing_ticket.mention}",
                ephemeral=True
            )
            return
        
        # Show support type selection
        embed = discord.Embed(
            title="Select Support Type",
            description="Please choose the type of support you need:",
            color=0x1B75BD,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=".pixel Support • Choose your support type")
        
        await interaction.response.send_message(
            embed=embed,
            view=SupportSelectionView(),
            ephemeral=True
        )
    
    @discord.ui.button(label="Support Information", style=discord.ButtonStyle.secondary, custom_id="support_info")
    async def support_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="Support Information",
            description="How our support system works and what to expect.",
            color=0x1B75BD,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🔧 General Support",
            value="• Basic questions and assistance\n• General inquiries\n• Quick problem resolution",
            inline=False
        )
        
        embed.add_field(
            name="⚡ High Rank Support",
            value="• Complex technical issues\n• Escalated problems\n• Giveaways\n• Specialized assistance",
            inline=False
        )
        
        embed.add_field(
            name="👑 Executive Support",
            value="• Critical issues\n• Management concerns\n• Policy questions\n• Highest priority handling",
            inline=False
        )
        
        embed.add_field(
            name="What to Include",
            value="• Clear description of your issue\n• Relevant screenshots",
            inline=False
        )
        
        embed.set_footer(text=".pixel Support • We're here to help!")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class PackageClaimView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Claim Package", style=discord.ButtonStyle.primary, custom_id="claim_package")
    async def claim_package(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if package claims are enabled
        if not PACKAGE_CLAIM_ENABLED:
            embed = discord.Embed(
                title="📦 Package Claims Temporarily Unavailable",
                description=(
                    "**Package Orders Currently Unavailable**\n\n"
                    "We regret to inform you that we are currently unable to handle package orders at this time.\n\n"
                    "**What this means:**\n"
                    "• Package claiming functionality is temporarily suspended\n"
                    "• We are unable to process new package claims\n"
                    "• Existing package claims remain unaffected\n\n"
                    "**When will packages reopen?**\n"
                    "• Packages will reopen at a later date\n"
                    "• We will announce the reopening through our official channels\n"
                    "• Please stay tuned for updates\n\n"
                    "**We appreciate your understanding and patience.**\n"
                    "Thank you for your continued support!"
                ),
                color=0xFF6B6B,
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=".pixel Package Claims • Temporarily Unavailable")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check if user already has an open package claim ticket
        guild = interaction.guild
        user = interaction.user
        
        existing_ticket = discord.utils.get(guild.channels, name=f"package-claim-{user.name.lower()}")
        if existing_ticket:
            await interaction.response.send_message(
                f"You already have an open package claim ticket: {existing_ticket.mention}",
                ephemeral=True
            )
            return
        
        # Get package claim category
        category = guild.get_channel(PACKAGE_CLAIM_CATEGORY_ID)
        if not category:
            await interaction.response.send_message("Error: Package claim category not found.", ephemeral=True)
            return
        
        # Create package claim ticket channel
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }
        
        # Add support role permissions for staff to help
        support_role = guild.get_role(SUPPORT_ROLE_ID)
        if support_role:
            overwrites[support_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        
        # Add executive role permissions
        executive_role = guild.get_role(EXECUTIVE_ROLE_ID)
        if executive_role:
            overwrites[executive_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        
        # Add high rank role permissions
        high_rank_role = guild.get_role(HIGH_RANK_ROLE_ID)
        if high_rank_role:
            overwrites[high_rank_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        
        ticket_channel = await guild.create_text_channel(
            f"package-claim-{user.name}",
            category=category,
            overwrites=overwrites,
            topic=f"Package claim ticket for {user.mention}"
        )
        
        await self.send_package_claim_welcome_message(ticket_channel, user)
        await interaction.response.send_message(
            f"Your package claim ticket has been created: {ticket_channel.mention}!",
            ephemeral=True
        )
    
    def __init__(self):
        super().__init__(timeout=None)
        # Add the website button
        self.add_item(discord.ui.Button(label="View Website", style=discord.ButtonStyle.link, url="https://packsforyou.carrd.co/"))
    
    async def send_package_claim_welcome_message(self, channel, user):
        try:
            embed = discord.Embed(
                title="📦 Welcome to your Package Claim Ticket!",
                description=(
                    f"Hello {user.mention}! 👋\n\n"
                    f"**Welcome to your package claim ticket!**\n\n"
                    f"**📋 What we need from you:**\n"
                    f"• **Proof of Purchase**: Screenshot or receipt of your package purchase\n"
                    f"• **Package Details**: Which package you're claiming\n"
                    f"• **Any Additional Info**: Any specific requirements or questions\n\n"
                    f"**💡 Tips for faster processing:**\n"
                    f"• Make sure your proof of purchase is clear and readable\n"
                    f"• Include your username/email if it's not visible in the proof\n"
                    f"• Be specific about which package you purchased\n"
                    f"• Our staff will help you claim your package as soon as possible\n\n"
                    f"**Please provide the required information above so we can assist you!** 🚀\n\n"
                    f"Thank you for your purchase! 🙏"
                ),
                color=0x1B75BD,
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=f".pixel Package Claims • Ticket ID: {channel.id}")
            
            # Create package claim management view
            package_claim_view = PackageClaimManagementView()
            
            # Send pings first
            ping_message = f"Hey {user.mention}, our staff will be with you shortly to help with your package claim!"
            
            # Add management role ping
            management_ping = ""
            role = channel.guild.get_role(CO_EXECUTIVE_ROLE_ID)
            if role:
                management_ping += f"{role.mention} "
            
            if management_ping:
                ping_message += f"\n\n📦 **Package Claim Notification** {management_ping}"
            
            await channel.send(ping_message)
            
            # Send embed with management buttons
            await channel.send(embed=embed, view=package_claim_view)
            
            # Log package claim ticket creation
            await self.log_package_claim_creation(channel, user)
        except Exception as e:
            print(f"Error sending package claim welcome message: {e}")
            try:
                await channel.send(f"Welcome {user.mention}! Please provide proof of purchase and package details.")
            except:
                pass
    
    async def log_package_claim_creation(self, channel, user):
        """Log package claim ticket creation to the logging channel"""
        try:
            logging_channel = channel.guild.get_channel(LOGGING_CHANNEL_ID)
            if logging_channel:
                embed = discord.Embed(
                    title="📦 New Package Claim Ticket Created",
                    description=f"A new package claim ticket has been created",
                    color=0x6B8E6B,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="User", value=f"{user.mention} ({user.name})", inline=True)
                embed.add_field(name="Type", value="Package Claim", inline=True)
                embed.add_field(name="Channel", value=channel.mention, inline=True)
                embed.add_field(name="Status", value="🟡 Unclaimed", inline=True)
                embed.set_footer(text=f"Ticket ID: {channel.id}")
                
                await logging_channel.send(embed=embed)
        except Exception as e:
            print(f"Error logging package claim creation: {e}")

class PackageClaimManagementView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Claim Ticket", style=discord.ButtonStyle.success, custom_id="claim_package_ticket")
    async def claim_package_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has support role
        if not has_support_role(interaction.user):
            await interaction.response.send_message("You don't have permission to claim package claim tickets.", ephemeral=True)
            return
        
        channel = interaction.channel
        
        # Check if ticket is already claimed
        if channel.name.startswith("claimed-"):
            await interaction.response.send_message("This ticket has already been claimed.", ephemeral=True)
            return
        
        # Rename channel
        try:
            await channel.edit(name=f"claimed-{interaction.user.name}")
            
            # Send claim message
            embed = discord.Embed(
                title="Package Claim Ticket Claimed Successfully!",
                description=f"{interaction.user.mention} has claimed this package claim ticket!",
                color=0x6B8E6B,
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=".pixel Package Claims")
            
            await channel.send(embed=embed)
            
            # Log claim
            await self.log_package_claim_ticket_claim(channel, interaction.user)
            
            # Disable claim button
            button.disabled = True
            button.label = "Claimed"
            await interaction.response.edit_message(view=self)
            
        except Exception as e:
            await interaction.response.send_message(f"Error claiming ticket: {e}", ephemeral=True)
    
    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, custom_id="close_package_claim_ticket")
    async def close_package_claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has close privilege (support, high rank, or executive roles)
        if not has_support_privileged_role(interaction.user):
            await interaction.response.send_message("You don't have permission to close package claim tickets.", ephemeral=True)
            return
        
        # Create confirmation view
        confirm_view = PackageClaimCloseConfirmationView()
        embed = discord.Embed(
            title="⚠️ Confirm Ticket Closure",
            description=(
                f"Are you sure you want to close this package claim ticket?\n\n"
                f"This action cannot be undone and the channel will be archived.\n\n"
                f"**Closed by:** {interaction.user.mention}"
            ),
            color=0xFF6B6B,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=".pixel Package Claims • Confirmation Required")
        
        await interaction.response.send_message(embed=embed, view=confirm_view, ephemeral=True)
    
    async def log_package_claim_ticket_claim(self, channel, user):
        """Log package claim ticket claim to the logging channel"""
        try:
            logging_channel = channel.guild.get_channel(LOGGING_CHANNEL_ID)
            if logging_channel:
                embed = discord.Embed(
                    title="📦 Package Claim Ticket Claimed",
                    description=f"A package claim ticket has been claimed",
                    color=0x6B8E6B,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Claimed by", value=f"{user.mention} ({user.name})", inline=True)
                embed.add_field(name="Channel", value=channel.mention, inline=True)
                embed.add_field(name="Status", value="🟢 Claimed", inline=True)
                embed.set_footer(text=f"Ticket ID: {channel.id}")
                
                await logging_channel.send(embed=embed)
        except Exception as e:
            print(f"Error logging package claim ticket claim: {e}")

class PackageClaimCloseConfirmationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Confirm Close", style=discord.ButtonStyle.danger, custom_id="confirm_close_package_claim")
    async def confirm_close_package_claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has close privilege (support, high rank, or executive roles)
        if not has_support_privileged_role(interaction.user):
            await interaction.response.send_message("You don't have permission to close package claim tickets.", ephemeral=True)
            return
        
        channel = interaction.channel
        
        try:
            # Find the ticket opener
            ticket_opener_name = await find_ticket_opener(channel)
            
            # Send closure DM
            await send_ticket_closure_dm(channel, interaction.user, "package claim ticket")
            
            # Log ticket closure
            await self.log_package_claim_ticket_close(channel, interaction.user)
            
            # Send closure message
            embed = discord.Embed(
                title="📦 Package Claim Ticket Closed",
                description=(
                    f"This package claim ticket has been closed by {interaction.user.mention}.\n\n"
                    f"**Ticket opener:** {ticket_opener_name}\n"
                    f"**Closed by:** {interaction.user.mention}\n"
                    f"**Closed at:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n"
                    f"The channel will be deleted shortly."
                ),
                color=0xFF6B6B,
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=".pixel Package Claims • Ticket Closed")
            
            await channel.send(embed=embed)
            
            # Delete the channel after a delay
            await asyncio.sleep(5)
            
            # Delete the channel with error handling
            try:
                await channel.delete()
                print(f"Successfully deleted package claim ticket channel: {channel.name}")
            except discord.Forbidden:
                print(f"Permission denied when trying to delete package claim ticket channel: {channel.name}")
                # Try to send a message to the channel instead
                try:
                    await channel.send("❌ **Error**: Unable to delete this channel due to insufficient permissions. Please contact an administrator.")
                except:
                    pass
            except discord.NotFound:
                print(f"Package claim ticket channel already deleted: {channel.name}")
            except Exception as e:
                print(f"Error deleting package claim ticket channel {channel.name}: {e}")
                # Try to send a message to the channel instead
                try:
                    await channel.send(f"❌ **Error**: Unable to delete this channel. Error: {str(e)}")
                except:
                    pass
            
            await interaction.response.send_message("Package claim ticket closed successfully.", ephemeral=True)
            
        except Exception as e:
            print(f"Error in package claim ticket close process: {e}")
            await interaction.response.send_message(f"Error closing ticket: {e}", ephemeral=True)
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, custom_id="cancel_close_package_claim")
    async def cancel_close_package_claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ticket closure cancelled.", ephemeral=True)
    
    async def log_package_claim_ticket_close(self, channel, user):
        """Log package claim ticket closure to the logging channel"""
        try:
            logging_channel = channel.guild.get_channel(LOGGING_CHANNEL_ID)
            if logging_channel:
                embed = discord.Embed(
                    title="📦 Package Claim Ticket Closed",
                    description=f"A package claim ticket has been closed",
                    color=0xFF6B6B,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Closed by", value=f"{user.mention} ({user.name})", inline=True)
                embed.add_field(name="Channel", value=channel.mention, inline=True)
                embed.add_field(name="Status", value="🔴 Closed", inline=True)
                embed.set_footer(text=f"Ticket ID: {channel.id}")
                
                await logging_channel.send(embed=embed)
        except Exception as e:
            print(f"Error logging package claim ticket close: {e}")

def has_privileged_role(user):
    """Check if user has any manager or designer role"""
    return has_manager_role(user) or has_designer_role(user)

def has_support_role(user):
    """Check if user has any support role"""
    user_role_ids = [role.id for role in user.roles]
    return any(role_id in user_role_ids for role_id in SUPPORT_ROLE_IDS)

def has_support_privileged_role(user):
    """Check if user has any support, high rank, or executive role"""
    return has_support_role(user) or has_high_rank_role(user) or has_executive_role(user)

def has_high_rank_role(user):
    """Check if user has any high rank role"""
    user_role_ids = [role.id for role in user.roles]
    return any(role_id in user_role_ids for role_id in HIGH_RANK_ROLE_IDS)

def has_executive_role(user):
    """Check if user has any executive role"""
    user_role_ids = [role.id for role in user.roles]
    return any(role_id in user_role_ids for role_id in EXECUTIVE_ROLE_IDS)

@bot.tree.command(name="create-support-embed", description="Create the support embed (role restricted)")
async def slash_create_support_embed(interaction: discord.Interaction):
    """Slash command version of -se"""
    # Check if user has the required role
    if not has_support_privileged_role(interaction.user):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return
    
    # Check if command is used in the correct channel
    if interaction.channel.id != 1362585428183613589:
        await interaction.response.send_message("This command can only be used in the designated channel.", ephemeral=True)
        return
    
    # Create the main support embed
    embed = discord.Embed(
        title="🎫 .pixel Support Center",
        description=(
            "Need help? We're here to assist you! \n\n"
            "🔧 **Our Support Team**\n\n"
            "• **Professional Support Staff**: Experienced team ready to help\n"
            "• **Multiple Support Levels**: From general questions to complex issues\n"
            "• **Quick Response Times**: We prioritize your concerns\n"
            "• **Comprehensive Solutions**: We work to resolve issues completely\n"
            "• **24/7 Availability**: Support when you need it\n\n"
            "**Ready to get help?** \n\nClick the buttons below to create a support ticket or learn more about our support system."
        ),
        color=0x1B75BD,
    )
    
    embed.add_field(
        name="🔧 Support Types",
        value="General Support • High Rank Support • Executive Support",
        inline=False
    )
    
    embed.add_field(
        name="📋 What We Help With",
        value="• Account issues and questions\n• Technical problems and errors\n• Service inquiries and clarifications\n• Complex troubleshooting\n• Policy and management concerns",
        inline=False
    )
    
    embed.add_field(
        name="⏱️ Response Times",
        value="• General: 1-2 hours\n• High Rank: 30 minutes - 1 hour\n• Executive: 15-30 minutes",
        inline=False
    )
    
    embed.add_field(
        name="💡 Tips for Faster Support",
        value="• Be specific about your issue\n• Include error messages or codes\n• Provide steps to reproduce the problem\n• Add relevant screenshots when possible",
        inline=False
    )
    
    embed.set_footer(text="Professional Support Services • We're here to help!")
    
    # Send the embed with buttons
    await interaction.response.send_message(embed=embed, view=SupportTicketOrderView())

@bot.tree.command(name="create-package-claim-embed", description="Create the package claim embed (role restricted)")
async def slash_create_package_claim_embed(interaction: discord.Interaction):
    """Slash command version of -pe"""
    # Check if user has the required role
    if not has_support_privileged_role(interaction.user):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return
    
    # Check if command is used in the correct channel
    if interaction.channel.id != PACKAGE_CLAIM_CHANNEL_ID:
        await interaction.response.send_message("This command can only be used in the designated channel.", ephemeral=True)
        return
    
    # Create the main package claim embed
    if PACKAGE_CLAIM_ENABLED:
        embed = discord.Embed(
            title="📦 .pixel Package Claims",
            description=(
                "Ready to claim your purchased package? We're here to help! \n\n"
                "🎁 **Package Claim Process**\n\n"
                "• **Easy Claim Process**: Simple and straightforward package claiming\n"
                "• **Professional Support**: Our team will assist you with your claim\n"
                "• **Quick Processing**: We prioritize your package claims\n"
                "• **Secure Verification**: We ensure your purchase is verified\n"
                "• **Friendly Service**: Professional and helpful staff\n\n"
                "**Ready to claim your package?** \n\nClick the button below to start your package claim process."
            ),
            color=0x1B75BD,
        )
        
        embed.add_field(
            name="📋 What You'll Need",
            value="• Proof of purchase (screenshot/receipt)\n• Package details\n• Any additional requirements",
            inline=False
        )
        
        embed.add_field(
            name="⏱️ Processing Time",
            value="• Standard processing: 1-2 hours\n• Priority processing available",
            inline=False
        )
        
        embed.add_field(
            name="💡 Tips for Faster Processing",
            value="• Ensure proof of purchase is clear and readable\n• Include your username/email if not visible\n• Be specific about which package you purchased",
            inline=False
        )
        
        embed.set_footer(text="Professional Package Claims • We're here to help!")
    else:
        embed = discord.Embed(
            title="📦 .pixel Package Claims - Temporarily Unavailable",
            description=(
                "**Package Orders Currently Unavailable**\n\n"
                "We regret to inform you that we are currently unable to handle package orders at this time.\n\n"
                "**What this means:**\n"
                "• Package claiming functionality is temporarily suspended\n"
                "• We are unable to process new package claims\n"
                "• Existing package claims remain unaffected\n\n"
                "**When will packages reopen?**\n"
                "• Packages will reopen at a later date\n"
                "• We will announce the reopening through our official channels\n"
                "• Please stay tuned for updates\n\n"
                "**We appreciate your understanding and patience.**\n"
                "Thank you for your continued support!"
            ),
            color=0xFF6B6B,
        )
        
        embed.add_field(
            name="⏰ Status Update",
            value="• Package orders temporarily suspended\n• Reopening date to be announced\n• Stay tuned for official updates",
            inline=False
        )
        
        embed.add_field(
            name="📞 Support",
            value="• For urgent matters, please contact support\n• Existing claims will be processed as usual\n• We apologize for any inconvenience",
            inline=False
        )
        
        embed.set_footer(text="Professional Package Claims • Temporarily Unavailable")
    
    # Send the embed with buttons
    view = PackageClaimView()
    if not PACKAGE_CLAIM_ENABLED:
        # Disable the button when packages aren't available
        for child in view.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
                child.label = "Packages Temporarily Unavailable"
                child.style = discord.ButtonStyle.secondary
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="disable-package-claims", description="Disable package claim functionality (role restricted)")
async def slash_disable_package_claims(interaction: discord.Interaction):
    """Slash command version of -disable-package-claims"""
    global PACKAGE_CLAIM_ENABLED
    
    # Check if user has the required role
    if not has_support_privileged_role(interaction.user):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return
    
    # Check if command is used in the correct channel
    if interaction.channel.id != PACKAGE_CLAIM_CHANNEL_ID:
        await interaction.response.send_message("This command can only be used in the designated channel.", ephemeral=True)
        return
    
    # Disable package claims
    PACKAGE_CLAIM_ENABLED = False
    
    # Create confirmation embed
    embed = discord.Embed(
        title="📦 Package Claims Disabled",
        description=(
            f"Package claim functionality has been **disabled** by {interaction.user.mention}.\n\n"
            "**What this means:**\n"
            "• Users can no longer create package claim tickets\n"
            "• The 'Claim Package' button will show a 'temporarily unavailable' message\n"
            "• Existing tickets remain unaffected\n\n"
            "**To re-enable:** Use `-enable-package-claims` or `/enable-package-claims`"
        ),
        color=0xFF6B6B,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text=".pixel Package Claims • Management")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="enable-package-claims", description="Enable package claim functionality (role restricted)")
async def slash_enable_package_claims(interaction: discord.Interaction):
    """Slash command version of -enable-package-claims"""
    global PACKAGE_CLAIM_ENABLED
    
    # Check if user has the required role
    if not has_support_privileged_role(interaction.user):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return
    
    # Check if command is used in the correct channel
    if interaction.channel.id != PACKAGE_CLAIM_CHANNEL_ID:
        await interaction.response.send_message("This command can only be used in the designated channel.", ephemeral=True)
        return
    
    # Enable package claims
    PACKAGE_CLAIM_ENABLED = True
    
    # Create confirmation embed
    embed = discord.Embed(
        title="📦 Package Claims Enabled",
        description=(
            f"Package claim functionality has been **enabled** by {interaction.user.mention}.\n\n"
            "**What this means:**\n"
            "• Users can now create package claim tickets\n"
            "• The 'Claim Package' button is fully functional\n"
            "• Package claims are now live! 🎉\n\n"
            "**To disable:** Use `-disable-package-claims` or `/disable-package-claims`"
        ),
        color=0x6B8E6B,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text=".pixel Package Claims • Management")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="switch-claim", description="Switch the claim of a ticket to another person (support/design tickets)")
@app_commands.describe(new_claimer="The new person to claim the ticket")
async def slash_switch_claim(interaction: discord.Interaction, new_claimer: discord.Member):
    """Slash command version of -switch-claim"""
    # Check if user has the required role
    if not has_privileged_role(interaction.user) and not has_support_privileged_role(interaction.user):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return
    
    # Check if this is a ticket channel
    if not (interaction.channel.name.startswith('unclaimed-') or interaction.channel.name.startswith('claimed-')):
        await interaction.response.send_message("This command can only be used in ticket channels.", ephemeral=True)
        return
    
    # Check if new claimer has appropriate roles
    is_design_ticket = interaction.channel.category and interaction.channel.category.id in DESIGN_CATEGORY_IDS
    is_support_ticket = interaction.channel.category and (interaction.channel.category.id == SUPPORT_GENERAL_CATEGORY_ID or 
                                                         interaction.channel.category.id == SUPPORT_HIGH_RANK_CATEGORY_ID or
                                                         interaction.channel.category.id == EXECUTIVE_CHANNEL_ID)
    
    if is_design_ticket and not has_designer_role(new_claimer):
        await interaction.response.send_message("The new claimer must have designer roles for design tickets.", ephemeral=True)
        return
    
    if is_support_ticket and not has_support_role(new_claimer):
        await interaction.response.send_message("The new claimer must have support roles for support tickets.", ephemeral=True)
        return
    
    # Get current claimer from channel name
    current_claimer_name = None
    if interaction.channel.name.startswith('claimed-'):
        current_claimer_name = interaction.channel.name.split('-', 1)[1]
    
    # Rename channel
    try:
        await interaction.channel.edit(name=f"claimed-{new_claimer.name}")
        
        # Create switch claim embed
        embed = discord.Embed(
            title="🔄 Ticket Claim Switched",
            description=(
                f"This ticket has been reassigned to a new team member.\n\n"
                f"**Previous Claimer:** {current_claimer_name if current_claimer_name else 'Unclaimed'}\n"
                f"**New Claimer:** {new_claimer.mention} ({new_claimer.name})\n"
                f"**Switched by:** {interaction.user.mention} ({interaction.user.name})\n\n"
                f"Please continue working on this ticket."
            ),
            color=0x1B75BD,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=".pixel Support • Ticket Management")
        
        await interaction.channel.send(embed=embed)
        
        # Log the switch
        await log_claim_switch(interaction.channel, interaction.user, new_claimer, current_claimer_name)
        
        await interaction.response.send_message("✅ Ticket claim switched successfully!", ephemeral=True)
        
    except Exception as e:
        await interaction.response.send_message(f"Error switching claim: {str(e)}", ephemeral=True)

@bot.tree.command(name="switch-order", description="Switch the order ownership to a new designer (design tickets only)")
@app_commands.describe(new_designer="The new designer to take ownership of the order")
async def slash_switch_order_ownership(interaction: discord.Interaction, new_designer: discord.Member):
    """Slash command version of -switch-order"""
    # Check if user has the required role
    if not has_privileged_role(interaction.user):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return
    
    # Check if this is a design ticket
    if not interaction.channel.category or interaction.channel.category.id not in DESIGN_CATEGORY_IDS:
        await interaction.response.send_message("This command can only be used in design ticket channels.", ephemeral=True)
        return
    
    # Check if this is a ticket channel
    if not (interaction.channel.name.startswith('unclaimed-') or interaction.channel.name.startswith('claimed-')):
        await interaction.response.send_message("This command can only be used in ticket channels.", ephemeral=True)
        return
    
    # Check if new designer has designer roles
    if not has_designer_role(new_designer):
        await interaction.response.send_message("The new designer must have designer roles.", ephemeral=True)
        return
    
    # Get current designer from channel name
    current_designer_name = None
    if interaction.channel.name.startswith('claimed-'):
        current_designer_name = interaction.channel.name.split('-', 1)[1]
    
    # Update order details if they exist
    old_designer = None
    if interaction.channel.id in order_details:
        old_designer = order_details[interaction.channel.id]['designer']
        order_details[interaction.channel.id]['designer'] = new_designer
    
    # Rename channel
    try:
        await interaction.channel.edit(name=f"claimed-{new_designer.name}")
        
        # Create switch order embed
        embed = discord.Embed(
            title="🎨 Order Ownership Transferred",
            description=(
                f"This order has been transferred to a new designer.\n\n"
                f"**Previous Designer:** {current_designer_name if current_designer_name else 'Unclaimed'}\n"
                f"**New Designer:** {new_designer.mention} ({new_designer.name})\n"
                f"**Transferred by:** {interaction.user.mention} ({interaction.user.name})\n\n"
                f"**Order Details Updated:**\n"
                f"• Payment will now be logged to {new_designer.mention}\n"
                f"• All future order actions will be attributed to the new designer\n\n"
                f"Please continue working on this order with the same dedication and quality."
            ),
            color=0x00FF00,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=".pixel Design Services • Order Management")
        
        await interaction.channel.send(embed=embed)
        
        # Log the switch
        await log_order_ownership_switch(interaction.channel, interaction.user, new_designer, old_designer, current_designer_name)
        
        await interaction.response.send_message("✅ Order ownership switched successfully!", ephemeral=True)
        
    except Exception as e:
        await interaction.response.send_message(f"Error switching order ownership: {str(e)}", ephemeral=True)

async def log_claim_switch(channel, switcher, new_claimer, old_claimer_name):
    """Log claim switch to the logging channel"""
    try:
        logging_channel = channel.guild.get_channel(LOGGING_CHANNEL_ID)
        if logging_channel:
            embed = discord.Embed(
                title="🔄 Ticket Claim Switched",
                description=f"A ticket claim has been switched to a new team member",
                color=0x1B75BD,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Switched By", value=f"{switcher.mention} ({switcher.name})", inline=True)
            embed.add_field(name="New Claimer", value=f"{new_claimer.mention} ({new_claimer.name})", inline=True)
            embed.add_field(name="Channel", value=channel.mention, inline=True)
            embed.add_field(name="Previous Claimer", value=old_claimer_name if old_claimer_name else "Unclaimed", inline=True)
            embed.set_footer(text=f"Ticket ID: {channel.id}")
            
            await logging_channel.send(embed=embed)
    except Exception as e:
        print(f"Error logging claim switch: {e}")

async def log_order_ownership_switch(channel, switcher, new_designer, old_designer, old_designer_name):
    """Log order ownership switch to the logging channel"""
    try:
        logging_channel = channel.guild.get_channel(LOGGING_CHANNEL_ID)
        if logging_channel:
            embed = discord.Embed(
                title="🎨 Order Ownership Transferred",
                description=f"An order has been transferred to a new designer",
                color=0x00FF00,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Transferred By", value=f"{switcher.mention} ({switcher.name})", inline=True)
            embed.add_field(name="New Designer", value=f"{new_designer.mention} ({new_designer.name})", inline=True)
            embed.add_field(name="Channel", value=channel.mention, inline=True)
            embed.add_field(name="Previous Designer", value=old_designer_name if old_designer_name else "Unclaimed", inline=True)
            if old_designer:
                embed.add_field(name="Old Designer Object", value=f"{old_designer.mention} ({old_designer.name})", inline=True)
            embed.set_footer(text=f"Ticket ID: {channel.id}")
            
            await logging_channel.send(embed=embed)
    except Exception as e:
        print(f"Error logging order ownership switch: {e}")

async def find_ticket_opener(channel):
    """Find the user who opened the ticket based on channel name"""
    try:
        # Extract username from channel name (works for both unclaimed- and claimed- prefixes)
        if channel.name.startswith('unclaimed-'):
            username = channel.name.split('-', 1)[1]
        elif channel.name.startswith('claimed-'):
            username = channel.name.split('-', 1)[1]
        elif channel.name.startswith('finished-'):
            username = channel.name.split('-', 1)[1]
        elif channel.name.startswith('resolved-'):
            username = channel.name.split('-', 1)[1]
        else:
            return None
        
        # Find the user in the guild
        for member in channel.guild.members:
            if member.name.lower() == username.lower():
                return member
        
        return None
    except Exception as e:
        print(f"Error finding ticket opener: {e}")
        return None

async def send_ticket_closure_dm(channel, closer, ticket_type="ticket"):
    """Send DM notification to ticket opener about ticket closure"""
    try:
        ticket_opener = await find_ticket_opener(channel)
        if not ticket_opener:
            print(f"Could not find ticket opener for channel {channel.name}")
            return
        
        embed = discord.Embed(
            title=f"🔒 Your {ticket_type.title()} Has Been Closed",
            description=(
                f"Hello {ticket_opener.mention}!\n\n"
                f"Your {ticket_type} has been closed by our team.\n\n"
                f"**Ticket Details:**\n"
                f"• **Channel:** #{channel.name}\n"
                f"• **Closed by:** {closer.mention} ({closer.name})\n"
                f"• **Closure Time:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n"
                f"Thank you for using our services! If you have any further questions or need additional assistance, please don't hesitate to create a new ticket.\n\n"
                f"We appreciate your business and hope to serve you again soon! 🙏"
            ),
            color=0x8E6B6B,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f".pixel {'Support' if 'support' in ticket_type.lower() else 'Design Services'} • Ticket ID: {channel.id}")
        
        try:
            await ticket_opener.send(embed=embed)
            print(f"Sent closure DM to {ticket_opener.name} for ticket {channel.name}")
        except discord.Forbidden:
            print(f"Could not send DM to {ticket_opener.name} - DMs disabled")
        except Exception as e:
            print(f"Error sending DM to {ticket_opener.name}: {e}")
            
    except Exception as e:
        print(f"Error in send_ticket_closure_dm: {e}")

@bot.command(name='switch-claim')
async def switch_claim(ctx, new_claimer: discord.Member):
    """Switch the claim of a ticket to another person (support/design tickets)"""
    # Check if user has the required role
    if not has_privileged_role(ctx.author) and not has_support_privileged_role(ctx.author):
        await ctx.message.delete()
        await ctx.send("You don't have permission to use this command.", delete_after=5)
        return
    
    # Check if this is a ticket channel
    if not (ctx.channel.name.startswith('unclaimed-') or ctx.channel.name.startswith('claimed-')):
        await ctx.message.delete()
        await ctx.send("This command can only be used in ticket channels.", delete_after=5)
        return
    
    # Check if new claimer has appropriate roles
    is_design_ticket = ctx.channel.category and ctx.channel.category.id in DESIGN_CATEGORY_IDS
    is_support_ticket = ctx.channel.category and (ctx.channel.category.id == SUPPORT_GENERAL_CATEGORY_ID or 
                                                 ctx.channel.category.id == SUPPORT_HIGH_RANK_CATEGORY_ID or
                                                 ctx.channel.category.id == EXECUTIVE_CHANNEL_ID)
    
    if is_design_ticket and not has_designer_role(new_claimer):
        await ctx.message.delete()
        await ctx.send("The new claimer must have designer roles for design tickets.", delete_after=5)
        return
    
    if is_support_ticket and not has_support_role(new_claimer):
        await ctx.message.delete()
        await ctx.send("The new claimer must have support roles for support tickets.", delete_after=5)
        return
    
    # Get current claimer from channel name
    current_claimer_name = None
    if ctx.channel.name.startswith('claimed-'):
        current_claimer_name = ctx.channel.name.split('-', 1)[1]
    
    # Rename channel
    try:
        await ctx.channel.edit(name=f"claimed-{new_claimer.name}")
        
        # Create switch claim embed
        embed = discord.Embed(
            title="🔄 Ticket Claim Switched",
            description=(
                f"This ticket has been reassigned to a new team member.\n\n"
                f"**Previous Claimer:** {current_claimer_name if current_claimer_name else 'Unclaimed'}\n"
                f"**New Claimer:** {new_claimer.mention} ({new_claimer.name})\n"
                f"**Switched by:** {ctx.author.mention} ({ctx.author.name})\n\n"
                f"Please continue working on this ticket."
            ),
            color=0x1B75BD,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=".pixel Support • Ticket Management")
        
        await ctx.channel.send(embed=embed)
        
        # Log the switch
        await log_claim_switch(ctx.channel, ctx.author, new_claimer, current_claimer_name)
        
        await ctx.message.delete()
        await ctx.send("✅ Ticket claim switched successfully!", delete_after=3)
        
    except Exception as e:
        await ctx.message.delete()
        await ctx.send(f"Error switching claim: {str(e)}", delete_after=5)

@bot.command(name='switch-order')
async def switch_order_ownership(ctx, new_designer: discord.Member):
    """Switch the order ownership to a new designer (design tickets only)"""
    # Check if user has the required role
    if not has_privileged_role(ctx.author):
        await ctx.message.delete()
        await ctx.send("You don't have permission to use this command.", delete_after=5)
        return
    
    # Check if this is a design ticket
    if not ctx.channel.category or ctx.channel.category.id not in DESIGN_CATEGORY_IDS:
        await ctx.message.delete()
        await ctx.send("This command can only be used in design ticket channels.", delete_after=5)
        return
    
    # Check if this is a ticket channel
    if not (ctx.channel.name.startswith('unclaimed-') or ctx.channel.name.startswith('claimed-')):
        await ctx.message.delete()
        await ctx.send("This command can only be used in ticket channels.", delete_after=5)
        return
    
    # Check if new designer has designer roles
    if not has_designer_role(new_designer):
        await ctx.message.delete()
        await ctx.send("The new designer must have designer roles.", delete_after=5)
        return
    
    # Get current designer from channel name
    current_designer_name = None
    if ctx.channel.name.startswith('claimed-'):
        current_designer_name = ctx.channel.name.split('-', 1)[1]
    
    # Update order details if they exist
    old_designer = None
    if ctx.channel.id in order_details:
        old_designer = order_details[ctx.channel.id]['designer']
        order_details[ctx.channel.id]['designer'] = new_designer
    
    # Rename channel
    try:
        await ctx.channel.edit(name=f"claimed-{new_designer.name}")
        
        # Create switch order embed
        embed = discord.Embed(
            title="🎨 Order Ownership Transferred",
            description=(
                f"This order has been transferred to a new designer.\n\n"
                f"**Previous Designer:** {current_designer_name if current_designer_name else 'Unclaimed'}\n"
                f"**New Designer:** {new_designer.mention} ({new_designer.name})\n"
                f"**Transferred by:** {ctx.author.mention} ({ctx.author.name})\n\n"
                f"**Order Details Updated:**\n"
                f"• Payment will now be logged to {new_designer.mention}\n"
                f"• All future order actions will be attributed to the new designer\n\n"
                f"Please continue working on this order with the same dedication and quality."
            ),
            color=0x00FF00,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=".pixel Design Services • Order Management")
        
        await ctx.channel.send(embed=embed)
        
        # Log the switch
        await log_order_ownership_switch(ctx.channel, ctx.author, new_designer, old_designer, current_designer_name)
        
        await ctx.message.delete()
        await ctx.send("✅ Order ownership switched successfully!", delete_after=3)
        
    except Exception as e:
        await ctx.message.delete()
        await ctx.send(f"Error switching order ownership: {str(e)}", delete_after=5)

@bot.command(name='resolved')
async def resolve_support_ticket(ctx):
    """Mark the support ticket as resolved and rename the channel (support staff only)"""
    # Check if user has support privilege (support, high rank, or executive roles)
    if not has_support_privileged_role(ctx.author):
        await ctx.message.delete()
        await ctx.send("You don't have permission to resolve support tickets.", delete_after=5)
        return
    
    channel = ctx.channel
    
    # Only allow in support ticket categories
    is_support_ticket = channel.category and (channel.category.id == SUPPORT_GENERAL_CATEGORY_ID or 
                                             channel.category.id == SUPPORT_HIGH_RANK_CATEGORY_ID or
                                             channel.category.id == EXECUTIVE_CHANNEL_ID)
    
    if not is_support_ticket:
        await ctx.message.delete()
        await ctx.send("This command can only be used in support ticket channels.", delete_after=5)
        return
    
    # Check if this is a ticket channel
    if not (channel.name.startswith('unclaimed-') or channel.name.startswith('claimed-')):
        await ctx.message.delete()
        await ctx.send("This command can only be used in ticket channels.", delete_after=5)
        return
    
    # Get ticket opener from channel name
    ticket_opener_name = None
    if channel.name.startswith('unclaimed-'):
        ticket_opener_name = channel.name.split('-', 1)[1]
    elif channel.name.startswith('claimed-'):
        ticket_opener_name = channel.name.split('-', 1)[1]
    
    if not ticket_opener_name:
        await ctx.message.delete()
        await ctx.send("Could not determine ticket opener from channel name.", delete_after=5)
        return
    
    # Rename the channel to resolved-username
    try:
        await channel.edit(name=f"resolved-{ticket_opener_name}")
        
        # Send resolution message
        embed = discord.Embed(
            title="✅ Support Ticket Resolved!",
            description=(
                f"**This support ticket has been marked as resolved!** 🎉\n\n"
                f"We're glad we could help you with your issue.\n\n"
                f"**Resolution Details:**\n"
                f"• **Resolved by:** {ctx.author.mention} ({ctx.author.name})\n"
                f"• **Resolution Time:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
                f"• **Ticket ID:** {channel.id}\n\n"
                f"**What happens next?**\n"
                f"• This ticket will remain open for reference\n"
                f"• You can continue to ask questions if needed\n"
                f"• Feel free to create a new ticket for any new issues\n\n"
                f"Thank you for reaching out to us! We appreciate your patience and hope we resolved your issue satisfactorily. 🙏"
            ),
            color=0x6B8E6B,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=".pixel Support • Issue Resolved")
        
        await channel.send(embed=embed)
        
        # Send DM notification to ticket opener
        await send_support_resolution_dm(channel, ctx.author, ticket_opener_name)
        
        # Log the resolution
        await log_support_ticket_resolution(channel, ctx.author, ticket_opener_name)
        
        await ctx.message.delete()
        await ctx.send("✅ Support ticket marked as resolved!", delete_after=3)
        
    except Exception as e:
        await ctx.message.delete()
        await ctx.send(f"Error resolving ticket: {str(e)}", delete_after=5)

async def send_support_resolution_dm(channel, resolver, ticket_opener_name):
    """Send DM notification to ticket opener about ticket resolution"""
    try:
        ticket_opener = await find_ticket_opener(channel)
        if not ticket_opener:
            print(f"Could not find ticket opener {ticket_opener_name} for channel {channel.name}")
            return
        
        embed = discord.Embed(
            title="✅ Your Support Ticket Has Been Resolved!",
            description=(
                f"Hello {ticket_opener.mention}!\n\n"
                f"Great news! Your support ticket has been marked as resolved.\n\n"
                f"**Resolution Details:**\n"
                f"• **Channel:** #{channel.name}\n"
                f"• **Resolved by:** {resolver.mention} ({resolver.name})\n"
                f"• **Resolution Time:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
                f"• **Ticket ID:** {channel.id}\n\n"
                f"**What this means:**\n"
                f"• Your issue has been addressed and resolved\n"
                f"• The ticket remains open for your reference\n"
                f"• You can continue to ask follow-up questions if needed\n"
                f"• Feel free to create a new ticket for any new issues\n\n"
                f"Thank you for your patience and for choosing .pixel Support! 🙏\n\n"
                f"If you have any feedback about your support experience, we'd love to hear it!"
            ),
            color=0x6B8E6B,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=".pixel Support • Issue Resolved")
        
        try:
            await ticket_opener.send(embed=embed)
            print(f"Sent resolution DM to {ticket_opener.name} for ticket {channel.name}")
        except discord.Forbidden:
            print(f"Could not send DM to {ticket_opener.name} - DMs disabled")
        except Exception as e:
            print(f"Error sending DM to {ticket_opener.name}: {e}")
            
    except Exception as e:
        print(f"Error in send_support_resolution_dm: {e}")

async def log_support_ticket_resolution(channel, resolver, ticket_opener_name):
    """Log support ticket resolution to the logging channel"""
    try:
        logging_channel = channel.guild.get_channel(LOGGING_CHANNEL_ID)
        if logging_channel:
            embed = discord.Embed(
                title="✅ Support Ticket Resolved",
                description=f"A support ticket has been marked as resolved",
                color=0x6B8E6B,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Resolved By", value=f"{resolver.mention} ({resolver.name})", inline=True)
            embed.add_field(name="Channel", value=channel.mention, inline=True)
            embed.add_field(name="Ticket Opener", value=ticket_opener_name, inline=True)
            embed.add_field(name="Status", value="✅ Resolved", inline=True)
            embed.set_footer(text=f"Ticket ID: {channel.id}")
            
            await logging_channel.send(embed=embed)
    except Exception as e:
        print(f"Error logging support ticket resolution: {e}")

@bot.tree.command(name="resolved", description="Mark the support ticket as resolved (support staff only)")
async def slash_resolve_support_ticket(interaction: discord.Interaction):
    """Slash command version of -resolved"""
    # Check if user has support privilege (support, high rank, or executive roles)
    if not has_support_privileged_role(interaction.user):
        await interaction.response.send_message("You don't have permission to resolve support tickets.", ephemeral=True)
        return
    
    channel = interaction.channel
    
    # Only allow in support ticket categories
    is_support_ticket = channel.category and (channel.category.id == SUPPORT_GENERAL_CATEGORY_ID or 
                                             channel.category.id == SUPPORT_HIGH_RANK_CATEGORY_ID or
                                             channel.category.id == EXECUTIVE_CHANNEL_ID)
    
    if not is_support_ticket:
        await interaction.response.send_message("This command can only be used in support ticket channels.", ephemeral=True)
        return
    
    # Check if this is a ticket channel
    if not (channel.name.startswith('unclaimed-') or channel.name.startswith('claimed-')):
        await interaction.response.send_message("This command can only be used in ticket channels.", ephemeral=True)
        return
    
    # Get ticket opener from channel name
    ticket_opener_name = None
    if channel.name.startswith('unclaimed-'):
        ticket_opener_name = channel.name.split('-', 1)[1]
    elif channel.name.startswith('claimed-'):
        ticket_opener_name = channel.name.split('-', 1)[1]
    
    if not ticket_opener_name:
        await interaction.response.send_message("Could not determine ticket opener from channel name.", ephemeral=True)
        return
    
    # Rename the channel to resolved-username
    try:
        await channel.edit(name=f"resolved-{ticket_opener_name}")
        
        # Send resolution message
        embed = discord.Embed(
            title="✅ Support Ticket Resolved!",
            description=(
                f"**This support ticket has been marked as resolved!** 🎉\n\n"
                f"We're glad we could help you with your issue.\n\n"
                f"**Resolution Details:**\n"
                f"• **Resolved by:** {interaction.user.mention} ({interaction.user.name})\n"
                f"• **Resolution Time:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
                f"• **Ticket ID:** {channel.id}\n\n"
                f"**What happens next?**\n"
                f"• This ticket will remain open for reference\n"
                f"• You can continue to ask questions if needed\n"
                f"• Feel free to create a new ticket for any new issues\n\n"
                f"Thank you for reaching out to us! We appreciate your patience and hope we resolved your issue satisfactorily. 🙏"
            ),
            color=0x6B8E6B,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=".pixel Support • Issue Resolved")
        
        await channel.send(embed=embed)
        
        # Send DM notification to ticket opener
        await send_support_resolution_dm(channel, interaction.user, ticket_opener_name)
        
        # Log the resolution
        await log_support_ticket_resolution(channel, interaction.user, ticket_opener_name)
        
        await interaction.response.send_message("✅ Support ticket marked as resolved!", ephemeral=True)
        
    except Exception as e:
        await interaction.response.send_message(f"Error resolving ticket: {str(e)}", ephemeral=True)

@bot.command(name='delay')
async def delay_explanation(ctx):
    """Send a professional delay explanation embed (privileged only)"""
    if not has_privileged_role(ctx.author):
        await ctx.message.delete()
        await ctx.send("You don't have permission to use this command.", delete_after=5)
        return
    
    # Check if this is a design ticket
    if not ctx.channel.category or ctx.channel.category.id not in DESIGN_CATEGORY_IDS:
        await ctx.message.delete()
        await ctx.send("This command can only be used in design ticket channels.", delete_after=5)
        return
    
    # Check if this is a ticket channel
    if not (ctx.channel.name.startswith('unclaimed-') or ctx.channel.name.startswith('claimed-')):
        await ctx.message.delete()
        await ctx.send("This command can only be used in ticket channels.", delete_after=5)
        return
    
    await ctx.message.delete()
    
    embed = discord.Embed(
        title="⏳ Order Update: We Appreciate Your Patience!",
        description=(
            "Hello! 👋 We wanted to provide you with an update on your order status.\n\n"
            "**Current Situation:**\n"
            "We're currently experiencing either:\n"
            "• **High Volume of Orders**: We've received an exceptional number of orders recently\n"
            "• **Limited Designer Availability**: Our specialized designers for your service type are currently at capacity\n\n"
            "**What This Means:**\n"
            "• Your order is still in our queue and will be processed\n"
            "• We're working to assign the best designer for your project\n"
            "• Quality won't be compromised - we maintain our standards\n\n"
            "**What You Can Expect:**\n"
            "• We'll notify you as soon as your order is claimed\n"
            "• You'll receive regular updates on progress\n"
            "• We'll communicate any timeline adjustments promptly\n\n"
            "**We Value Your Business:**\n"
            "Thank you for choosing .pixel! We understand your time is valuable and appreciate your patience. We're committed to delivering exceptional results that exceed your expectations.\n\n"
            "If you have any questions or need clarification, please don't hesitate to ask!"
        ),
        color=0x1B75BD,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text=".pixel Design Services • We appreciate your patience!")
    await ctx.send(embed=embed)

@bot.command(name='eta-update')
async def update_eta(ctx, new_eta: str):
    """Update the ETA for a design order (privileged only)"""
    if not has_privileged_role(ctx.author):
        await ctx.message.delete()
        await ctx.send("You don't have permission to use this command.", delete_after=5)
        return
    
    # Check if this is a design ticket
    if not ctx.channel.category or ctx.channel.category.id not in DESIGN_CATEGORY_IDS:
        await ctx.message.delete()
        await ctx.send("This command can only be used in design ticket channels.", delete_after=5)
        return
    
    # Check if this is a ticket channel
    if not (ctx.channel.name.startswith('unclaimed-') or ctx.channel.name.startswith('claimed-')):
        await ctx.message.delete()
        await ctx.send("This command can only be used in ticket channels.", delete_after=5)
        return
    
    # Check if order details exist
    if ctx.channel.id not in order_details:
        await ctx.message.delete()
        await ctx.send("No order details found for this channel. Please ensure the order was started with /order-start or -os.", delete_after=5)
        return
    
    # Update the ETA
    old_eta = order_details[ctx.channel.id]['completion_time']
    order_details[ctx.channel.id]['completion_time'] = new_eta
    
    # Create ETA update embed
    embed = discord.Embed(
        title="📅 ETA Updated",
        description=(
            f"**The estimated completion time for your order has been updated.**\n\n"
            f"**Previous ETA:** {old_eta}\n"
            f"**New ETA:** {new_eta}\n"
            f"**Updated by:** {ctx.author.mention} ({ctx.author.name})\n\n"
            f"We'll work to meet this updated timeline and keep you informed of any further changes."
        ),
        color=0xFFA500,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text=".pixel Design Services • Order Management")
    
    await ctx.channel.send(embed=embed)
    
    # Log the ETA update
    await log_eta_update(ctx.channel, ctx.author, old_eta, new_eta)
    
    await ctx.message.delete()
    await ctx.send("✅ ETA updated successfully!", delete_after=3)

@bot.command(name='promote')
async def promote_user(ctx, user: discord.Member, *, reason: str):
    """Promote a user to the next role tier (management only)"""
    # Check if user has management role
    if not has_manager_role(ctx.author):
        await ctx.message.delete()
        await ctx.send("You don't have permission to promote users.", delete_after=5)
        return
    
    # Check if target is a bot
    if user.bot:
        await ctx.message.delete()
        await ctx.send("You cannot promote bots.", delete_after=5)
        return
    
    # Check if target is the same as promoter
    if user == ctx.author:
        await ctx.message.delete()
        await ctx.send("You cannot promote yourself.", delete_after=5)
        return
    
    # Get current role information
    target_dept, target_tier, current_role_id = get_user_role_tier(user)
    
    if not target_dept or target_dept == "EXECUTIVE":
        await ctx.message.delete()
        await ctx.send("This user cannot be promoted further or has no valid role tier.", delete_after=5)
        return
    
    # Check if promoter can promote this user
    if not can_promote_user(ctx.author, user):
        await ctx.message.delete()
        await ctx.send("You don't have permission to promote this user.", delete_after=5)
        return
    
    # Get next role
    next_role_id = get_next_role(target_dept, target_tier)
    if not next_role_id:
        await ctx.message.delete()
        await ctx.send("This user is already at the highest tier in their department.", delete_after=5)
        return
    
    try:
        # Remove current role and add new role
        current_role = ctx.guild.get_role(current_role_id)
        next_role = ctx.guild.get_role(next_role_id)
        
        if current_role and current_role in user.roles:
            await user.remove_roles(current_role)
        
        if next_role:
            await user.add_roles(next_role)
        
        # Check if this is a trial completion
        is_trial_completion = target_tier == "trial"
        
        # Create promotion embed
        embed = discord.Embed(
            title="📈 Promotion Successful!",
            description=(
                f"**{user.mention} has been promoted!** 🎉\n\n"
                f"**Previous Role:** {current_role.mention if current_role else 'None'}\n"
                f"**New Role:** {next_role.mention if next_role else 'None'}\n"
                f"**Promoted by:** {ctx.author.mention} ({ctx.author.name})\n"
                f"**Reason:** {reason}\n\n"
                f"{'🎉 **Trial Period Completed!** Welcome to the team!' if is_trial_completion else 'Congratulations on your promotion!'}"
            ),
            color=0x6B8E6B,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=".pixel Management • Promotion System")
        
        await ctx.send(embed=embed)
        
        # Log the promotion
        await log_promotion_action("promotion", ctx.author, user, reason, current_role_id, next_role_id)
        
        # Log trial completion if applicable
        if is_trial_completion:
            await log_trial_completion(user, next_role_id)
        
        await ctx.message.delete()
        
    except Exception as e:
        await ctx.message.delete()
        await ctx.send(f"Error promoting user: {str(e)}", delete_after=5)

@bot.command(name='demote')
async def demote_user(ctx, user: discord.Member, *, reason: str):
    """Demote a user to the previous role tier (management only)"""
    # Check if user has management role
    if not has_manager_role(ctx.author):
        await ctx.message.delete()
        await ctx.send("You don't have permission to demote users.", delete_after=5)
        return
    
    # Check if target is a bot
    if user.bot:
        await ctx.message.delete()
        await ctx.send("You cannot demote bots.", delete_after=5)
        return
    
    # Check if target is the same as demoter
    if user == ctx.author:
        await ctx.message.delete()
        await ctx.send("You cannot demote yourself.", delete_after=5)
        return
    
    # Get current role information
    target_dept, target_tier, current_role_id = get_user_role_tier(user)
    
    if not target_dept or target_dept == "EXECUTIVE":
        await ctx.message.delete()
        await ctx.send("This user cannot be demoted or has no valid role tier.", delete_after=5)
        return
    
    # Check if demoter can demote this user
    if not can_demote_user(ctx.author, user):
        await ctx.message.delete()
        await ctx.send("You don't have permission to demote this user.", delete_after=5)
        return
    
    # Get previous role
    prev_role_id = get_previous_role(target_dept, target_tier)
    if not prev_role_id:
        await ctx.message.delete()
        await ctx.send("This user is already at the lowest tier in their department.", delete_after=5)
        return
    
    try:
        # Remove current role and add new role
        current_role = ctx.guild.get_role(current_role_id)
        prev_role = ctx.guild.get_role(prev_role_id)
        
        if current_role and current_role in user.roles:
            await user.remove_roles(current_role)
        
        if prev_role:
            await user.add_roles(prev_role)
        
        # Create demotion embed
        embed = discord.Embed(
            title="📉 Demotion Action",
            description=(
                f"**{user.mention} has been demoted.**\n\n"
                f"**Previous Role:** {current_role.mention if current_role else 'None'}\n"
                f"**New Role:** {prev_role.mention if prev_role else 'None'}\n"
                f"**Demoted by:** {ctx.author.mention} ({ctx.author.name})\n"
                f"**Reason:** {reason}\n\n"
                f"This action has been logged for record keeping."
            ),
            color=0x8E6B6B,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=".pixel Management • Demotion System")
        
        await ctx.send(embed=embed)
        
        # Log the demotion
        await log_promotion_action("demotion", ctx.author, user, reason, current_role_id, prev_role_id)
        
        await ctx.message.delete()
        
    except Exception as e:
        await ctx.message.delete()
        await ctx.send(f"Error demoting user: {str(e)}", delete_after=5)

@bot.command(name='role-info')
async def role_info(ctx, user: discord.Member):
    """Get information about a user's role tier (management only)"""
    # Check if user has management role
    if not has_manager_role(ctx.author):
        await ctx.message.delete()
        await ctx.send("You don't have permission to view role information.", delete_after=5)
        return
    
    dept, tier, role_id = get_user_role_tier(user)
    
    if not dept:
        await ctx.message.delete()
        await ctx.send("This user has no valid role tier.", delete_after=5)
        return
    
    embed = discord.Embed(
        title="👤 Role Information",
        description=f"Role information for {user.mention}",
        color=0x1B75BD,
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(name="User", value=f"{user.mention} ({user.name})", inline=True)
    embed.add_field(name="Department", value=dept.title(), inline=True)
    embed.add_field(name="Current Tier", value=tier.replace('_', ' ').title(), inline=True)
    
    if dept in ROLE_HIERARCHY:
        tiers = list(ROLE_HIERARCHY[dept].keys())
        try:
            current_index = tiers.index(tier)
            if current_index < len(tiers) - 1:
                next_tier = tiers[current_index + 1]
                embed.add_field(name="Next Tier", value=next_tier.replace('_', ' ').title(), inline=True)
            else:
                embed.add_field(name="Next Tier", value="Maximum tier reached", inline=True)
            
            if current_index > 0:
                prev_tier = tiers[current_index - 1]
                embed.add_field(name="Previous Tier", value=prev_tier.replace('_', ' ').title(), inline=True)
            else:
                embed.add_field(name="Previous Tier", value="Minimum tier", inline=True)
        except ValueError:
            embed.add_field(name="Tier Position", value="Unknown", inline=True)
    
    embed.set_footer(text=".pixel Management • Role System")
    
    await ctx.send(embed=embed)
    await ctx.message.delete()

@bot.command(name='role-hierarchy')
async def show_role_hierarchy(ctx):
    """Show the complete role hierarchy (management only)"""
    # Check if user has management role
    if not has_manager_role(ctx.author):
        await ctx.message.delete()
        await ctx.send("You don't have permission to view role hierarchy.", delete_after=5)
        return
    
    embed = discord.Embed(
        title="🏗️ Role Hierarchy",
        description="Complete role hierarchy for all departments",
        color=0x1B75BD,
        timestamp=datetime.utcnow()
    )
    
    for department, roles in ROLE_HIERARCHY.items():
        hierarchy_text = ""
        for i, (tier, role_id) in enumerate(roles.items()):
            role_mention = f"<@&{role_id}>"
            if i == 0:
                hierarchy_text += f"🥇 **{tier.replace('_', ' ').title()}** - {role_mention}\n"
            elif i == len(roles) - 1:
                hierarchy_text += f"👑 **{tier.replace('_', ' ').title()}** - {role_mention}\n"
            else:
                hierarchy_text += f"📊 **{tier.replace('_', ' ').title()}** - {role_mention}\n"
        
        embed.add_field(
            name=f"📋 {department.title()}",
            value=hierarchy_text,
            inline=False
        )
    
    # Add co-executive information
    embed.add_field(
        name="👑 Executive",
        value=f"**Co-Executive** - <@&{CO_EXECUTIVE_ROLE_ID}>\n*Can promote/demote anyone*",
        inline=False
    )
    
    embed.set_footer(text=".pixel Management • Role Hierarchy")
    
    await ctx.send(embed=embed)
    await ctx.message.delete()

@bot.command(name='department-stats')
async def department_stats(ctx):
    """Show statistics for each department (management only)"""
    # Check if user has management role
    if not has_manager_role(ctx.author):
        await ctx.message.delete()
        await ctx.send("You don't have permission to view department statistics.", delete_after=5)
        return
    
    embed = discord.Embed(
        title="📊 Department Statistics",
        description="Current member counts by department and tier",
        color=0x1B75BD,
        timestamp=datetime.utcnow()
    )
    
    for department, roles in ROLE_HIERARCHY.items():
        dept_stats = ""
        total_members = 0
        
        for tier, role_id in roles.items():
            role = ctx.guild.get_role(role_id)
            if role:
                member_count = len(role.members)
                total_members += member_count
                dept_stats += f"• **{tier.replace('_', ' ').title()}**: {member_count} members\n"
        
        embed.add_field(
            name=f"📋 {department.title()} ({total_members} total)",
            value=dept_stats,
            inline=True
        )
    
    # Add co-executive count
    co_exec_role = ctx.guild.get_role(CO_EXECUTIVE_ROLE_ID)
    if co_exec_role:
        co_exec_count = len(co_exec_role.members)
        embed.add_field(
            name="👑 Executive",
            value=f"• **Co-Executive**: {co_exec_count} members",
            inline=True
        )
    
    embed.set_footer(text=".pixel Management • Department Statistics")
    
    await ctx.send(embed=embed)
    await ctx.message.delete()

async def log_eta_update(channel, updater, old_eta, new_eta):
    """Log ETA update to the logging channel"""
    try:
        logging_channel = channel.guild.get_channel(LOGGING_CHANNEL_ID)
        if logging_channel:
            embed = discord.Embed(
                title="📅 ETA Updated",
                description=f"An order ETA has been updated",
                color=0xFFA500,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Updated By", value=f"{updater.mention} ({updater.name})", inline=True)
            embed.add_field(name="Channel", value=channel.mention, inline=True)
            embed.add_field(name="Previous ETA", value=old_eta, inline=True)
            embed.add_field(name="New ETA", value=new_eta, inline=True)
            embed.set_footer(text=f"Ticket ID: {channel.id}")
            
            await logging_channel.send(embed=embed)
    except Exception as e:
        print(f"Error logging ETA update: {e}")

@bot.tree.command(name="delay-explanation", description="Send a professional delay explanation (role restricted)")
async def slash_delay_explanation(interaction: discord.Interaction):
    """Slash command version of -de"""
    # Check if user has the required role
    if not has_privileged_role(interaction.user):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return
    
    # Check if this is a design ticket
    if not interaction.channel.category or interaction.channel.category.id not in DESIGN_CATEGORY_IDS:
        await interaction.response.send_message("This command can only be used in design ticket channels.", ephemeral=True)
        return
    
    # Check if this is a ticket channel
    if not (interaction.channel.name.startswith('unclaimed-') or interaction.channel.name.startswith('claimed-')):
        await interaction.response.send_message("This command can only be used in ticket channels.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="⏳ Order Update: We Appreciate Your Patience!",
        description=(
            "Hello! 👋 We wanted to provide you with an update on your order status.\n\n"
            "**Current Situation:**\n"
            "We're currently experiencing either:\n"
            "• **High Volume of Orders**: We've received an exceptional number of orders recently\n"
            "• **Limited Designer Availability**: Our specialized designers for your service type are currently at capacity\n\n"
            "**What This Means:**\n"
            "• Your order is still in our queue and will be processed\n"
            "• We're working to assign the best designer for your project\n"
            "• Quality won't be compromised - we maintain our standards\n\n"
            "**What You Can Expect:**\n"
            "• We'll notify you as soon as your order is claimed\n"
            "• You'll receive regular updates on progress\n"
            "• We'll communicate any timeline adjustments promptly\n\n"
            "**We Value Your Business:**\n"
            "Thank you for choosing .pixel! We understand your time is valuable and appreciate your patience. We're committed to delivering exceptional results that exceed your expectations.\n\n"
            "If you have any questions or need clarification, please don't hesitate to ask!"
        ),
        color=0x1B75BD,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text=".pixel Design Services • We appreciate your patience!")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="eta-update", description="Update the ETA for a design order (role restricted)")
@app_commands.describe(new_eta="The new estimated completion time")
async def slash_eta_update(interaction: discord.Interaction, new_eta: str):
    """Slash command version of -eta-update"""
    # Check if user has the required role
    if not has_privileged_role(interaction.user):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return
    
    # Check if this is a design ticket
    if not interaction.channel.category or interaction.channel.category.id not in DESIGN_CATEGORY_IDS:
        await interaction.response.send_message("This command can only be used in design ticket channels.", ephemeral=True)
        return
    
    # Check if this is a ticket channel
    if not (interaction.channel.name.startswith('unclaimed-') or interaction.channel.name.startswith('claimed-')):
        await interaction.response.send_message("This command can only be used in ticket channels.", ephemeral=True)
        return
    
    # Check if order details exist
    if interaction.channel.id not in order_details:
        await interaction.response.send_message("No order details found for this channel. Please ensure the order was started with /order-start or -os.", ephemeral=True)
        return
    
    # Update the ETA
    old_eta = order_details[interaction.channel.id]['completion_time']
    order_details[interaction.channel.id]['completion_time'] = new_eta
    
    # Create ETA update embed
    embed = discord.Embed(
        title="📅 ETA Updated",
        description=(
            f"**The estimated completion time for your order has been updated.**\n\n"
            f"**Previous ETA:** {old_eta}\n"
            f"**New ETA:** {new_eta}\n"
            f"**Updated by:** {interaction.user.mention} ({interaction.user.name})\n\n"
            f"We'll work to meet this updated timeline and keep you informed of any further changes."
        ),
        color=0xFFA500,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text=".pixel Design Services • Order Management")
    
    await interaction.channel.send(embed=embed)
    
    # Log the ETA update
    await log_eta_update(interaction.channel, interaction.user, old_eta, new_eta)
    
    await interaction.response.send_message("✅ ETA updated successfully!", ephemeral=True)

@bot.tree.command(name="promote", description="Promote a user to the next role tier (management only)")
@app_commands.describe(
    user="The user to promote",
    reason="Reason for the promotion"
)
async def slash_promote(interaction: discord.Interaction, user: discord.Member, reason: str):
    """Promote a user to the next role tier"""
    # Check if user has management role
    if not has_manager_role(interaction.user):
        await interaction.response.send_message("You don't have permission to promote users.", ephemeral=True)
        return
    
    # Check if target is a bot
    if user.bot:
        await interaction.response.send_message("You cannot promote bots.", ephemeral=True)
        return
    
    # Check if target is the same as promoter
    if user == interaction.user:
        await interaction.response.send_message("You cannot promote yourself.", ephemeral=True)
        return
    
    # Get current role information
    target_dept, target_tier, current_role_id = get_user_role_tier(user)
    
    if not target_dept or target_dept == "EXECUTIVE":
        await interaction.response.send_message("This user cannot be promoted further or has no valid role tier.", ephemeral=True)
        return
    
    # Check if promoter can promote this user
    if not can_promote_user(interaction.user, user):
        await interaction.response.send_message("You don't have permission to promote this user.", ephemeral=True)
        return
    
    # Get next role
    next_role_id = get_next_role(target_dept, target_tier)
    if not next_role_id:
        await interaction.response.send_message("This user is already at the highest tier in their department.", ephemeral=True)
        return
    
    try:
        # Remove current role and add new role
        current_role = interaction.guild.get_role(current_role_id)
        next_role = interaction.guild.get_role(next_role_id)
        
        if current_role and current_role in user.roles:
            await user.remove_roles(current_role)
        
        if next_role:
            await user.add_roles(next_role)
        
        # Check if this is a trial completion
        is_trial_completion = target_tier == "trial"
        
        # Create promotion embed
        embed = discord.Embed(
            title="📈 Promotion Successful!",
            description=(
                f"**{user.mention} has been promoted!** 🎉\n\n"
                f"**Previous Role:** {current_role.mention if current_role else 'None'}\n"
                f"**New Role:** {next_role.mention if next_role else 'None'}\n"
                f"**Promoted by:** {interaction.user.mention} ({interaction.user.name})\n"
                f"**Reason:** {reason}\n\n"
                f"{'🎉 **Trial Period Completed!** Welcome to the team!' if is_trial_completion else 'Congratulations on your promotion!'}"
            ),
            color=0x6B8E6B,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=".pixel Management • Promotion System")
        
        await interaction.response.send_message(embed=embed)
        
        # Log the promotion
        await log_promotion_action("promotion", interaction.user, user, reason, current_role_id, next_role_id)
        
        # Log trial completion if applicable
        if is_trial_completion:
            await log_trial_completion(user, next_role_id)
        
    except Exception as e:
        await interaction.response.send_message(f"Error promoting user: {str(e)}", ephemeral=True)

@bot.tree.command(name="demote", description="Demote a user to the previous role tier (management only)")
@app_commands.describe(
    user="The user to demote",
    reason="Reason for the demotion"
)
async def slash_demote(interaction: discord.Interaction, user: discord.Member, reason: str):
    """Demote a user to the previous role tier"""
    # Check if user has management role
    if not has_manager_role(interaction.user):
        await interaction.response.send_message("You don't have permission to demote users.", ephemeral=True)
        return
    
    # Check if target is a bot
    if user.bot:
        await interaction.response.send_message("You cannot demote bots.", ephemeral=True)
        return
    
    # Check if target is the same as demoter
    if user == interaction.user:
        await interaction.response.send_message("You cannot demote yourself.", ephemeral=True)
        return
    
    # Get current role information
    target_dept, target_tier, current_role_id = get_user_role_tier(user)
    
    if not target_dept or target_dept == "EXECUTIVE":
        await interaction.response.send_message("This user cannot be demoted or has no valid role tier.", ephemeral=True)
        return
    
    # Check if demoter can demote this user
    if not can_demote_user(interaction.user, user):
        await interaction.response.send_message("You don't have permission to demote this user.", ephemeral=True)
        return
    
    # Get previous role
    prev_role_id = get_previous_role(target_dept, target_tier)
    if not prev_role_id:
        await interaction.response.send_message("This user is already at the lowest tier in their department.", ephemeral=True)
        return
    
    try:
        # Remove current role and add new role
        current_role = interaction.guild.get_role(current_role_id)
        prev_role = interaction.guild.get_role(prev_role_id)
        
        if current_role and current_role in user.roles:
            await user.remove_roles(current_role)
        
        if prev_role:
            await user.add_roles(prev_role)
        
        # Create demotion embed
        embed = discord.Embed(
            title="📉 Demotion Action",
            description=(
                f"**{user.mention} has been demoted.**\n\n"
                f"**Previous Role:** {current_role.mention if current_role else 'None'}\n"
                f"**New Role:** {prev_role.mention if prev_role else 'None'}\n"
                f"**Demoted by:** {interaction.user.mention} ({interaction.user.name})\n"
                f"**Reason:** {reason}\n\n"
                f"This action has been logged for record keeping."
            ),
            color=0x8E6B6B,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=".pixel Management • Demotion System")
        
        await interaction.response.send_message(embed=embed)
        
        # Log the demotion
        await log_promotion_action("demotion", interaction.user, user, reason, current_role_id, prev_role_id)
        
    except Exception as e:
        await interaction.response.send_message(f"Error demoting user: {str(e)}", ephemeral=True)

@bot.tree.command(name="role-info", description="Get information about a user's role tier")
@app_commands.describe(user="The user to check")
async def slash_role_info(interaction: discord.Interaction, user: discord.Member):
    """Get information about a user's role tier"""
    # Check if user has management role
    if not has_manager_role(interaction.user):
        await interaction.response.send_message("You don't have permission to view role information.", ephemeral=True)
        return
    
    dept, tier, role_id = get_user_role_tier(user)
    
    if not dept:
        await interaction.response.send_message("This user has no valid role tier.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="👤 Role Information",
        description=f"Role information for {user.mention}",
        color=0x1B75BD,
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(name="User", value=f"{user.mention} ({user.name})", inline=True)
    embed.add_field(name="Department", value=dept.title(), inline=True)
    embed.add_field(name="Current Tier", value=tier.replace('_', ' ').title(), inline=True)
    
    if dept in ROLE_HIERARCHY:
        tiers = list(ROLE_HIERARCHY[dept].keys())
        try:
            current_index = tiers.index(tier)
            if current_index < len(tiers) - 1:
                next_tier = tiers[current_index + 1]
                embed.add_field(name="Next Tier", value=next_tier.replace('_', ' ').title(), inline=True)
            else:
                embed.add_field(name="Next Tier", value="Maximum tier reached", inline=True)
            
            if current_index > 0:
                prev_tier = tiers[current_index - 1]
                embed.add_field(name="Previous Tier", value=prev_tier.replace('_', ' ').title(), inline=True)
            else:
                embed.add_field(name="Previous Tier", value="Minimum tier", inline=True)
        except ValueError:
            embed.add_field(name="Tier Position", value="Unknown", inline=True)
    
    embed.set_footer(text=".pixel Management • Role System")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
@bot.tree.command(name="activity-check", description="Check activity of designer and support role members (executives, HR, and managers only)")
@app_commands.describe(days="Number of days to check activity for (default: 7)")
async def activity_check(interaction: discord.Interaction, days: int = 7):
    """Check activity of designer and support role members over specified days"""
    # Check if user has executive, HR, or manager role
    if not (has_executive_role(interaction.user) or has_high_rank_role(interaction.user) or has_manager_role(interaction.user)):
        await interaction.response.send_message("You don't have permission to use this command. Only executives, HR, and managers can use this command.", ephemeral=True)
        return
    
    # Validate days parameter
    if days < 1 or days > 365:
        await interaction.response.send_message("Please specify a number of days between 1 and 365.", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    try:
        guild = interaction.guild
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        # Get all members with designer or support roles
        target_members = []
        all_role_ids = DESIGNER_ROLE_IDS + SUPPORT_ROLE_IDS
        
        for member in guild.members:
            member_role_ids = [role.id for role in member.roles]
            if any(role_id in member_role_ids for role_id in all_role_ids):
                target_members.append(member)
        
        if not target_members:
            embed = discord.Embed(
                title="No Target Members Found",
                description="No members with designer or support roles were found in this server.",
                color=0xFFA500,
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=".pixel Design Services • Activity Check")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Check message activity for each member
        inactive_members = []
        total_messages = 0
        
        for member in target_members:
            message_count = 0
            
            # Check messages in all text channels
            for channel in guild.text_channels:
                try:
                    # Check if bot has permission to read message history
                    if not channel.permissions_for(guild.me).read_message_history:
                        continue
                    
                    # Count messages from this member since cutoff time
                    async for message in channel.history(limit=None, after=cutoff_time):
                        if message.author.id == member.id:
                            message_count += 1
                            total_messages += 1
                            
                            # Stop counting if they have more than 2 messages
                            if message_count > 2:
                                break
                    
                    # If member already has more than 2 messages, no need to check other channels
                    if message_count > 2:
                        break
                        
                except discord.Forbidden:
                    # Skip channels where bot doesn't have permission
                    continue
                except Exception as e:
                    print(f"Error checking messages in {channel.name}: {e}")
                    continue
            
            # If member has 2 or fewer messages, add to inactive list
            if message_count <= 2:
                inactive_members.append({
                    'member': member,
                    'message_count': message_count,
                    'roles': [role.name for role in member.roles if role.id in all_role_ids]
                })
        
        # Create embed with results
        embed = discord.Embed(
            title="📊 Activity Check Results",
            description=f"Activity check for the last **{days} days**",
            color=0x1B75BD,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📈 Overall Statistics",
            value=f"• **Total members checked:** {len(target_members)}\n"
                  f"• **Total messages sent:** {total_messages}\n"
                  f"• **Inactive members (≤2 messages):** {len(inactive_members)}",
            inline=False
        )
        
        if inactive_members:
            # Sort by message count (ascending)
            inactive_members.sort(key=lambda x: x['message_count'])
            
            # Create list of inactive members
            inactive_list = []
            for i, data in enumerate(inactive_members[:20], 1):  # Limit to 20 for embed
                member = data['member']
                message_count = data['message_count']
                roles = ', '.join(data['roles'])
                
                inactive_list.append(
                    f"**{i}.** {member.mention} (`{member.id}`)\n"
                    f"   • Messages: {message_count}\n"
                    f"   • Roles: {roles}"
                )
            
            inactive_text = "\n\n".join(inactive_list)
            
            if len(inactive_members) > 20:
                inactive_text += f"\n\n*...and {len(inactive_members) - 20} more members*"
            
            embed.add_field(
                name=f"⚠️ Inactive Members ({len(inactive_members)})",
                value=inactive_text,
                inline=False
            )
        else:
            embed.add_field(
                name="✅ All Members Active",
                value="All designer and support role members have sent more than 2 messages in the specified time period.",
                inline=False
            )
        
        embed.add_field(
            name="📋 Check Details",
            value=f"• **Time period:** {days} days\n"
                  f"• **Cutoff date:** {cutoff_time.strftime('%Y-%m-%d %H:%M UTC')}\n"
                  f"• **Checked by:** {interaction.user.mention}",
            inline=False
        )
        
        embed.set_footer(text=".pixel Design Services • Activity Check")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error During Activity Check",
            description=f"An error occurred while performing the activity check:\n```{str(e)}```",
            color=0x8E6B6B,
            timestamp=datetime.utcnow()
        )
        error_embed.set_footer(text=".pixel Design Services • Activity Check")
        await interaction.followup.send(embed=error_embed, ephemeral=True)


@bot.tree.command(name="role-hierarchy", description="Show the complete role hierarchy (management only)")
async def slash_role_hierarchy(interaction: discord.Interaction):
    """Show the complete role hierarchy"""
    # Check if user has management role
    if not has_manager_role(interaction.user):
        await interaction.response.send_message("You don't have permission to view role hierarchy.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🏗️ Role Hierarchy",
        description="Complete role hierarchy for all departments",
        color=0x1B75BD,
        timestamp=datetime.utcnow()
    )
    
    for department, roles in ROLE_HIERARCHY.items():
        hierarchy_text = ""
        for i, (tier, role_id) in enumerate(roles.items()):
            role_mention = f"<@&{role_id}>"
            if i == 0:
                hierarchy_text += f"🥇 **{tier.replace('_', ' ').title()}** - {role_mention}\n"
            elif i == len(roles) - 1:
                hierarchy_text += f"👑 **{tier.replace('_', ' ').title()}** - {role_mention}\n"
            else:
                hierarchy_text += f"📊 **{tier.replace('_', ' ').title()}** - {role_mention}\n"
        
        embed.add_field(
            name=f"📋 {department.title()}",
            value=hierarchy_text,
            inline=False
        )
    
    # Add co-executive information
    embed.add_field(
        name="👑 Executive",
        value=f"**Co-Executive** - <@&{CO_EXECUTIVE_ROLE_ID}>\n*Can promote/demote anyone*",
        inline=False
    )
    
    embed.set_footer(text=".pixel Management • Role Hierarchy")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="department-stats", description="Show statistics for each department (management only)")
async def slash_department_stats(interaction: discord.Interaction):
    """Show statistics for each department"""
    # Check if user has management role
    if not has_manager_role(interaction.user):
        await interaction.response.send_message("You don't have permission to view department statistics.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="📊 Department Statistics",
        description="Current member counts by department and tier",
        color=0x1B75BD,
        timestamp=datetime.utcnow()
    )
    
    for department, roles in ROLE_HIERARCHY.items():
        dept_stats = ""
        total_members = 0
        
        for tier, role_id in roles.items():
            role = interaction.guild.get_role(role_id)
            if role:
                member_count = len(role.members)
                total_members += member_count
                dept_stats += f"• **{tier.replace('_', ' ').title()}**: {member_count} members\n"
        
        embed.add_field(
            name=f"📋 {department.title()} ({total_members} total)",
            value=dept_stats,
            inline=True
        )
    
    # Add co-executive count
    co_exec_role = interaction.guild.get_role(CO_EXECUTIVE_ROLE_ID)
    if co_exec_role:
        co_exec_count = len(co_exec_role.members)
        embed.add_field(
            name="👑 Executive",
            value=f"• **Co-Executive**: {co_exec_count} members",
            inline=True
        )
    
    embed.set_footer(text=".pixel Management • Department Statistics")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="strike", description="Give a strike to a user (high privilege only)")
@app_commands.describe(
    user="The user to give a strike to",
    reason="Reason for the strike"
)
async def slash_strike(interaction: discord.Interaction, user: discord.Member, reason: str):
    """Give a strike to a user (slash command version)"""
    # Check if user has high privilege
    if not can_give_strike(interaction.user):
        await interaction.response.send_message("You don't have permission to give strikes. Only high privilege users can give strikes.", ephemeral=True)
        return
    
    # Check if trying to strike themselves
    if user == interaction.user:
        await interaction.response.send_message("You cannot give yourself a strike.", ephemeral=True)
        return
    
    # Check if trying to strike another high privilege user
    if can_give_strike(user):
        await interaction.response.send_message("You cannot give strikes to other high privilege users.", ephemeral=True)
        return
    
    success, message = await give_strike(user, interaction.user, reason)
    
    if success:
        embed = discord.Embed(
            title="⚠️ Strike Given",
            description=f"Strike given to {user.mention}",
            color=0xFF6B6B,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="User", value=f"{user.mention} ({user.name})", inline=True)
        embed.add_field(name="Strike Count", value=f"{get_user_strike_count(user)}/3", inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_footer(text=f"Given by {interaction.user.name}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message(f"Error: {message}", ephemeral=True)

@bot.command(name='strike')
async def strike_prefix(ctx, user: discord.Member, *, reason: str):
    """Give a strike to a user (prefix command version)"""
    # Check if user has high privilege
    if not can_give_strike(ctx.author):
        await ctx.send("You don't have permission to give strikes. Only high privilege users can give strikes.")
        return
    
    # Check if trying to strike themselves
    if user == ctx.author:
        await ctx.send("You cannot give yourself a strike.")
        return
    
    # Check if trying to strike another high privilege user
    if can_give_strike(user):
        await ctx.send("You cannot give strikes to other high privilege users.")
        return
    
    success, message = await give_strike(user, ctx.author, reason)
    
    if success:
        embed = discord.Embed(
            title="⚠️ Strike Given",
            description=f"Strike given to {user.mention}",
            color=0xFF6B6B,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="User", value=f"{user.mention} ({user.name})", inline=True)
        embed.add_field(name="Strike Count", value=f"{get_user_strike_count(user)}/3", inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_footer(text=f"Given by {ctx.author.name}")
        
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"Error: {message}")

@bot.tree.command(name="strike-info", description="Check strike information for a user")
@app_commands.describe(user="The user to check strikes for")
async def slash_strike_info(interaction: discord.Interaction, user: discord.Member):
    """Check strike information for a user (slash command version)"""
    strike_count = get_user_strike_count(user)
    
    embed = discord.Embed(
        title="⚠️ Strike Information",
        description=f"Strike information for {user.mention}",
        color=0xFF6B6B if strike_count > 0 else 0x6B8E6B,
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(name="User", value=f"{user.mention} ({user.name})", inline=True)
    embed.add_field(name="Strike Count", value=f"{strike_count}/3", inline=True)
    
    if strike_count == 0:
        embed.add_field(name="Status", value="✅ No strikes", inline=True)
    elif strike_count == 1:
        embed.add_field(name="Status", value="⚠️ 1 strike", inline=True)
    elif strike_count == 2:
        embed.add_field(name="Status", value="⚠️ 2 strikes", inline=True)
    else:
        embed.add_field(name="Status", value="🚨 3 strikes (maximum)", inline=True)
    
    embed.set_footer(text=f"Checked by {interaction.user.name}")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.command(name='strike-info')
async def strike_info_prefix(ctx, user: discord.Member):
    """Check strike information for a user (prefix command version)"""
    strike_count = get_user_strike_count(user)
    
    embed = discord.Embed(
        title="⚠️ Strike Information",
        description=f"Strike information for {user.mention}",
        color=0xFF6B6B if strike_count > 0 else 0x6B8E6B,
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(name="User", value=f"{user.mention} ({user.name})", inline=True)
    embed.add_field(name="Strike Count", value=f"{strike_count}/3", inline=True)
    
    if strike_count == 0:
        embed.add_field(name="Status", value="✅ No strikes", inline=True)
    elif strike_count == 1:
        embed.add_field(name="Status", value="⚠️ 1 strike", inline=True)
    elif strike_count == 2:
        embed.add_field(name="Status", value="⚠️ 2 strikes", inline=True)
    else:
        embed.add_field(name="Status", value="🚨 3 strikes (maximum)", inline=True)
    
    embed.set_footer(text=f"Checked by {ctx.author.name}")
    
    await ctx.send(embed=embed)

# Promotion/Demotion system constants
PROMOTION_LOG_CHANNEL_ID = 1362585429227995184

# Strike system role IDs
STRIKE_1_ROLE_ID = 1362585427093229714
STRIKE_2_ROLE_ID = 1362585427093229713
STRIKE_3_ROLE_ID = 1362585427093229712

# Role hierarchy definitions
ROLE_HIERARCHY = {
    "DESIGNERS": {
        "trial": 1362585427135168652,
        "junior": 1362585427135168653,
        "standard": 1362585427168592018,  # Original CLAIM_ROLE_ID
        "senior": 1362585427168592015,
        "lead": 1362585427168592016,
        "head": 1362585427168592017
    },
    "SUPPORT": {
        "trial": 1362585427168592020,
        "junior": 1362585427168592021,
        "normal": 1362585427168592022,
        "senior": 1362585427168592023,
        "head": 1362585427168592024
    },
    "MANAGEMENT": {
        "trial": 1362585427550146614,
        "standard": 1362585427550146615,
        "senior": 1362585427550146616,
        "head": 1362585427550146617,
        "manager": 1362585427550146618  # Add the missing manager role
    }
}

# Special roles
CO_EXECUTIVE_ROLE_ID = 1389024033408024647
MANAGEMENT_REQUIRED_ROLE_ID = 1362585427550146618

def get_user_role_tier(user):
    """Get the current role tier of a user"""
    user_role_ids = [role.id for role in user.roles]
    
    # Check each department
    for department, roles in ROLE_HIERARCHY.items():
        for tier, role_id in roles.items():
            if role_id in user_role_ids:
                return department, tier, role_id
    
    # Check for co-executive
    if CO_EXECUTIVE_ROLE_ID in user_role_ids:
        return "EXECUTIVE", "co_executive", CO_EXECUTIVE_ROLE_ID
    
    return None, None, None

def get_next_role(department, current_tier):
    """Get the next role in the hierarchy"""
    if department not in ROLE_HIERARCHY:
        return None
    
    tiers = list(ROLE_HIERARCHY[department].keys())
    try:
        current_index = tiers.index(current_tier)
        if current_index < len(tiers) - 1:
            next_tier = tiers[current_index + 1]
            return ROLE_HIERARCHY[department][next_tier]
    except ValueError:
        pass
    
    return None

def get_previous_role(department, current_tier):
    """Get the previous role in the hierarchy"""
    if department not in ROLE_HIERARCHY:
        return None
    
    tiers = list(ROLE_HIERARCHY[department].keys())
    try:
        current_index = tiers.index(current_tier)
        if current_index > 0:
            prev_tier = tiers[current_index - 1]
            return ROLE_HIERARCHY[department][prev_tier]
    except ValueError:
        pass
    
    return None

def get_promoter_max_role(promoter):
    """Get the highest role tier the promoter can promote to"""
    promoter_dept, promoter_tier, _ = get_user_role_tier(promoter)
    
    if promoter_dept == "EXECUTIVE":
        return None  # Can promote to any role
    
    if promoter_dept not in ROLE_HIERARCHY:
        return None
    
    # Find the role that's one below the promoter's role
    tiers = list(ROLE_HIERARCHY[promoter_dept].keys())
    try:
        promoter_index = tiers.index(promoter_tier)
        if promoter_index > 0:
            max_tier = tiers[promoter_index - 1]
            return ROLE_HIERARCHY[promoter_dept][max_tier]
    except ValueError:
        pass
    
    return None

def can_promote_user(promoter, target_user):
    """Check if promoter can promote target user"""
    promoter_dept, promoter_tier, _ = get_user_role_tier(promoter)
    target_dept, target_tier, _ = get_user_role_tier(target_user)
    
    # Co-executives can promote anyone
    if promoter_dept == "EXECUTIVE":
        return True
    
    # Can only promote within same department
    if promoter_dept != target_dept:
        return False
    
    # Check if target is already at or above promoter's level
    if promoter_dept in ROLE_HIERARCHY:
        tiers = list(ROLE_HIERARCHY[promoter_dept].keys())
        try:
            promoter_index = tiers.index(promoter_tier)
            target_index = tiers.index(target_tier)
            return target_index < promoter_index
        except ValueError:
            return False
    
    return False

def can_demote_user(demoter, target_user):
    """Check if demoter can demote target user"""
    demoter_dept, demoter_tier, _ = get_user_role_tier(demoter)
    target_dept, target_tier, _ = get_user_role_tier(target_user)
    
    # Co-executives can demote anyone
    if demoter_dept == "EXECUTIVE":
        return True
    
    # Can only demote within same department
    if demoter_dept != target_dept:
        return False
    
    # Check if target is at or above demoter's level
    if demoter_dept in ROLE_HIERARCHY:
        tiers = list(ROLE_HIERARCHY[demoter_dept].keys())
        try:
            demoter_index = tiers.index(demoter_tier)
            target_index = tiers.index(target_tier)
            return target_index >= demoter_index
        except ValueError:
            return False
    
    return False

async def log_promotion_action(action_type, actor, target, reason, old_role, new_role):
    """Log promotion/demotion actions"""
    try:
        logging_channel = actor.guild.get_channel(PROMOTION_LOG_CHANNEL_ID)
        if not logging_channel:
            return
        
        color = 0x6B8E6B if action_type == "promotion" else 0x8E6B6B
        
        embed = discord.Embed(
            title=f"{'📈' if action_type == 'promotion' else '📉'} {action_type.title()} Action",
            description=f"A user has been {action_type}",
            color=color,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Actor", value=f"{actor.mention} ({actor.name})", inline=True)
        embed.add_field(name="Target", value=f"{target.mention} ({target.name})", inline=True)
        embed.add_field(name="Action", value=action_type.title(), inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        
        if old_role:
            embed.add_field(name="Previous Role", value=f"<@&{old_role}>", inline=True)
        if new_role:
            embed.add_field(name="New Role", value=f"<@&{new_role}>", inline=True)
        
        embed.set_footer(text=f"Action ID: {actor.id}-{target.id}-{datetime.utcnow().timestamp()}")
        
        await logging_channel.send(embed=embed)
        
    except Exception as e:
        print(f"Error logging {action_type} action: {e}")

async def log_trial_completion(target, new_role):
    """Log when a user completes their trial period"""
    try:
        logging_channel = target.guild.get_channel(PROMOTION_LOG_CHANNEL_ID)
        if not logging_channel:
            return
        
        embed = discord.Embed(
            title="🎉 Trial Period Completed!",
            description=f"A user has successfully completed their trial period",
            color=0x00FF00,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="User", value=f"{target.mention} ({target.name})", inline=True)
        embed.add_field(name="New Role", value=f"<@&{new_role}>", inline=True)
        embed.add_field(name="Status", value="✅ Trial Completed", inline=True)
        embed.add_field(name="Message", value="Congratulations on completing your trial period! Welcome to the team!", inline=False)
        
        embed.set_footer(text=f"Trial Completion ID: {target.id}-{datetime.utcnow().timestamp()}")
        
        await logging_channel.send(embed=embed)
        
    except Exception as e:
        print(f"Error logging trial completion: {e}")

def get_user_strike_count(user):
    """Get the current strike count for a user"""
    user_role_ids = [role.id for role in user.roles]
    
    if STRIKE_3_ROLE_ID in user_role_ids:
        return 3
    elif STRIKE_2_ROLE_ID in user_role_ids:
        return 2
    elif STRIKE_1_ROLE_ID in user_role_ids:
        return 1
    else:
        return 0

def can_give_strike(striker):
    """Check if user can give strikes (high privileged users only)"""
    striker_role_ids = [role.id for role in striker.roles]
    
    # Check for high rank roles (manager, executive, etc.)
    high_privilege_roles = [
        MANAGEMENT_REQUIRED_ROLE_ID,  # Manager
        CO_EXECUTIVE_ROLE_ID,  # Co-executive
    ]
    
    # Add head roles from each department
    for department, roles in ROLE_HIERARCHY.items():
        if "head" in roles:
            high_privilege_roles.append(roles["head"])
    
    return any(role_id in striker_role_ids for role_id in high_privilege_roles)

async def give_strike(target, striker, reason):
    """Give a strike to a user"""
    current_strikes = get_user_strike_count(target)
    
    if current_strikes >= 3:
        return False, "User already has maximum strikes (3)"
    
    # Remove previous strike roles
    strike_roles = [STRIKE_1_ROLE_ID, STRIKE_2_ROLE_ID, STRIKE_3_ROLE_ID]
    for role_id in strike_roles:
        role = target.guild.get_role(role_id)
        if role and role in target.roles:
            await target.remove_roles(role)
    
    # Add new strike role
    new_strike_count = current_strikes + 1
    if new_strike_count == 1:
        strike_role = target.guild.get_role(STRIKE_1_ROLE_ID)
    elif new_strike_count == 2:
        strike_role = target.guild.get_role(STRIKE_2_ROLE_ID)
    else:  # new_strike_count == 3
        strike_role = target.guild.get_role(STRIKE_3_ROLE_ID)
    
    if strike_role:
        await target.add_roles(strike_role)
    
    # Log the strike action
    await log_strike_action(striker, target, reason, new_strike_count)
    
    return True, f"Strike {new_strike_count}/3 given successfully"

async def log_strike_action(striker, target, reason, strike_count):
    """Log strike actions in the promotion/demotion channel"""
    try:
        logging_channel = striker.guild.get_channel(PROMOTION_LOG_CHANNEL_ID)
        if not logging_channel:
            return
        
        embed = discord.Embed(
            title="⚠️ Strike Given",
            description=f"A user has been given a strike",
            color=0xFF6B6B,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Striker", value=f"{striker.mention} ({striker.name})", inline=True)
        embed.add_field(name="Target", value=f"{target.mention} ({target.name})", inline=True)
        embed.add_field(name="Strike Count", value=f"{strike_count}/3", inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        
        if strike_count == 3:
            embed.add_field(name="⚠️ Warning", value="This user has reached the maximum strike count!", inline=False)
        
        embed.set_footer(text=f"Strike ID: {striker.id}-{target.id}-{datetime.utcnow().timestamp()}")
        
        await logging_channel.send(embed=embed)
        
    except Exception as e:
        print(f"Error logging strike action: {e}")

@bot.tree.command(name="say", description="Make the bot say something in the channel")
@app_commands.describe(message="The message to say (supports **bold** and *italics*)")
async def slash_say(interaction: discord.Interaction, message: str):
    """Make the bot say something in the channel with markdown support"""
    # Check if user has privileged role
    if not has_privileged_role(interaction.user):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return
    
    # Delete the interaction response since we're sending a new message
    await interaction.response.defer(ephemeral=True)
    
    try:
        # Send the message with markdown support
        await interaction.channel.send(message)
        await interaction.followup.send("✅ Message sent successfully!", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Error sending message: {str(e)}", ephemeral=True)

@bot.command(name='hue')
async def help_usage_embed(ctx):
    """Display comprehensive usage guide for all commands"""
    embed = discord.Embed(
        title="📚 **Pixel Management Bot - Complete Command Guide**",
        description="Comprehensive documentation for all available commands and features",
        color=0x7289DA,
        timestamp=datetime.utcnow()
    )
    
    # Order Management Commands
    embed.add_field(
        name="🛒 **Order Management**",
        value=(
            "**Prefix Commands:**\n"
            "• `!oe` - Create order embed (role restricted)\n"
            "• `!update-order-status <service> <status>` - Update service status\n"
            "• `!order-status` - Show current order status\n"
            "• `!os <designer> <customer> <details>` - Start order with details\n"
            "• `!de` - Send design format reminder\n"
            "• `!close` - Close current ticket\n"
            "• `!we` - Workload explanation\n"
            "• `!delay` - Send delay explanation\n"
            "• `!eta-update <new_eta>` - Update completion time\n\n"
            "**Slash Commands:**\n"
            "• `/create-order-embed` - Create order embed\n"
            "• `/update-order-status` - Update service status\n"
            "• `/order-status` - Show order status\n"
            "• `/order-start` - Start order with details\n"
            "• `/design-reminder` - Send design reminder\n"
            "• `/finished` - Mark order as finished\n"
            "• `/delay-explanation` - Send delay explanation\n"
            "• `/eta-update` - Update completion time"
        ),
        inline=False
    )
    
    # Support Management Commands
    embed.add_field(
        name="🆘 **Support Management**",
        value=(
            "**Prefix Commands:**\n"
            "• `!se` - Create support embed\n"
            "• `!resolved` - Mark support ticket as resolved\n\n"
            "**Slash Commands:**\n"
            "• `/create-support-embed` - Create support embed\n"
            "• `/resolved` - Mark support ticket as resolved"
        ),
        inline=False
    )
    
    # Ticket Management Commands
    embed.add_field(
        name="🎫 **Ticket Management**",
        value=(
            "**Prefix Commands:**\n"
            "• `!switch-claim <new_claimer>` - Switch ticket claim\n"
            "• `!switch-order <new_designer>` - Switch order ownership\n\n"
            "**Slash Commands:**\n"
            "• `/switch-claim` - Switch ticket claim\n"
            "• `/switch-order` - Switch order ownership"
        ),
        inline=False
    )
    
    # Payment & Financial Commands
    embed.add_field(
        name="💰 **Payment & Financial**",
        value=(
            "**Prefix Commands:**\n"
            "• `!pl` - Log payment information\n"
            "• `!tax <amount>` - Calculate Roblox tax (70% cut)\n"
            "• `!review <designer> <rating> <remarks>` - Submit review\n\n"
            "**Slash Commands:**\n"
            "• `/payment-log` - Log payment information\n"
            "• `/tax` - Calculate Roblox tax\n"
            "• `/review` - Submit designer review"
        ),
        inline=False
    )
    
    # Role Management Commands
    embed.add_field(
        name="👥 **Role Management**",
        value=(
            "**Prefix Commands:**\n"
            "• `!promote <user> <reason>` - Promote user\n"
            "• `!demote <user> <reason>` - Demote user\n"
            "• `!role-info <user>` - Get user role information\n"
            "• `!role-hierarchy` - Show role hierarchy\n"
            "• `!department-stats` - Show department statistics\n\n"
            "**Slash Commands:**\n"
            "• `/promote` - Promote user\n"
            "• `/demote` - Demote user\n"
            "• `/role-info` - Get user role information\n"
            "• `/role-hierarchy` - Show role hierarchy\n"
            "• `/department-stats` - Show department statistics"
        ),
        inline=False
    )
    
    # Strike System Commands
    embed.add_field(
        name="⚠️ **Strike System**",
        value=(
            "**Prefix Commands:**\n"
            "• `!strike <user> <reason>` - Give strike to user\n"
            "• `!strike-info <user>` - Check user's strike count\n\n"
            "**Slash Commands:**\n"
            "• `/strike` - Give strike to user\n"
            "• `/strike-info` - Check user's strike count\n\n"
            "**Strike Levels:**\n"
            "• Strike 1: Warning role\n"
            "• Strike 2: Second warning role\n"
            "• Strike 3: Final warning role (maximum)"
        ),
        inline=False
    )
    
    # Utility Commands
    embed.add_field(
        name="🔧 **Utility Commands**",
        value=(
            "**Prefix Commands:**\n"
            "• `!sync` - Sync slash commands\n"
            "• `!check-perms` - Check user permissions\n\n"
            "**System Features:**\n"
            "• Automatic ticket creation\n"
            "• Persistent button views\n"
            "• Role-based permissions\n"
            "• Payment logging system\n"
            "• Review system\n"
            "• Support escalation"
        ),
        inline=False
    )
    
    # Command Usage Examples
    embed.add_field(
        name="📝 **Usage Examples**",
        value=(
            "**Order Management:**\n"
            "• `!os @designer @customer Logo Design - 500 RBX - 3 days`\n"
            "• `!update-order-status logos delayed`\n"
            "• `!eta-update 2 more days`\n\n"
            "**Role Management:**\n"
            "• `!promote @user Excellent performance`\n"
            "• `!demote @user Inactive for 2 weeks`\n\n"
            "**Payment:**\n"
            "• `!tax 1000` (calculates ~1429 RBX needed)\n"
            "• `!review @designer 5 Amazing work!`"
        ),
        inline=False
    )
    
    # Role Requirements
    embed.add_field(
        name="🔐 **Role Requirements**",
        value=(
            "**Design Commands:** Designer, Manager, or Executive roles\n"
            "**Support Commands:** Support, High Rank, or Executive roles\n"
            "**Management Commands:** Manager or Executive roles\n"
            "**Strike Commands:** High privilege users only (Manager, Head, Executive)\n"
            "**Payment Commands:** Designer roles (payment log), All users (tax/review)\n"
            "**Utility Commands:** Varies by command"
        ),
        inline=False
    )
    
    embed.set_footer(text="Use !hue to display this guide • All commands support both prefix (!) and slash (/) formats")
    
    await ctx.send(embed=embed)

# Run the bot
if __name__ == "__main__":
    # Load token from environment variable or config file
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                TOKEN = config.get('token')
        except FileNotFoundError:
            print("Please set DISCORD_TOKEN environment variable or create config.json with your bot token")
            exit(1)
    
    if not TOKEN or TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("Please set DISCORD_TOKEN environment variable or update config.json with your bot token")
        exit(1)
    
    bot.run(TOKEN) 