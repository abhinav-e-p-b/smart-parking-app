# Deployment Guide for Smart Parking Application

## Prerequisites

- Docker & Docker Compose
- Python 3.9+
- Node.js 18+
- PostgreSQL 13+ (if not using Docker)

## Local Development Setup

### 1. Clone Repository

\`\`\`bash
git clone https://github.com/yourusername/smart-parking.git
cd smart-parking
\`\`\`

### 2. Run Setup Script

\`\`\`bash
chmod +x scripts/setup.sh
./scripts/setup.sh
\`\`\`

### 3. Start Development Servers

Terminal 1 - Backend:
\`\`\`bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
\`\`\`

Terminal 2 - Frontend:
\`\`\`bash
cd frontend
npm run dev
\`\`\`

Access at http://localhost:3000

## Docker Deployment

### 1. Using Docker Compose

\`\`\`bash
docker-compose up -d
\`\`\`

Services:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Database: postgresql://localhost:5432/smart_parking

### 2. View Logs

\`\`\`bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
\`\`\`

### 3. Stop Services

\`\`\`bash
docker-compose down
\`\`\`

## Production Deployment

### Option 1: Vercel (Frontend) + Railway (Backend)

#### Frontend Deployment (Vercel)

1. Push to GitHub
2. Connect repository to Vercel
3. Set environment variables:
   - `NEXT_PUBLIC_API_URL`: Production backend URL

#### Backend Deployment (Railway)

1. Create Railway project
2. Connect GitHub repository
3. Add environment variables:
   - `DATABASE_URL`: PostgreSQL connection string
   - `SECRET_KEY`: Generate secure key
   - `ML_MODELS_DIR`: Path to models

### Option 2: AWS Deployment

#### Backend on EC2

1. Create EC2 instance (Ubuntu 22.04)
2. SSH into instance
3. Clone repository and run setup
4. Use systemd to manage service:

\`\`\`ini
[Unit]
Description=Smart Parking Backend
After=network.target

[Service]
User=ubuntu
ExecStart=/home/ubuntu/smart-parking/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
\`\`\`

#### Database on RDS

1. Create PostgreSQL RDS instance
2. Update `DATABASE_URL` in environment variables
3. Run migrations

#### Frontend on CloudFront + S3

1. Build frontend: `npm run build`
2. Upload to S3 bucket
3. Configure CloudFront distribution
4. Set cache policies

### Option 3: DigitalOcean App Platform

1. Create new app
2. Connect GitHub repository
3. Configure services:
   - Frontend (Node.js 18)
   - Backend (Python 3.11)
4. Add PostgreSQL database
5. Set environment variables
6. Deploy

## Environment Variables

### Backend (.env)

\`\`\`env
DATABASE_URL=postgresql://user:password@host:5432/smart_parking
SECRET_KEY=your-production-secret-key
ML_MODELS_DIR=./models
FRONTEND_URL=https://yourdomain.com
GOOGLE_MAPS_API_KEY=your_api_key
\`\`\`

### Frontend (.env.local)

\`\`\`env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_GOOGLE_MAPS_KEY=your_api_key
\`\`\`

## Database Migrations

### Create Migration

\`\`\`bash
alembic revision --autogenerate -m "description"
\`\`\`

### Run Migration

\`\`\`bash
alembic upgrade head
\`\`\`

## Monitoring & Logs

### Backend Logs

\`\`\`bash
# Local
tail -f backend/app.log

# Docker
docker-compose logs -f backend

# Production (e.g., Railway)
railway logs --service backend
\`\`\`

### Performance Monitoring

- Frontend: Vercel Analytics
- Backend: Sentry for error tracking
- Database: CloudWatch or Datadog

## Scaling Considerations

- Use database read replicas for scaling
- Implement caching with Redis
- Use CDN for static assets
- Load balance multiple backend instances
- Implement rate limiting on API

## Troubleshooting

### Database Connection Issues

\`\`\`bash
# Test connection
psql postgresql://user:password@host:5432/smart_parking

# Check logs
docker-compose logs postgres
\`\`\`

### Backend Startup Issues

\`\`\`bash
# Check Python environment
python --version
pip list

# Test imports
python -c "import fastapi; print(fastapi.__version__)"
\`\`\`

### Frontend Build Issues

\`\`\`bash
# Clear cache
rm -rf .next node_modules
npm install
npm run build
\`\`\`

## Maintenance

### Regular Backups

\`\`\`bash
# PostgreSQL backup
pg_dump postgresql://user:password@host:5432/smart_parking > backup.sql

# Restore
psql postgresql://user:password@host:5432/smart_parking < backup.sql
\`\`\`

### Update Dependencies

\`\`\`bash
# Backend
pip list --outdated
pip install --upgrade package_name

# Frontend
npm outdated
npm update
\`\`\`

## Security Checklist

- [ ] Change default passwords
- [ ] Enable SSL/TLS
- [ ] Set strong SECRET_KEY
- [ ] Enable CORS only for trusted origins
- [ ] Use environment variables for secrets
- [ ] Enable database encryption
- [ ] Set up firewall rules
- [ ] Enable logging and monitoring
- [ ] Regular security updates
- [ ] Database backups
