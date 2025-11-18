# Infoblox MCP Server - Production Deployment Guide

## Overview

This guide covers multiple deployment options for your Infoblox MCP server, from simple cloud hosting to enterprise-grade AWS deployment behind API Gateway.

**Current Setup:**
- FastMCP server with SSE (Server-Sent Events) transport
- Port 3001
- HTTP endpoint: `http://127.0.0.1:3001/sse`
- 98 MCP tools
- 4 service clients (IPAM, VPN, Security, SOC Insights)

---

## Deployment Options

### Option 1: AWS ECS Fargate + API Gateway (Recommended for Enterprise) 🏆

**Why this is best:**
- ✅ Fully managed (no servers to maintain)
- ✅ Auto-scaling based on load
- ✅ API Gateway provides: authentication, rate limiting, caching, CORS
- ✅ CloudWatch logs integration (works with your structlog)
- ✅ Custom domain with SSL/TLS
- ✅ Pay per use (cheap for MCP servers)

**Architecture:**
```
Internet → API Gateway (api.yourcompany.com/mcp)
            ↓ (with API key auth)
          Application Load Balancer
            ↓
          ECS Fargate Task (your MCP server)
            ↓
          Infoblox Cloud API
```

**Cost Estimate:**
- API Gateway: $3.50/million requests + $0.09/GB data transfer
- ECS Fargate: ~$30/month (1 vCPU, 2GB RAM, 24/7)
- ALB: ~$20/month
- **Total: ~$50-60/month** for production-ready setup

**Implementation:**

#### Step 1: Create Dockerfile
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:3001/health', timeout=2)"

# Run the server
CMD ["python", "mcp_infoblox.py"]
```

#### Step 2: Add Health Check to MCP Server
```python
# Add to mcp_infoblox.py before if __name__ == "__main__":

@mcp.app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    return {
        "status": "healthy",
        "service": "infoblox-mcp",
        "version": "1.0.0",
        "clients": {
            "ipam": client is not None,
            "vpn": niosxaas_client is not None,
            "security": atcfw_client is not None,
            "insights": insights_client is not None
        }
    }
```

#### Step 3: AWS Infrastructure (Terraform)

Create `terraform/main.tf`:

```hcl
# terraform/main.tf

provider "aws" {
  region = "us-east-1"
}

# ECR Repository for Docker images
resource "aws_ecr_repository" "infoblox_mcp" {
  name                 = "infoblox-mcp-server"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "mcp_cluster" {
  name = "infoblox-mcp-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# Task Definition
resource "aws_ecs_task_definition" "mcp_task" {
  family                   = "infoblox-mcp-task"
  requires_compatibilities = ["FARGATE"]
  network_mode            = "awsvpc"
  cpu                     = "512"  # 0.5 vCPU
  memory                  = "1024" # 1 GB
  execution_role_arn      = aws_iam_role.ecs_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "infoblox-mcp"
      image = "${aws_ecr_repository.infoblox_mcp.repository_url}:latest"

      portMappings = [
        {
          containerPort = 3001
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "INFOBLOX_BASE_URL"
          value = "https://csp.infoblox.com"
        }
      ]

      secrets = [
        {
          name      = "INFOBLOX_API_KEY"
          valueFrom = aws_secretsmanager_secret.infoblox_api_key.arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/infoblox-mcp"
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "mcp"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:3001/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])
}

# Store API key in Secrets Manager
resource "aws_secretsmanager_secret" "infoblox_api_key" {
  name        = "infoblox-mcp-api-key"
  description = "Infoblox API key for MCP server"
}

# Application Load Balancer
resource "aws_lb" "mcp_alb" {
  name               = "infoblox-mcp-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = var.public_subnet_ids

  enable_deletion_protection = false

  tags = {
    Name = "infoblox-mcp-alb"
  }
}

# Target Group
resource "aws_lb_target_group" "mcp_tg" {
  name        = "infoblox-mcp-tg"
  port        = 3001
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 3
  }
}

# ECS Service
resource "aws_ecs_service" "mcp_service" {
  name            = "infoblox-mcp-service"
  cluster         = aws_ecs_cluster.mcp_cluster.id
  task_definition = aws_ecs_task_definition.mcp_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [aws_security_group.ecs_sg.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.mcp_tg.arn
    container_name   = "infoblox-mcp"
    container_port   = 3001
  }

  depends_on = [aws_lb_listener.mcp_listener]
}

# API Gateway REST API
resource "aws_api_gateway_rest_api" "mcp_api" {
  name        = "infoblox-mcp-api"
  description = "API Gateway for Infoblox MCP Server"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# API Gateway VPC Link (connects to ALB)
resource "aws_api_gateway_vpc_link" "mcp_vpc_link" {
  name        = "infoblox-mcp-vpc-link"
  target_arns = [aws_lb.mcp_alb.arn]
}

# API Gateway Resource (proxy all requests)
resource "aws_api_gateway_resource" "mcp_proxy" {
  rest_api_id = aws_api_gateway_rest_api.mcp_api.id
  parent_id   = aws_api_gateway_rest_api.mcp_api.root_resource_id
  path_part   = "{proxy+}"
}

# API Gateway Method
resource "aws_api_gateway_method" "mcp_proxy_method" {
  rest_api_id   = aws_api_gateway_rest_api.mcp_api.id
  resource_id   = aws_api_gateway_resource.mcp_proxy.id
  http_method   = "ANY"
  authorization = "API_KEY"
  api_key_required = true
}

# API Gateway Integration (to ALB)
resource "aws_api_gateway_integration" "mcp_integration" {
  rest_api_id = aws_api_gateway_rest_api.mcp_api.id
  resource_id = aws_api_gateway_resource.mcp_proxy.id
  http_method = aws_api_gateway_method.mcp_proxy_method.http_method

  type                    = "HTTP_PROXY"
  uri                     = "http://${aws_lb.mcp_alb.dns_name}/{proxy}"
  integration_http_method = "ANY"
  connection_type         = "VPC_LINK"
  connection_id           = aws_api_gateway_vpc_link.mcp_vpc_link.id

  request_parameters = {
    "integration.request.path.proxy" = "method.request.path.proxy"
  }
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "mcp_deployment" {
  rest_api_id = aws_api_gateway_rest_api.mcp_api.id
  stage_name  = "prod"

  depends_on = [aws_api_gateway_integration.mcp_integration]
}

# API Gateway Usage Plan (for rate limiting)
resource "aws_api_gateway_usage_plan" "mcp_usage_plan" {
  name = "infoblox-mcp-usage-plan"

  api_stages {
    api_id = aws_api_gateway_rest_api.mcp_api.id
    stage  = aws_api_gateway_deployment.mcp_deployment.stage_name
  }

  quota_settings {
    limit  = 10000
    period = "DAY"
  }

  throttle_settings {
    burst_limit = 100
    rate_limit  = 50
  }
}

# API Key
resource "aws_api_gateway_api_key" "mcp_api_key" {
  name = "infoblox-mcp-api-key"
}

# Associate API Key with Usage Plan
resource "aws_api_gateway_usage_plan_key" "mcp_usage_plan_key" {
  key_id        = aws_api_gateway_api_key.mcp_api_key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.mcp_usage_plan.id
}

# Outputs
output "api_gateway_url" {
  value = "${aws_api_gateway_deployment.mcp_deployment.invoke_url}/sse"
  description = "MCP Server SSE endpoint"
}

output "api_key" {
  value     = aws_api_gateway_api_key.mcp_api_key.value
  sensitive = true
  description = "API Gateway API Key for authentication"
}
```

#### Step 4: Deploy to AWS

```bash
# 1. Build and push Docker image
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker build -t infoblox-mcp .
docker tag infoblox-mcp:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/infoblox-mcp-server:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/infoblox-mcp-server:latest

# 2. Store Infoblox API key in Secrets Manager
aws secretsmanager put-secret-value \
  --secret-id infoblox-mcp-api-key \
  --secret-string '{"INFOBLOX_API_KEY":"your-api-key-here"}'

# 3. Deploy infrastructure
cd terraform
terraform init
terraform plan
terraform apply

# 4. Get the API endpoint
terraform output api_gateway_url
# Returns: https://abc123.execute-api.us-east-1.amazonaws.com/prod/sse

# 5. Get the API key
terraform output -raw api_key
```

#### Step 5: Test Deployment

```bash
# Test with API key
curl -H "x-api-key: YOUR_API_KEY" \
  https://abc123.execute-api.us-east-1.amazonaws.com/prod/sse
```

---

### Option 2: FastMCP Cloud (Easiest - 1-Click Deploy) ⚡

**Why this is easiest:**
- ✅ Purpose-built for MCP servers
- ✅ One command deployment
- ✅ Free tier available
- ✅ Built-in monitoring
- ✅ No infrastructure management

**Steps:**

```bash
# 1. Install FastMCP CLI
pip install fastmcp

# 2. Login to FastMCP Cloud
fastmcp login

# 3. Deploy
fastmcp deploy mcp_infoblox.py

# 4. Get the public URL
# Returns: https://your-server.fastmcp.cloud/sse
```

**Pricing:**
- Free: Up to 10K requests/month
- Pro: $29/month - 1M requests
- Enterprise: Custom pricing

**Official Docs:** https://fastmcp.cloud/docs/deploy

---

### Option 3: Railway / Render / Fly.io (Quick Cloud Deploy) 🚀

**Why this is good for prototypes:**
- ✅ Simple git push deployment
- ✅ Free tier available
- ✅ Automatic HTTPS
- ✅ Fast setup (5 minutes)

#### Railway Deployment

**Step 1:** Create `railway.json`
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Step 2:** Create `Procfile`
```
web: python mcp_infoblox.py
```

**Step 3:** Deploy
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Add environment variables
railway variables set INFOBLOX_API_KEY="your-key"
railway variables set INFOBLOX_BASE_URL="https://csp.infoblox.com"

# Deploy
railway up

# Get URL
railway domain
```

**Pricing:** $5/month (starter plan)

---

### Option 4: Docker Compose + Cloud VM (DigitalOcean/Linode) 🐳

**Why this is good for cost control:**
- ✅ Cheapest option ($6-12/month)
- ✅ Full control
- ✅ Simple scaling

**Step 1:** Create `docker-compose.yml`
```yaml
version: '3.8'

services:
  infoblox-mcp:
    build: .
    ports:
      - "3001:3001"
    environment:
      - INFOBLOX_API_KEY=${INFOBLOX_API_KEY}
      - INFOBLOX_BASE_URL=https://csp.infoblox.com
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3001/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 10s

  # Optional: Nginx reverse proxy with SSL
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - infoblox-mcp
    restart: unless-stopped
```

**Step 2:** Create `nginx.conf`
```nginx
events {
    worker_connections 1024;
}

http {
    upstream mcp_backend {
        server infoblox-mcp:3001;
    }

    server {
        listen 80;
        server_name your-domain.com;

        # Redirect to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://mcp_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;

            # SSE specific headers
            proxy_buffering off;
            proxy_cache off;
        }
    }
}
```

**Step 3:** Deploy to DigitalOcean
```bash
# Create droplet ($6/month)
doctl compute droplet create infoblox-mcp \
  --image ubuntu-22-04-x64 \
  --size s-1vcpu-1gb \
  --region nyc1

# SSH into droplet
ssh root@your-droplet-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone your repo
git clone https://github.com/yourusername/subnet_mcp.git
cd subnet_mcp

# Set environment variables
echo "INFOBLOX_API_KEY=your-key" > .env

# Deploy
docker-compose up -d

# Check logs
docker-compose logs -f
```

---

### Option 5: Kubernetes (For Enterprise Scale) ☸️

**When to use:**
- Multiple regions
- High availability required
- 1000+ requests/second

See `kubernetes/` folder for full manifests (can create if needed).

---

## Security Checklist

Before deploying to production:

- [ ] **API Key Management**
  - Store in AWS Secrets Manager / HashiCorp Vault
  - Rotate keys every 90 days
  - Never commit to git

- [ ] **Authentication**
  - Require API Gateway API keys
  - Or implement OAuth2/JWT
  - Rate limit per key (100 req/min)

- [ ] **Network Security**
  - Run in private subnet (ECS tasks)
  - Use VPC endpoints for AWS services
  - Enable VPC Flow Logs

- [ ] **Encryption**
  - HTTPS/TLS only (no HTTP)
  - Encrypt environment variables
  - Encrypt logs at rest

- [ ] **Monitoring**
  - CloudWatch alarms for errors
  - CloudWatch dashboards
  - Log aggregation (CloudWatch Logs Insights)

- [ ] **Compliance**
  - Enable CloudTrail for audit logs
  - Tag all resources
  - Set up cost alerts

---

## Monitoring & Observability

### CloudWatch Dashboard

```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/ApiGateway", "Count", {"stat": "Sum"}],
          [".", "4XXError", {"stat": "Sum"}],
          [".", "5XXError", {"stat": "Sum"}]
        ],
        "period": 300,
        "stat": "Sum",
        "region": "us-east-1",
        "title": "API Gateway Metrics"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/ECS", "CPUUtilization"],
          [".", "MemoryUtilization"]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "ECS Resource Usage"
      }
    }
  ]
}
```

---

## Cost Comparison

| Option | Cost/Month | Effort | Best For |
|--------|-----------|--------|----------|
| **AWS ECS + API Gateway** | $50-60 | High | Enterprise production |
| **FastMCP Cloud** | $0-29 | Very Low | Quick start |
| **Railway/Render** | $5-10 | Low | Prototypes |
| **DigitalOcean VM** | $6-12 | Medium | Cost-conscious |
| **Kubernetes** | $100+ | Very High | Large scale |

---

## Recommended Approach

### For You (Infoblox MCP):

**Phase 1: Test with FastMCP Cloud (Week 1)**
- Deploy with `fastmcp deploy`
- Share with 5-10 users
- Validate functionality
- Cost: $0

**Phase 2: Production on AWS (Week 2-3)**
- Deploy to ECS Fargate + API Gateway
- Configure custom domain (mcp.yourcompany.com)
- Set up monitoring and alerts
- Cost: ~$50/month

**Phase 3: Optimize (Month 2)**
- Add response caching (80% cost reduction)
- Add circuit breakers
- Fine-tune scaling policies
- Cost: ~$20/month (after caching)

---

## Next Steps

Would you like me to:

1. **Create complete AWS deployment with Terraform** (full infrastructure as code)
2. **Set up FastMCP Cloud deployment** (quickest option)
3. **Create Docker Compose setup for DigitalOcean** (cheapest option)
4. **Create Kubernetes manifests** (enterprise scale)
5. **Add authentication layer** (OAuth2, JWT, or API key management)

Let me know which deployment approach you prefer!
