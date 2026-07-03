# 🚀 Premium Video Bot

A production-ready enterprise Telegram bot for premium video delivery with referral and points system.

## Features

✅ **Unlimited Video System**
- Upload unlimited videos via Telegram file_id
- Duplicate detection
- No local video storage
- Watch history tracking

✅ **Free & Premium Content**
- 2 free videos for new users
- Point-based unlock system
- 1 Point = 5 Videos

✅ **Referral System**
- Generate unique referral links
- 1 Referral = 1 Point
- Top referrer tracking
- CSV export

✅ **User Dashboard**
- Profile with statistics
- Points and rewards tracking
- Watch history
- Referral management

✅ **Admin Panel**
- Video management
- User management
- Points control
- Broadcasting
- CSV exports
- Database backup
- Custom buttons
- Force join channels

✅ **Reliability**
- Atomic JSON database
- Automatic corruption recovery
- Database backups
- Crash-safe polling loop
- Production logging

## Installation

### Prerequisites
- Python 3.8+
- Telegram Bot Token (from @BotFather)

### Setup

1. Clone the repository:
```bash
git clone <repo-url>
cd premium-video-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. Configure your bot:
```env
BOT_TOKEN=your_bot_token_here
BOT_USERNAME=your_bot_username
OWNER_ID=your_user_id
ADMIN_IDS=admin_id_1,admin_id_2
LOG_CHANNEL=-1001234567890
```

5. Run the bot:
```bash
python bot.py
```

## Usage

### For Users

1. Start the bot: `/start`
2. Watch videos: Click "🎬 Premium Video"
3. View profile: Click "👤 My Profile"
4. Share referral: Click "👥 My Referral" and share the link
5. Check points: Click "💎 My Points"

### For Admins

Access admin panel: `/admin`

**Admin Features:**
- Upload Premium Video
- Video Statistics
- Delete Video
- Add/Remove Points
- Ban/Unban Users
- Broadcast Messages
- View Top Referrers
- Export CSV Reports
- Manage Custom Buttons
- Configure Force Join
- Backup Database

## Project Structure

```
premium-video-bot/
├── bot.py                 # Entry point
├── config.py             # Configuration
├── requirements.txt      # Dependencies
├── database.json         # JSON database
├── .env.example          # Environment template
├── README.md            # Documentation
├── .gitignore           # Git ignore rules
│
├── core/                 # Core bot logic
│   └── bot.py
│
├── models/               # Data models
│   ├── user.py
│   ├── video.py
│   └── admin_button.py
│
├── services/             # Business logic
│   ├── user_service.py
│   ├── video_service.py
│   └── broadcast_service.py
│
├── handlers/             # Message handlers
│   ├── user_handlers.py
│   ├── admin_handlers.py
│   └── callback_handlers.py
│
├── keyboards/            # Keyboard layouts
│   ├── user_keyboards.py
│   └── admin_keyboards.py
│
├── utils/                # Utility functions
│   ├── database.py       # Database operations
│   └── logger.py         # Logging setup
│
├── data/                 # Data storage
│   └── backups/
│
├── logs/                 # Log files
│   ├── bot.log
│   ├── error.log
│   └── broadcast.log
│
and temp/                # Temporary files
```

## Database Schema

### Users
```json
{
  "id": 123456,
  "username": "user_handle",
  "name": "User Name",
  "points": 5,
  "free_videos_left": 0,
  "videos_remaining": 10,
  "videos_watched": [0, 1, 2],
  "repeat_index": 0,
  "referrals": 5,
  "is_banned": false,
  "join_date": "2024-01-01T00:00:00",
  "last_active": "2024-01-02T12:00:00"
}
```

### Videos
```json
{
  "file_id": "AgADBAAD...",
  "file_unique_id": "...",
  "caption": "Video Title",
  "uploaded_at": "2024-01-01T00:00:00",
  "uploaded_by": 123456
}
```

## Video Delivery Logic

1. **New Users**: Get 2 FREE videos
2. **After Free**: Users earn points through referrals (1 referral = 1 point)
3. **Point Usage**: 1 point = 5 videos
4. **Video Selection**:
   - Show unseen videos first
   - Once all videos watched, repeat from beginning
   - No duplicates until all videos watched

## Broadcasting

Admins can broadcast messages to:
- All users
- Active users only
- Selected users

Features:
- Pause/Resume broadcasts
- Failure logging
- Statistics tracking

## Force Join

Admins can require users to join channels before watching videos:
- Add unlimited channels
- Auto-verify membership
- Support public & private channels

## Logging

Three log files are maintained:

- **bot.log**: General bot operations
- **error.log**: Error tracking
- **broadcast.log**: Broadcast statistics

## Performance

- ✅ Low memory usage
- ✅ Low CPU usage
- ✅ Memory leak free
- ✅ Optimized for Render free plan
- ✅ Async polling with timeouts

## Security

- Admin-only operations protected
- Ban system for spam/abuse
- Database backups for recovery
- Atomic file operations
- Corruption recovery

## Deployment

### Render

1. Push code to GitHub
2. Connect GitHub repo to Render
3. Create Web Service
4. Set environment variables in Render dashboard
5. Deploy!

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

## Troubleshooting

### Bot doesn't respond
- Check BOT_TOKEN in .env
- Verify bot is not already running
- Check logs/error.log

### Database corruption
- Bot automatically recovers from backups
- Check data/backups/ directory
- Manual restore: Replace database.json with backup

### Videos not sending
- Verify video file_id is valid
- Check Telegram API limits
- Review error.log

## Support

For issues and feature requests, please create a GitHub issue.

## License

MIT License - See LICENSE file for details

---

**Made with ❤️ for production-ready Telegram bots**
