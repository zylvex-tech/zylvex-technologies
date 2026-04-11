# MIND MAPPER - BCI-Powered Thought Visualization Platform

## 🧠 Overview

MIND MAPPER is a cross-platform application that translates neural patterns into interactive visual mind maps in real-time. The MVP simulates BCI input with a focus slider, with real hardware integration planned for future releases.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          MIND MAPPER ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    │
│  │   Mobile App    │    │   Desktop App   │    │   Web Portal    │    │
│  │  (React Native) │    │   (Electron)    │    │   (React)       │    │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘    │
│           │                      │                      │              │
│           │  ┌──────────────────────────────────────┐   │              │
│           │  │        Shared Authentication         │   │              │
│           │  │         (JWT Service Port 8001)      │   │              │
│           │  └──────────────────────────────────────┘   │              │
│           │                      │                      │              │
│  ┌────────▼────────┐    ┌────────▼────────┐    ┌───────▼────────┐    │
│  │  Neural Data    │    │ Visualization   │    │   API Gateway   │    │
│  │   Processing    │    │    Engine       │    │   (FastAPI)     │    │
│  │   (On-Device)   │    │   (D3.js)       │    │   Port 8002     │    │
│  └────────┬────────┘    └─────────────────┘    └───────┬────────┘    │
│           │                                            │              │
│           └────────────────────────────────────────────┘              │
│                                    │                                  │
│                         ┌──────────▼──────────┐                       │
│                         │   Backend Services   │                       │
│                         │   (Microservices)    │                       │
│                         └──────────┬──────────┘                       │
│                                    │                                  │
│                    ┌───────────────▼────────────────┐                 │
│                    │          PostgreSQL            │                 │
│                    │  ┌──────────────────────────┐  │                 │
│                    │  │        mindmaps          │  │                 │
│                    │  │        nodes             │  │                 │
│                    │  │        sessions          │  │                 │
│                    │  └──────────────────────────┘  │                 │
│                    └────────────────────────────────┘                 │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    External Integrations                         │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐ │  │
│  │  │   BCI      │  │   Cloud    │  │   Export   │  │   AI/ML    │ │  │
│  │  │  Devices   │  │   Sync     │  │   Tools    │  │  Services  │ │  │
│  │  │ (Future)   │  │            │  │            │  │            │ │  │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘ │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

## 📱 Mobile App (React Native + Expo)

### Screens
1. **Auth Flow** - Login/Register using shared auth service
2. **Home Screen** - List mind maps with CRUD operations
3. **Mind Map Editor** - Interactive canvas with focus simulator
4. **Session Stats** - Analytics and focus visualization

### Focus Simulator
- Slider from 0-100 representing focus level
- Color-coded nodes based on focus:
  - >70: Green nodes with larger font (High Focus 🟢)
  - 40-70: Yellow nodes with normal font (Moderate 🟡)
  - <40: Red nodes with smaller font (Low Focus 🔴)

## 🖥️ Backend Services (Python FastAPI)

### Database Schema
```sql
-- mindmaps table
CREATE TABLE mindmaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- nodes table
CREATE TABLE nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mindmap_id UUID REFERENCES mindmaps(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES nodes(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    color VARCHAR(7) NOT NULL,
    font_size INTEGER NOT NULL,
    focus_level INTEGER NOT NULL,
    x FLOAT DEFAULT 0,
    y FLOAT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mindmap_id UUID REFERENCES mindmaps(id) ON DELETE CASCADE,
    avg_focus FLOAT NOT NULL,
    duration_seconds INTEGER NOT NULL,
    node_count INTEGER NOT NULL,
    focus_timeline JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### API Endpoints
```
POST   /mindmaps              - Create new mind map
GET    /mindmaps              - List user's mind maps
DELETE /mindmaps/{id}         - Delete mind map
POST   /mindmaps/{id}/nodes   - Add node to mind map
DELETE /mindmaps/{id}/nodes/{node_id} - Remove node
POST   /mindmaps/{id}/sessions - Save session stats
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ and npm
- Python 3.11+

### 1. Clone and Setup
```bash
git clone https://github.com/zylvex-tech/zylvex-technologies.git
cd zylvex-technologies
```

### 2. Start Shared Auth Service
```bash
cd shared/auth
docker-compose up -d
```

### 3. Start Mind Mapper Backend
```bash
cd mind-mapper/backend-services
docker-compose up -d
```

### 4. Run Mobile App
```bash
cd mind-mapper/mobile-bci
npm install
npm start  # Expo development server
```

### 5. Access Services
- **Auth Service**: http://localhost:8001/docs
- **Mind Mapper API**: http://localhost:8002/docs
- **Mobile App**: Scan QR code with Expo Go app

## 🔧 Development

### Backend Development
```bash
cd mind-mapper/backend-services
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mindmapper
export AUTH_SERVICE_URL=http://localhost:8001
export JWT_SECRET_KEY=your-secret-key-here

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8002
```

### Mobile Development
```bash
cd mind-mapper/mobile-bci
npm install

# iOS
expo start --ios

# Android
expo start --android

# Web
expo start --web
```

## 🧪 Testing

### Backend Tests
```bash
cd mind-mapper/backend-services
pytest tests/ -v
```

### Mobile Tests
```bash
cd mind-mapper/mobile-bci
npm test
```

## 📊 Data Flow

```
1. User logs in → JWT token obtained from auth service
2. User creates mind map → POST /mindmaps
3. User adds nodes → POST /mindmaps/{id}/nodes
   - Focus level from slider determines node color/size
4. User edits mind map → Real-time updates
5. Session ends → POST /mindmaps/{id}/sessions
   - Stats saved: avg_focus, duration, node_count, focus_timeline
6. Data visualized in Session Stats screen
```

## 🔒 Security

- **JWT Authentication**: All endpoints require valid JWT tokens
- **Data Privacy**: Neural data processed on-device (future BCI integration)
- **Input Validation**: Pydantic models validate all API requests
- **CORS**: Configured for mobile and web clients

## 📈 Future Roadmap

### Phase 2: Real BCI Integration
- Integrate with Muse, NeuroSky, or OpenBCI devices
- Real-time EEG data processing pipeline
- Advanced focus detection algorithms

### Phase 3: Advanced Features
- Collaborative mind mapping
- AI-powered node suggestions
- Export to various formats (PDF, PNG, Markdown)
- Cloud sync across devices

### Phase 4: Enterprise Features
- Team workspaces
- Analytics dashboard
- API for third-party integrations
- Advanced privacy controls

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

Copyright © 2024 Zylvex Technologies Ltd. All rights reserved.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/zylvex-tech/zylvex-technologies/issues)
- **Email**: support@zylvex.tech
- **Documentation**: [docs.zylvex.tech](https://docs.zylvex.tech)

---

*"Visualize your thoughts, amplify your focus."* 🧠✨
