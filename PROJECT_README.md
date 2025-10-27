# Traffic Share - Complete Implementation

This is a complete implementation of the Traffic Share platform as described in the original README.md file. The project allows users to share their internet traffic through a mobile app, and buyers can purchase this traffic via API.

## 🏗️ Project Structure

```
traffic_share/
├── __init__.py
├── server/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py              # Configuration management
│   ├── database.py            # Database connection and session management
│   ├── models.py              # SQLAlchemy database models
│   ├── schemas.py             # Pydantic request/response schemas
│   ├── dependencies.py        # FastAPI dependencies
│   ├── utils.py               # Utility functions
│   ├── logger.py              # Logging configuration
│   ├── limiter.py             # Rate limiting
│   ├── services/              # Business logic services
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── traffic_service.py
│   │   ├── buyer_service.py
│   │   ├── payment_service.py
│   │   ├── notification_service.py
│   │   └── admin_service.py
│   ├── routes/                # API route handlers
│   │   ├── auth_routes.py
│   │   ├── user_routes.py
│   │   ├── traffic_routes.py
│   │   ├── buyer_routes.py
│   │   ├── payment_routes.py
│   │   ├── admin_routes.py
│   │   └── system_routes.py
│   └── tasks/                 # Background tasks
│       ├── cleanup_task.py
│       ├── notify_task.py
│       ├── stats_task.py
│       └── backup_task.py
├── core/                      # Core utilities
│   ├── security.py           # Authentication and security
│   ├── exceptions.py         # Custom exceptions
│   ├── constants.py          # Application constants
│   └── region_check.py       # IP region validation
├── migrations/               # Database migrations
│   ├── env.py
│   └── versions/
├── tests/                    # Test files
│   ├── test_auth.py
│   ├── test_traffic.py
│   ├── test_buyer.py
│   └── test_payment.py
├── bot/                      # Telegram bot
│   ├── bot.py
│   ├── handlers/
│   │   ├── user_handlers.py
│   │   ├── admin_handlers.py
│   │   ├── callback_handlers.py
│   │   └── notification_handlers.py
│   └── utils/
│       ├── requests_helper.py
│       ├── message_templates.py
│       └── state_manager.py
└── app/                      # Flutter mobile app
    ├── lib/
    │   ├── main.dart
    │   ├── api/
    │   │   ├── api_client.dart
    │   │   ├── auth_api.dart
    │   │   ├── traffic_api.dart
    │   │   ├── user_api.dart
    │   │   ├── buyer_api.dart
    │   │   └── payment_api.dart
    │   ├── models/
    │   │   ├── user_model.dart
    │   │   ├── traffic_model.dart
    │   │   ├── package_model.dart
    │   │   └── payment_model.dart
    │   ├── screens/
    │   │   ├── login_screen.dart
    │   │   ├── home_screen.dart
    │   │   ├── traffic_screen.dart
    │   │   ├── wallet_screen.dart
    │   │   └── settings_screen.dart
    │   └── widgets/
    │       ├── traffic_card.dart
    │       ├── balance_card.dart
    │       └── loading_indicator.dart
    ├── scripts/
    │   ├── init_db.py
    │   ├── seed_data.py
    │   ├── rotate_tokens.py
    │   ├── clear_sessions.py
    │   └── export_stats.py
    └── pubspec.yaml
├── .env                      # Environment variables
├── requirements.txt          # Python dependencies
├── alembic.ini              # Database migration config
├── run_server.sh            # Server startup script
├── docker-compose.yml       # Docker composition
└── Dockerfile               # Docker configuration
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Flutter SDK (for mobile app)
- Docker (optional)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd traffic_share
```

### 2. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env` file and update the values:

```bash
cp .env.example .env
# Edit .env with your actual values
```

Key environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `CRYPTOMUS_MERCHANT_ID`: Cryptomus merchant ID
- `CRYPTOMUS_API_KEY`: Cryptomus API key

### 4. Setup Database

```bash
# Using Docker (recommended)
docker-compose up -d postgres redis

# Or setup PostgreSQL manually
createdb traffic_share
```

### 5. Run Database Migrations

```bash
# Initialize Alembic (first time only)
alembic init traffic_share/migrations

# Run migrations
alembic upgrade head
```

### 6. Start the Server

```bash
# Using the startup script
./run_server.sh

# Or manually
python -m traffic_share.server.main
```

The API will be available at `http://localhost:8000`

### 7. Start the Telegram Bot

```bash
python -m traffic_share.bot.bot
```

### 8. Build Flutter App

```bash
cd traffic_share/app
flutter pub get
flutter build apk  # For Android
flutter build ios  # For iOS
```

## 📚 API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key API Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/request_login_code` - Request login code
- `POST /api/auth/verify_code` - Verify login code

#### User Management
- `GET /api/user/me` - Get user profile
- `POST /api/user/update` - Update user profile
- `POST /api/user/device/register` - Register device

#### Traffic Sharing
- `POST /api/traffic/start` - Start traffic session
- `POST /api/traffic/update` - Update traffic data
- `POST /api/traffic/stop` - Stop traffic session
- `GET /api/traffic/history` - Get traffic history

#### Buyer API
- `POST /api/buyer/packets/pull` - Pull available packages
- `POST /api/buyer/packets/{uuid}/status` - Update package status
- `GET /api/buyer/me/allocations` - Get allocated packages

#### Admin
- `POST /api/admin/buyers` - Create buyer
- `GET /api/admin/users` - Get all users
- `POST /api/admin/packages/bulk_create` - Create packages

## 🔧 Configuration

### Database Configuration

The application supports both SQLite (development) and PostgreSQL (production):

```python
# SQLite (default for development)
DATABASE_URL=sqlite:///./traffic_share.db

# PostgreSQL (production)
DATABASE_URL=postgresql://user:password@localhost:5432/traffic_share
```

### Payment Integration

The system uses Cryptomus for payments. Configure your credentials in `.env`:

```env
CRYPTOMUS_MERCHANT_ID=your_merchant_id
CRYPTOMUS_API_KEY=your_api_key
CRYPTOMUS_WEBHOOK_SECRET=your_webhook_secret
```

### Telegram Bot

Configure your bot token and admin IDs:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_ADMIN_IDS=123456789,987654321
```

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Docker Build

```bash
# Build image
docker build -t traffic-share .

# Run container
docker run -p 8000:8000 --env-file .env traffic-share
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=traffic_share

# Run specific test file
pytest tests/test_auth.py
```

## 📱 Mobile App Development

### Flutter Setup

```bash
cd traffic_share/app

# Install dependencies
flutter pub get

# Run in debug mode
flutter run

# Build for production
flutter build apk --release
```

### App Features

- User authentication via Telegram
- Real-time traffic sharing
- Balance tracking
- Withdrawal requests
- Session history
- Settings management

## 🔒 Security Features

- JWT-based authentication
- Rate limiting on all endpoints
- IP region validation
- Token hashing for secure storage
- Input validation with Pydantic
- CORS protection
- SQL injection prevention

## 📊 Monitoring

- Health check endpoint: `/health`
- System metrics: `/api/system/metrics`
- Request logging
- Error tracking
- Performance monitoring

## 🚀 Production Deployment

### Environment Setup

1. Set up PostgreSQL database
2. Configure Redis for caching
3. Set up reverse proxy (Nginx)
4. Configure SSL certificates
5. Set up monitoring and logging

### Security Checklist

- [ ] Change default secrets
- [ ] Configure proper CORS origins
- [ ] Set up rate limiting
- [ ] Enable HTTPS
- [ ] Configure firewall rules
- [ ] Set up backup procedures

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation

## 🔄 Updates

The system is designed to be easily extensible. Key areas for future development:

- Real-time WebSocket connections
- Advanced analytics dashboard
- Mobile app push notifications
- Multi-currency support
- Advanced fraud detection
- Machine learning for traffic optimization

---

**Note**: This is a complete implementation of the Traffic Share platform. Make sure to configure all environment variables and test thoroughly before deploying to production.
