# Deployment Guide

Complete deployment guide for Oodaloo across development, staging, and production environments.

## Quick Start

### Development Setup
```bash
# Clone and setup
git clone <repo>
cd oodaloo
poetry install

# Environment setup
cp .env.example .env
# Edit .env with development settings

# Database setup
poetry run python scripts/create_tables.py

# Start development server
poetry run uvicorn main:app --reload
```

### Production Deployment
```bash
# Production environment
ENVIRONMENT=production
USE_MOCK_*=false
DATABASE_URL=postgresql://...

# Start production server
poetry run gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Environment Configuration

### **Development Environment**

**`.env` for Development**:
```bash
# Environment
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=sqlite:///oodaloo.db

# Mock Services (Fast Development)
USE_MOCK_EMAIL=true
USE_MOCK_QBO=true
USE_MOCK_PAYMENTS=true
USE_MOCK_HASH=true

# Background Jobs
USE_REDIS_JOBS=false  # In-memory for development

# Security (Development Only)
SECRET_KEY=dev_secret_key_change_in_production
EXTERNAL_WRITE_ENABLED=false
```

### **Staging Environment**

**`.env` for Staging**:
```bash
# Environment
ENVIRONMENT=staging
DEBUG=false

# Database
DATABASE_URL=postgresql://user:pass@staging-db:5432/oodaloo_staging

# Mixed Services (Real Email, Mock QBO)
USE_MOCK_EMAIL=false
USE_MOCK_QBO=true  # Keep QBO mocked for cost control
USE_MOCK_PAYMENTS=true
USE_MOCK_HASH=false

# Background Jobs
USE_REDIS_JOBS=true
REDIS_URL=redis://staging-redis:6379

# Real Email Service
SENDGRID_API_KEY=staging_sendgrid_key

# Security
SECRET_KEY=staging_secret_key_from_secrets_manager
EXTERNAL_WRITE_ENABLED=true
QBO_RATE_LIMIT_ENABLED=true
```

### **Production Environment**

**`.env` for Production**:
```bash
# Environment
ENVIRONMENT=production
DEBUG=false

# Database
DATABASE_URL=postgresql://user:pass@prod-db:5432/oodaloo

# Real Services
USE_MOCK_EMAIL=false
USE_MOCK_QBO=false
USE_MOCK_PAYMENTS=false
USE_MOCK_HASH=false

# Background Jobs
USE_REDIS_JOBS=true
REDIS_URL=redis://prod-redis:6379

# Email Service
SENDGRID_API_KEY=prod_sendgrid_key
SES_ACCESS_KEY_ID=prod_ses_key
SES_SECRET_ACCESS_KEY=prod_ses_secret

# QBO Integration
QBO_CLIENT_ID=prod_qbo_client_id
QBO_CLIENT_SECRET=prod_qbo_client_secret
QBO_SANDBOX=false

# Security
SECRET_KEY=prod_secret_key_from_secrets_manager
EXTERNAL_WRITE_ENABLED=true
QBO_RATE_LIMIT_ENABLED=true
QBO_WEBHOOK_TOKEN=prod_webhook_secret

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
LOG_LEVEL=INFO
```

## Database Deployment

### **SQLite → PostgreSQL Migration**

**Development** (SQLite):
```bash
# Simple file-based database
DATABASE_URL=sqlite:///oodaloo.db
poetry run python scripts/create_tables.py
```

**Production** (PostgreSQL):
```bash
# Install PostgreSQL dependencies
poetry add psycopg2-binary

# Update DATABASE_URL
DATABASE_URL=postgresql://user:pass@host:5432/oodaloo

# Run migrations
poetry run alembic upgrade head
```

### **Database Migration Strategy**

```bash
# Generate migration
poetry run alembic revision --autogenerate -m "Add runway reserves"

# Review migration file
# Edit alembic/versions/xxx_add_runway_reserves.py

# Apply migration
poetry run alembic upgrade head

# Rollback if needed
poetry run alembic downgrade -1
```

### **Database Backup Strategy**

**Development**:
```bash
# SQLite backup
cp oodaloo.db oodaloo_backup_$(date +%Y%m%d).db
```

**Production**:
```bash
# PostgreSQL backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated backups (cron)
0 2 * * * /usr/local/bin/pg_dump $DATABASE_URL | gzip > /backups/oodaloo_$(date +\%Y\%m\%d).sql.gz
```

## Container Deployment

### **Docker Configuration**

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Set work directory
WORKDIR /app

# Install dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

# Copy application
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash oodaloo
USER oodaloo

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

**docker-compose.yml** (Development):
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://oodaloo:password@db:5432/oodaloo
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - .:/app  # Development only
  
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: oodaloo
      POSTGRES_USER: oodaloo
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### **Production Docker Compose**

**docker-compose.prod.yml**:
```yaml
version: '3.8'

services:
  app:
    build: .
    restart: unless-stopped
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
      - redis
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.oodaloo.rule=Host(`api.oodaloo.com`)"
      - "traefik.http.routers.oodaloo.tls.certresolver=letsencrypt"
  
  db:
    image: postgres:15
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
  
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
  
  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - app

volumes:
  postgres_data:
  redis_data:
```

## Cloud Deployment

### **AWS Deployment**

**ECS Task Definition**:
```json
{
  "family": "oodaloo-app",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/oodalooTaskRole",
  "containerDefinitions": [
    {
      "name": "oodaloo-app",
      "image": "your-account.dkr.ecr.region.amazonaws.com/oodaloo:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:oodaloo/database-url"
        },
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:oodaloo/secret-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/oodaloo",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

**RDS Database Setup**:
```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
    --db-instance-identifier oodaloo-prod \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --engine-version 15.3 \
    --master-username oodaloo \
    --master-user-password $DB_PASSWORD \
    --allocated-storage 20 \
    --vpc-security-group-ids sg-xxxxxxxxx \
    --db-subnet-group-name oodaloo-db-subnet-group \
    --backup-retention-period 7 \
    --storage-encrypted
```

### **Heroku Deployment**

**Procfile**:
```
web: gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
worker: python -m runway.jobs.worker
release: python scripts/run_migrations.py
```

**heroku.yml**:
```yaml
build:
  docker:
    web: Dockerfile
addons:
  - plan: heroku-postgresql:mini
  - plan: heroku-redis:mini
```

**Deployment Commands**:
```bash
# Create Heroku app
heroku create oodaloo-prod

# Add addons
heroku addons:create heroku-postgresql:mini
heroku addons:create heroku-redis:mini

# Set environment variables
heroku config:set ENVIRONMENT=production
heroku config:set USE_MOCK_EMAIL=false
heroku config:set SENDGRID_API_KEY=your_key

# Deploy
git push heroku main

# Run migrations
heroku run python scripts/run_migrations.py

# Scale workers
heroku ps:scale web=2 worker=1
```

## CI/CD Pipeline

### **GitHub Actions Workflow**

**.github/workflows/deploy.yml**:
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install Poetry
      run: |
        curl -sSL https://install.python-poetry.org | python3 -
        echo "$HOME/.local/bin" >> $GITHUB_PATH
    
    - name: Install dependencies
      run: poetry install
    
    - name: Run tests
      run: |
        poetry run pytest -m "phase0 and not qbo" --cov=domains --cov=runway
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost/postgres
        USE_MOCK_EMAIL: true
        USE_MOCK_QBO: true
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-west-2
    
    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1
    
    - name: Build and push Docker image
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        ECR_REPOSITORY: oodaloo
        IMAGE_TAG: ${{ github.sha }}
      run: |
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
        docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to ECS
      run: |
        aws ecs update-service \
          --cluster oodaloo-cluster \
          --service oodaloo-service \
          --force-new-deployment
```

## Monitoring and Observability

### **Health Checks**

**Health Check Endpoint**:
```python
# main.py
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers."""
    checks = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }
    
    # Database connectivity
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        checks["database"] = "connected"
        db.close()
    except Exception as e:
        checks["database"] = f"error: {str(e)}"
        checks["status"] = "unhealthy"
    
    # Redis connectivity (if enabled)
    if os.getenv("USE_REDIS_JOBS") == "true":
        try:
            import redis
            r = redis.from_url(os.getenv("REDIS_URL"))
            r.ping()
            checks["redis"] = "connected"
        except Exception as e:
            checks["redis"] = f"error: {str(e)}"
    
    # QBO connectivity (if not mocked)
    if os.getenv("USE_MOCK_QBO") == "false":
        # Add QBO health check
        checks["qbo"] = "mocked"  # Or real check
    
    status_code = 200 if checks["status"] == "healthy" else 503
    return JSONResponse(content=checks, status_code=status_code)
```

### **Logging Configuration**

**logging.yml**:
```yaml
version: 1
disable_existing_loggers: false

formatters:
  default:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  json:
    format: '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: default
    stream: ext://sys.stdout
  
  file:
    class: logging.handlers.RotatingFileHandler
    level: INFO
    formatter: json
    filename: /var/log/oodaloo/app.log
    maxBytes: 10485760  # 10MB
    backupCount: 5

loggers:
  oodaloo:
    level: INFO
    handlers: [console, file]
    propagate: false
  
  runway.services:
    level: INFO
    handlers: [console, file]
    propagate: false
  
  domains.integrations:
    level: INFO
    handlers: [console, file]
    propagate: false

root:
  level: WARNING
  handlers: [console]
```

### **Metrics and Alerting**

**Prometheus Metrics**:
```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Request metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

# Business metrics
DIGEST_EMAILS_SENT = Counter('digest_emails_sent_total', 'Total digest emails sent')
QBO_API_CALLS = Counter('qbo_api_calls_total', 'Total QBO API calls', ['endpoint', 'status'])
RUNWAY_CALCULATIONS = Counter('runway_calculations_total', 'Total runway calculations')

# System metrics
ACTIVE_BUSINESSES = Gauge('active_businesses', 'Number of active businesses')
```

## Security Considerations

### **Environment Security**

**Secrets Management**:
```bash
# Development: .env file (gitignored)
SECRET_KEY=dev_secret

# Production: Environment variables or secrets manager
export SECRET_KEY=$(aws secretsmanager get-secret-value --secret-id oodaloo/secret-key --query SecretString --output text)
```

**HTTPS Configuration**:
```nginx
# nginx.conf
server {
    listen 80;
    server_name api.oodaloo.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.oodaloo.com;
    
    ssl_certificate /etc/ssl/certs/oodaloo.crt;
    ssl_certificate_key /etc/ssl/private/oodaloo.key;
    
    location / {
        proxy_pass http://app:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### **Database Security**

**Connection Security**:
```bash
# Use SSL connections
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require

# Connection pooling
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
```

**Backup Encryption**:
```bash
# Encrypted backups
pg_dump $DATABASE_URL | gpg --cipher-algo AES256 --compress-algo 1 --symmetric --output backup_$(date +%Y%m%d).sql.gpg
```

## Performance Optimization

### **Application Performance**

**Gunicorn Configuration**:
```bash
# Production server
gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 30 \
    --keepalive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100
```

**Database Optimization**:
```python
# Connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### **Caching Strategy**

**Redis Caching**:
```python
# Cache frequently accessed data
@cache.memoize(timeout=300)  # 5 minute cache
def get_business_runway(business_id: str):
    return calculate_runway(business_id)
```

## Troubleshooting

### **Common Deployment Issues**

**Database Connection Issues**:
```bash
# Test database connectivity
poetry run python -c "from db.session import SessionLocal; SessionLocal().execute('SELECT 1')"

# Check environment variables
env | grep DATABASE_URL
```

**QBO Integration Issues**:
```bash
# Check QBO configuration
env | grep QBO_

# Test QBO connection
poetry run python scripts/test_qbo_connection.py
```

**Performance Issues**:
```bash
# Check resource usage
docker stats

# Database query analysis
poetry run python scripts/analyze_slow_queries.py
```

---

**Next**: See `docs/architecture/` for architectural decision records and `docs/testing/` for testing strategies.
