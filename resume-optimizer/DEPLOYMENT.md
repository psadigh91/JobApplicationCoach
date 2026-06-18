# 🚀 Deployment Guide - Resume Optimizer

This guide covers deployment options for the Resume Optimizer application.

---

## 📋 Prerequisites

### **Required:**
- Docker 20.10+ and Docker Compose 1.29+
- 2GB RAM minimum (4GB recommended)
- 10GB disk space
- Anthropic API key

### **Optional:**
- Domain name (for production)
- SSL certificate (for HTTPS)
- Reverse proxy (nginx/Traefik)

---

## 🐳 Docker Deployment (Recommended)

### **1. Setup Environment:**

```bash
# Clone or navigate to project
cd resume-optimizer

# Create .env file
cat > .env << EOF
ANTHROPIC_API_KEY=your_api_key_here
EOF
```

### **2. Deploy with One Command:**

```bash
./deploy.sh
```

This script will:
- ✅ Validate environment variables
- ✅ Build Docker images
- ✅ Start containers
- ✅ Check health status

### **3. Access Application:**

- **Frontend:** http://localhost
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### **4. View Logs:**

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

### **5. Stop Services:**

```bash
./stop.sh

# Or with Docker Compose
docker-compose down

# Remove all data (database, uploads, exports)
docker-compose down -v
```

---

## 🔧 Manual Deployment

### **Backend:**

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env
cat > .env << EOF
ANTHROPIC_API_KEY=your_api_key_here
EOF

# Initialize database
python -c "from core.database import init_db; init_db()"

# Start server
uvicorn main:app --host 0.0.0.0 --port 8000
```

### **Frontend:**

```bash
cd frontend

# Install dependencies
npm install

# Create .env
cat > .env << EOF
VITE_API_URL=http://localhost:8000/api
EOF

# Build for production
npm run build

# Serve with nginx or serve
npx serve -s dist -p 80
```

---

## 🌐 Production Deployment

### **1. With Domain and SSL:**

Update `docker-compose.yml`:

```yaml
services:
  frontend:
    environment:
      - VIRTUAL_HOST=yourdomain.com
      - LETSENCRYPT_HOST=yourdomain.com
      - LETSENCRYPT_EMAIL=your@email.com
```

### **2. Behind Reverse Proxy:**

**nginx configuration:**

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### **3. Environment Variables:**

**Production `.env`:**

```bash
# API Keys
ANTHROPIC_API_KEY=your_production_key

# Database (if using PostgreSQL)
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Security
SECRET_KEY=generate_random_secret_key
CORS_ORIGINS=https://yourdomain.com

# Uploads
MAX_UPLOAD_SIZE=10485760  # 10MB
UPLOAD_DIR=/var/app/uploads
EXPORT_DIR=/var/app/exports

# Session
SESSION_EXPIRY_HOURS=24
```

---

## 🔒 Security Checklist

### **Before Production:**

- [ ] Change default ports if needed
- [ ] Set strong SECRET_KEY
- [ ] Configure CORS_ORIGINS
- [ ] Enable HTTPS/SSL
- [ ] Set up firewall rules
- [ ] Configure rate limiting
- [ ] Set up monitoring/logging
- [ ] Enable health checks
- [ ] Configure backup strategy
- [ ] Review file upload limits
- [ ] Set up automatic cleanup (24h)

---

## 📊 Health Checks

### **Backend Health:**
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

### **Frontend Health:**
```bash
curl http://localhost/health
# Expected: healthy
```

### **Database Check:**
```bash
docker-compose exec backend python -c "from core.database import init_db; init_db()"
```

---

## 🔄 Updates and Maintenance

### **Update Application:**

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### **Database Backup:**

```bash
# Backup database
docker-compose exec backend cp /app/database/resume_optimizer.db /app/database/backup.db

# Or from host
cp backend/database/resume_optimizer.db backend/database/backup_$(date +%Y%m%d).db
```

### **View Metrics:**

```bash
# Container stats
docker stats

# Disk usage
docker system df
```

---

## 🐛 Troubleshooting

### **Backend Won't Start:**

```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Missing ANTHROPIC_API_KEY
# - Port 8000 already in use
# - Database permission issues
```

### **Frontend Won't Connect:**

```bash
# Check if backend is running
curl http://localhost:8000/health

# Check frontend logs
docker-compose logs frontend

# Verify API URL in frontend/.env
```

### **Database Issues:**

```bash
# Reinitialize database
docker-compose exec backend python -c "from core.database import init_db; init_db()"

# Clear database (CAUTION: deletes all data)
rm backend/database/resume_optimizer.db
docker-compose restart backend
```

### **Out of Memory:**

```bash
# Increase Docker memory limit
# Docker Desktop > Settings > Resources > Memory

# Or in docker-compose.yml:
services:
  backend:
    mem_limit: 2g
```

---

## 📈 Scaling

### **Horizontal Scaling:**

```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      replicas: 3
    # Add load balancer
```

### **Database Migration:**

For production, switch to PostgreSQL:

```bash
# Update docker-compose.yml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: resume_optimizer
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password

  backend:
    environment:
      DATABASE_URL: postgresql://user:password@postgres/resume_optimizer
```

---

## 🎯 Performance Tips

1. **Enable Redis for caching** (optional)
2. **Use CDN for static assets**
3. **Configure nginx caching**
4. **Enable gzip compression**
5. **Optimize Claude API calls** (batch requests)
6. **Set up database indexes**
7. **Monitor API rate limits**

---

## 📞 Support

**Issues:**
- Check logs: `docker-compose logs`
- Review health checks
- Verify environment variables
- Check disk space: `df -h`

**Resources:**
- API Documentation: http://localhost:8000/docs
- Project README: README.md
- Quick Start: QUICKSTART.md

---

**🚀 Ready to deploy!**
