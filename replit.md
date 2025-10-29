# Telegram Report Bot

## Overview
This is a Telegram bot with a referral system and admin broadcast functionality. The bot allows users to report Telegram usernames/channels after referring 3 friends. Admin users have special privileges including the ability to broadcast messages to all users.

## Recent Changes (October 27, 2025)
- Removed referral requirements for admin user (LapsusVishal)
- Added broadcast functionality for admin
- Admin can send text, photos, or videos to all users
- Broadcast button is only visible to admin (LapsusVishal)
- Protected usernames from reports: LapsusVishal, MassReportTelegram_bot
- Updated developer attribution to @LapsusVishal
- Added referral bypass for user @Ghost_oppp (can use bot without 3 referrals)

## Features
- **Referral System**: Users must refer 3 friends to unlock bot access
- **Admin Bypass**: Admin (LapsusVishal) can use all features without referral requirements
- **VIP Users**: Special users (Ghost_oppp) can bypass referral requirements
- **Broadcast System**: Admin can send messages (text/photo/video) to all users
- **Protected Usernames**: LapsusVishal and MassReportTelegram_bot are protected from reports
- **Report Tracking**: All report attempts are logged and tracked
- **Proxy Support**: Uses SOCKS4 proxies for report submissions

## Project Structure
- `main.py`: Main bot logic with conversation handlers
- `database.py`: SQLite database operations for user management
- `report.txt`: Report message templates
- `NG.txt`: SOCKS4 proxy list
- `bot_users.db`: SQLite database file (auto-created)

## Admin Features
- Username: `LapsusVishal`
- No referral requirements
- Access to broadcast button
- Can send text, photos, or videos to all users
- Broadcasts show delivery statistics

## User Flow
1. New users join via /start command
2. Users receive a referral link
3. After 3 referrals, users can access the bot
4. Admin can access immediately without referrals
5. Admin can broadcast messages via the broadcast button

## Environment Variables
- `TELEGRAM_BOT_TOKEN`: Telegram bot token from BotFather

## Dependencies
- python-telegram-bot
- faker
- requests
- pysocks
- sqlite3 (built-in)
