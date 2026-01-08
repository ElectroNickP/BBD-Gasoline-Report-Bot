# BBD Gasoline Report Bot 🚤⛽

Telegram bot for tracking fuel consumption reports for boat fleet management.

## Features

- 📝 **Easy Report Filling** - Button-based interface for quick data entry
- 👨‍✈️ **Captain & Boat Tracking** - Track fuel usage by captain and boat
- 🏝 **Program Management** - Support for different tour programs including private tours
- 📊 **Analytics** - View statistics by boats, captains, programs with efficiency rankings
- 📥 **CSV Export** - Export data for Google Sheets integration
- 📷 **Photo Attachments** - Optional odometer and receipt photos
- 🔐 **Access Control** - Whitelist-based user authorization

## Tech Stack

- Python 3.11+
- python-telegram-bot 22.5
- SQLAlchemy 2.0 (async) + SQLite
- PyYAML for configuration

## Project Structure

```
├── bot/
│   ├── handlers/       # Telegram handlers
│   ├── middlewares/    # Auth middleware
│   ├── keyboards.py    # Inline keyboards
│   └── states.py       # FSM states
├── config/
│   ├── settings.py     # App settings
│   ├── dictionaries.yaml   # Captains, boats, programs, piers
│   └── allowed_users.yaml  # User whitelist
├── database/
│   ├── models.py       # SQLAlchemy models
│   ├── database.py     # DB connection
│   └── repository.py   # Data access layer
├── services/
│   ├── report_service.py
│   ├── analytics_service.py
│   ├── dictionary_service.py
│   └── user_service.py
├── data/               # SQLite database (gitignored)
├── main.py             # Entry point
└── requirements.txt
```

## Setup

1. Clone the repository
2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create `.env` file:
   ```
   BOT_TOKEN=your_telegram_bot_token
   ```
5. Configure `config/allowed_users.yaml` with Telegram user IDs
6. Run:
   ```bash
   python main.py
   ```

## Configuration

### Dictionaries (`config/dictionaries.yaml`)
Edit to add/remove captains, boats, programs, and piers.

### User Access (`config/allowed_users.yaml`)
Add Telegram user IDs to whitelist. Set `0` to allow all users.

## Bot Commands

- `/start` - Start the bot
- `/help` - Show help
- `/cancel` - Cancel current operation

## Menu Options

- 📝 **New Report** - Fill a new fuel report
- 📊 **Analytics** - View statistics and export data
- 📋 **History** - View recent reports
- ℹ️ **Help** - Show help information

## License

MIT
