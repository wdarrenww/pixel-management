# Design Server Discord Bot

A comprehensive Discord bot for managing design service orders and tickets in your Discord server.

## Features

### 🎨 Order Management System
- **Professional Embed**: Beautiful, modern embed with compelling copywriting
- **Interactive Buttons**: "Order Now" and "Order Info & Pricing" buttons
- **Ticket Creation**: Automatic ticket channel creation for each order
- **Role-Based Access**: Only users with specific role can create order embeds
- **Dynamic Order Status**: Real-time status updates for all services with custom emojis

### 📋 Ticket System
- **Automatic Channel Creation**: Creates private channels for each order
- **Permission Management**: Proper access control for ticket channels
- **Welcome Messages**: Professional onboarding for new tickets
- **Ticket Closing**: Easy ticket management with close command

### 💰 Pricing Information
- **Comprehensive Pricing**: Detailed pricing for all design services
- **Service Breakdown**: Logo design, brand identity, website design, etc.
- **Rush Order Options**: Additional fees for expedited service
- **What's Included**: Clear list of deliverables and features

## Setup Instructions

### 1. Prerequisites
- Python 3.8 or higher
- Discord Bot Token
- Discord Server with appropriate permissions

### 2. Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot**:
   - Option A: Edit `config.json` and add your bot token
   - Option B: Set environment variable `DISCORD_TOKEN`

4. **Set up your Discord bot**:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Go to "Bot" section and copy the token
   - Enable required intents (Message Content Intent, Server Members Intent)

5. **Invite the bot to your server**:
   - Go to OAuth2 > URL Generator
   - Select scopes: `bot`, `applications.commands`
   - Select permissions: `Administrator` (or customize as needed)
   - Use the generated URL to invite the bot

### 3. Configuration

#### Required Settings
- **Bot Token**: Your Discord bot token
- **Order Role ID**: Role ID that can create order embeds (1362585427621707999)
- **Ticket Channel ID**: Channel where order embeds can be created (1390384385177554965)

#### Optional Customization
- Edit the embed content in `src/main.py`
- Modify pricing information in the `order_info` method
- Customize ticket channel permissions and naming

### 4. Running the Bot

```bash
python src/main.py
```

## Usage

### Creating Order Embeds
1. Ensure you have the required role (ID: 1362585427621707999)
2. Go to the designated channel (ID: 1390384385177554965)
3. Type `-oe` or use `/create-order-embed` to create the order embed

### Ordering Process
1. Users click "Order Now" button
2. Bot shows service selection menu (ephemeral)
3. Users select their desired service type
4. Bot creates `unclaimed-<username>` channel in appropriate category
5. Welcome embed with custom banner and order form is sent
6. Users provide project details in the ticket
7. Design team responds and manages the order

### Service Categories
- **Clothing Design**: Category ID 1362585429227995179
- **Livery and ELS**: Category ID 1362585429227995178  
- **Graphics & Logos**: Category ID 1362585429227995180
- **Discord Layouts**: Category ID 1362585429227995181
- **ELS Only**: Category ID 1380555774429888644

### Order Status Management
- **Real-time Updates**: Use `-update-order-status <service> <open/delayed>` or `/update-order-status` to update service status
- **Visual Indicators**: Custom emojis show open/delayed status for each service
- **Automatic Updates**: Embed automatically updates when status changes
- **Status Overview**: Use `-order-status` or `/order-status` to view current status of all services
- **Slash Commands**: Modern Discord slash commands with dropdown selections

### Ticket Management System
- **Claim Tickets**: Users with claim role (ID: 1362585427168592018) can claim tickets
- **Channel Renaming**: Claimed tickets are renamed to `claimed-<username>`
- **Close Tickets**: Users with close role (ID: 1362585427550146618) or order role can close tickets
- **Double Confirmation**: Ticket closure requires confirmation to prevent accidents
- **Comprehensive Logging**: All ticket actions logged to designated channel (ID: 1362585429706019031)
- **Manager Permissions**: Users with manager role (ID: 1362585427550146618) can manage order embeds

### Pricing Information
- Users can click "Order Info & Pricing" for detailed service information
- Includes pricing, turnaround times, and what's included

### Ticket Management
- Use `-close` command in ticket channels to close them
- Only ticket owners and administrators can close tickets

## Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `-oe` | Create order embed (role restricted) | `-oe` |
| `-update-order-status` | Update service status (role restricted) | `-update-order-status <service> <open/delayed>` |
| `-order-status` | Show current order status (role restricted) | `-order-status` |
| `-close` | Close current ticket channel | `-close` |

### Slash Commands
| Command | Description | Usage |
|---------|-------------|-------|
| `/create-order-embed` | Create the order embed (role restricted) | `/create-order-embed` |
| `/update-order-status` | Update service status with dropdown (role restricted) | `/update-order-status` |
| `/order-status` | Show current order status (role restricted) | `/order-status` |

## File Structure

```
pixelmanagement/
├── src/
│   └── main.py              # Main bot file
├── requirements.txt         # Python dependencies
├── config.json             # Bot configuration
├── env_example.txt         # Environment variables template
└── README.md              # This file
```

## Security Features

- **Role-Based Access**: Only authorized users can create order embeds
- **Channel Restrictions**: Commands only work in designated channels
- **Permission Checks**: Proper validation for all actions
- **Ephemeral Responses**: Sensitive information sent privately

## Customization

### Embed Styling
The bot uses a professional dark theme with:
- Color: `#2F3136` (Discord dark theme)
- Minimal emoji usage
- Clean, modern typography
- Professional copywriting

### Adding New Services
Edit the `order_info` method in `src/main.py` to add new service categories and pricing.

### Modifying Permissions
Update the role and channel IDs in the configuration to match your server setup.

## Support

For issues or questions:
1. Check the Discord.py documentation
2. Verify your bot permissions and intents
3. Ensure all configuration values are correct

## License

This project is open source and available under the MIT License. 