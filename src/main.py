import discord
from discord.ext import commands
import asyncio
import json
import os
import random
from datetime import datetime
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
            existing_ticket = discord.utils.get(guild.channels, name=f"unclaimed-{user.name.lower()}")
            if existing_ticket:
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
        # Send closing message
        embed = discord.Embed(
            title="🔒 Ticket Closing",
            description="This ticket will be closed in 10 seconds...",
            color=0x8E6B6B,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=".pixel Design Services")
        await channel.send(embed=embed)
        # Log closure
        await self.log_ticket_close(channel, interaction.user)
        await interaction.response.send_message("Ticket will be closed in 10 seconds.", ephemeral=True)
        # Close after delay
        await asyncio.sleep(10)
        await channel.delete()
    
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
    embed = discord.Embed(
        title="Ticket Closing",
        description="This ticket will be closed in 10 seconds...",
        color=0x8E6B6B,
        timestamp=datetime.utcnow()
    )
    await ctx.send(embed=embed)
    await asyncio.sleep(10)
    await ctx.channel.delete()

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