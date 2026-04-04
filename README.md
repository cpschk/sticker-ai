# Sticker AI Monorepo

A fullstack application for AI-powered sticker generation with emotion detection.

## 🏗️ Architecture

This monorepo contains:
- **Backend**: Python FastAPI service for emotion detection and sticker suggestions
- **Mobile**: React Native Expo app for the user interface

## 📁 Project Structure

```
sticker-ai-monorepo/
├── backend/                    # Python FastAPI backend
│   ├── app/                    # Application code
│   │   ├── models/            # Pydantic models
│   │   ├── routes/            # API endpoints
│   │   ├── services/          # Business logic
│   │   └── utils/             # Utilities
│   ├── tests/                 # Backend tests
│   ├── requirements.txt       # Python dependencies
│   ├── main.py               # FastAPI entry point
│   └── Dockerfile            # Backend container
├── mobile/                    # React Native Expo app
│   ├── src/                  # Source code
│   │   ├── components/       # Reusable components
│   │   ├── screens/          # App screens
│   │   ├── services/         # API services
│   │   └── utils/            # Utilities
│   ├── assets/               # Images, fonts, etc.
│   ├── app.json              # Expo configuration
│   ├── package.json          # Node dependencies
│   ├── App.js                # Main app component
│   └── Dockerfile            # Mobile container (optional)
├── docs/                     # Documentation
│   ├── API.md                # API documentation
│   ├── SETUP.md              # Detailed setup guide
│   └── ARCHITECTURE.md       # System architecture
├── scripts/                  # Helper scripts
│   ├── setup.sh              # Initial setup script
│   ├── dev.sh                # Start development environment
│   └── deploy.sh             # Deployment script
├── docker/                   # Docker configurations
│   ├── backend.Dockerfile    # Backend container
│   └── mobile.Dockerfile     # Mobile container
├── .gitignore               # Git ignore rules
├── README.md                # This file
├── package.json             # Root scripts and commands
├── docker-compose.yml       # Multi-service orchestration
└── requirements-dev.txt     # Development dependencies
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm/yarn
- **Expo CLI** (`npm install -g @expo/cli`)
- **Git**

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd sticker-ai-monorepo

# Run setup script (Linux/Mac)
./scripts/setup.sh

# Or manual setup:
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Mobile setup
cd ../mobile
npm install
```

### 2. Environment Variables

Create `.env` files in both backend and mobile directories:

**backend/.env:**
```env
ENVIRONMENT=development
DEBUG=True
PORT=8000
```

**mobile/.env:**
```env
EXPO_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run Development Environment

```bash
# From project root
npm run dev

# This will start both backend and mobile in development mode
```

Or run separately:

```bash
# Terminal 1: Backend
npm run dev:backend

# Terminal 2: Mobile
npm run dev:mobile
```

## 🛠️ Development

### Backend (Python/FastAPI)

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Run development server
uvicorn main:app --reload --port 8000

# Run tests
pytest

# API Documentation: http://localhost:8000/docs
```

### Mobile (React Native/Expo)

```bash
cd mobile

# Start Expo development server
npx expo start

# Or with specific platform
npx expo start --ios
npx expo start --android
npx expo start --web
```

## 🐳 Docker Development

### Using Docker Compose

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Individual Services

```bash
# Backend only
docker build -f docker/backend.Dockerfile -t sticker-ai-backend .
docker run -p 8000:8000 sticker-ai-backend

# Mobile (for web development)
docker build -f docker/mobile.Dockerfile -t sticker-ai-mobile .
docker run -p 19006:19006 sticker-ai-mobile
```

## 📱 Mobile App Features

- **Text Input**: Enter text for emotion analysis
- **Generate Sticker Button**: Calls backend API
- **Image Display**: Shows generated avatar with speech bubble
- **Error Handling**: Graceful error messages

### API Integration

The mobile app calls the `/api/v1/suggest-sticker` endpoint:

```javascript
const response = await fetch('http://localhost:8000/api/v1/suggest-sticker', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: userInput })
});

const data = await response.json();
// data.generated_image_base64 contains the PNG image
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Mobile Tests

```bash
cd mobile
npm test
```

### Integration Tests

```bash
# Run both backend and mobile tests
npm run test:all
```

## 🚀 Deployment

### Backend Deployment

```bash
# Build and deploy backend
cd backend
docker build -t sticker-ai-backend .
docker run -d -p 8000:8000 sticker-ai-backend
```

### Mobile Deployment

```bash
# Build for production
cd mobile
npx expo build:android
npx expo build:ios
```

### Production Docker Compose

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d
```

## 📋 Available Scripts

From project root (`package.json`):

```bash
# Development
npm run dev              # Start both services
npm run dev:backend      # Start backend only
npm run dev:mobile       # Start mobile only

# Testing
npm run test:backend     # Run backend tests
npm run test:mobile      # Run mobile tests
npm run test:all         # Run all tests

# Docker
npm run docker:build     # Build all containers
npm run docker:up        # Start all services
npm run docker:down      # Stop all services

# Setup
npm run setup            # Initial project setup
npm run clean            # Clean all artifacts
```

## 🔧 Configuration

### Backend Configuration

- **Port**: 8000 (configurable via environment)
- **Environment**: development/production
- **Database**: SQLite for development, PostgreSQL for production

### Mobile Configuration

- **API URL**: Configurable via environment variables
- **Platform Support**: iOS, Android, Web
- **Build**: Expo managed workflow

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- **Backend**: Follow PEP 8, use Black for formatting
- **Mobile**: Follow Airbnb React Native style guide
- **Commits**: Use conventional commits

## 📚 Documentation

- [API Documentation](./docs/API.md)
- [Setup Guide](./docs/SETUP.md)
- [Architecture](./docs/ARCHITECTURE.md)
- [Backend README](./backend/README.md)
- [Mobile README](./mobile/README.md)

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
```bash
# Check Python version
python --version

# Check virtual environment
source backend/venv/bin/activate
pip list
```

**Mobile build fails:**
```bash
# Clear Expo cache
npx expo r -c

# Clear npm cache
npm cache clean --force
```

**Docker issues:**
```bash
# Check Docker status
docker ps

# View container logs
docker logs <container-id>
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- FastAPI for the amazing Python web framework
- Expo for simplifying React Native development
- Open source community for inspiration and tools
