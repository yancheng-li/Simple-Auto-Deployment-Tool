#!/usr/bin/env python3
"""
Auto Deployment Tool 
A simplified implementation
"""

import os
import re
import json
import requests
import zipfile
import tempfile
from dataclasses import dataclass

@dataclass
class AppConfig:
    """Application configuration - simple data class"""
    name: str
    type: str = "python"
    port: int = 5000
    cloud: str = "aws"

class SimpleNLP:
    """Simple natural language processing"""
    
    def parse(self, text):
        """Parse user input"""
        text = text.lower()
        
        # Simple keyword matching
        app_type = "python"  # default
        if "flask" in text:
            app_type = "flask"
        elif "node" in text or "javascript" in text:
            app_type = "nodejs"
        elif "django" in text:
            app_type = "django"
        
        # Detect cloud provider
        cloud = "aws"
        if "gcp" in text or "google" in text:
            cloud = "gcp"
        elif "azure" in text or "microsoft" in text:
            cloud = "azure"
        
        # Extract app name (simple version)
        words = text.split()
        name = "my-app"
        for word in words:
            if len(word) > 3 and word not in ["deploy", "this", "application", "using"]:
                name = word.replace(" ", "-")
                break
        
        return AppConfig(name=name, type=app_type, cloud=cloud)

class RepoAnalyzer:
    """Code repository analyzer - basic version"""
    
    def analyze_repo(self, url):
        """Analyze repository content"""
        if not url:
            return {"type": "unknown", "port": 5000}
        
        try:
            # Download repository (simplified version)
            print(f"Analyzing repository: {url}")
            
            # Convert GitHub URL
            if "github.com" in url and not url.endswith(".zip"):
                url = url + "/archive/main.zip"
            
            # Download file
            response = requests.get(url, timeout=10)
            
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, "repo.zip")
                with open(zip_path, "wb") as f:
                    f.write(response.content)
                
                # Extract and analyze
                with zipfile.ZipFile(zip_path) as zip_file:
                    zip_file.extractall(temp_dir)
                
                # Find project files
                return self._analyze_files(temp_dir)
                
        except Exception as e:
            print(f"Repository analysis failed: {e}")
            return {"type": "unknown", "port": 5000}
    
    def _analyze_files(self, directory):
        """Analyze file content - simple implementation"""
        app_type = "python"
        port = 5000
        
        # Walk through files looking for clues
        for root, dirs, files in os.walk(directory):
            for file in files:
                # Check Python project
                if file == "requirements.txt":
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read().lower()
                            if "flask" in content:
                                app_type = "flask"
                                port = 5000
                            elif "django" in content:
                                app_type = "django"
                                port = 8000
                    except:
                        pass
                
                # Check Node.js project
                elif file == "package.json":
                    app_type = "nodejs"
                    port = 3000
                
                # Check port configuration
                elif file.endswith(('.py', '.js')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                            # Simple port matching
                            port_match = re.search(r'port.*?(\d{4})', content, re.IGNORECASE)
                            if port_match:
                                port = int(port_match.group(1))
                    except:
                        pass
        
        return {"type": app_type, "port": port}

class ConfigGenerator:
    """Configuration file generator - basic templates"""
    
    def generate_docker(self, config):
        """Generate simple Dockerfile"""
        if config.type == "flask":
            return f"""FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE {config.port}
CMD ["python", "app.py"]"""
        
        elif config.type == "django":
            return f"""FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput
EXPOSE {config.port}
CMD ["python", "manage.py", "runserver", "0.0.0.0:{config.port}"]"""
        
        elif config.type == "nodejs":
            return f"""FROM node:16
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE {config.port}
CMD ["npm", "start"]"""
        
        else:
            return f"""FROM python:3.9
WORKDIR /app
COPY . .
EXPOSE {config.port}
CMD ["python", "app.py"]"""
    
    def generate_terraform(self, config):
        """Generate basic Terraform configuration"""
        # Simplified AWS ECS configuration
        return f"""# Basic AWS deployment configuration
terraform {{
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = "us-west-2"
}}

# Simple ECS cluster
resource "aws_ecs_cluster" "app" {{
  name = "{config.name}-cluster"
}}

# Container definition
resource "aws_ecs_task_definition" "app" {{
  family                   = "{config.name}"
  requires_compatibilities = ["FARGATE"]
  network_mode            = "awsvpc"
  cpu                     = 256
  memory                  = 512
  
  container_definitions = jsonencode([{{
    name  = "{config.name}"
    image = "{config.name}:latest"
    
    portMappings = [{{
      containerPort = {config.port}
      hostPort      = {config.port}
    }}]
  }}])
}}

# Output information
output "cluster_name" {{
  description = "ECS cluster name"
  value = aws_ecs_cluster.app.name
}}"""

    def generate_deploy_script(self, config):
        """Generate simple deployment script"""
        return f"""#!/bin/bash
# Simple deployment script

echo "Starting deployment of {config.name}..."

# Check environment
if ! command -v docker &> /dev/null; then
    echo "Please install Docker first"
    exit 1
fi

if ! command -v terraform &> /dev/null; then
    echo "Please install Terraform first"  
    exit 1
fi

# Build image
echo "Building Docker image..."
docker build -t {config.name}:latest .

# Initialize Terraform
echo "Initializing Terraform..."
terraform init

# Deploy
echo "Deploying to cloud..."
terraform plan
terraform apply -auto-approve

echo "Deployment complete!"
"""

    def generate_docker_compose(self, config):
        """Generate docker-compose for local development"""
        return f"""version: '3.8'

services:
  {config.name}:
    build: .
    ports:
      - "{config.port}:{config.port}"
    environment:
      - NODE_ENV=development
      - FLASK_ENV=development
    volumes:
      - .:/app
    restart: unless-stopped
"""

class AutoDeployTool:
    """Main auto deployment tool class"""
    
    def __init__(self):
        self.nlp = SimpleNLP()
        self.repo_analyzer = RepoAnalyzer()
        self.generator = ConfigGenerator()
    
    def process(self, description, repo_url=None):
        """Process deployment request"""
        print(f"Processing request: {description}")
        
        # 1. Parse natural language
        config = self.nlp.parse(description)
        print(f"Detected configuration: {config.name} ({config.type})")
        
        # 2. Check code repository
        if repo_url:
            repo_info = self.repo_analyzer.analyze_repo(repo_url)
            if repo_info["type"] != "unknown":
                config.type = repo_info["type"]
                config.port = repo_info["port"]
            print(f"Updated configuration: {config.type}, port: {config.port}")
        
        # 3. Generate configuration files
        print("Generating configuration files...")
        
        files = {
            "Dockerfile": self.generator.generate_docker(config),
            "main.tf": self.generator.generate_terraform(config),
            "deploy.sh": self.generator.generate_deploy_script(config),
            "docker-compose.yml": self.generator.generate_docker_compose(config)
        }
        
        return {
            "config": config,
            "files": files,
            "success": True
        }
    
    def save_files(self, result):
        """Save generated files"""
        config = result["config"]
        output_dir = f"deployment_{config.name}"
        
        os.makedirs(output_dir, exist_ok=True)
        
        for filename, content in result["files"].items():
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Give shell scripts execute permission
            if filename.endswith('.sh'):
                os.chmod(filepath, 0o755)
        
        # Generate simple README
        readme = f"""# {config.name.title()} Deployment Configuration

Auto-generated deployment configuration for your {config.type} application.

## Quick Start

1. Build Docker image:
```bash
docker build -t {config.name} .
```

2. Deploy to AWS:
```bash
terraform init
terraform apply
```

3. Local development:
```bash
docker-compose up
```

## Files Description
- `Dockerfile`: Docker image configuration
- `main.tf`: Terraform infrastructure configuration  
- `deploy.sh`: Automated deployment script
- `docker-compose.yml`: Local development environment

## Configuration Details
- **Application Type**: {config.type}
- **Port**: {config.port}
- **Cloud Provider**: {config.cloud.upper()}

Generated by: Auto Deployment Tool
"""
        
        with open(os.path.join(output_dir, "README.md"), 'w', encoding='utf-8') as f:
            f.write(readme)
        
        print(f"Files saved to: {output_dir}/")
        return output_dir

def main():
    """Main function - simple command line interface"""
    print("Simple Auto Deployment Tool")
    print("=" * 40)
    
    # Get user input
    description = input("Describe your deployment needs: ").strip()
    if not description:
        print("Please enter a deployment description")
        return
    
    repo_url = input("Code repository URL (optional): ").strip()
    if not repo_url:
        repo_url = None
    
    # Process request
    tool = AutoDeployTool()
    
    try:
        result = tool.process(description, repo_url)
        
        if result["success"]:
            output_dir = tool.save_files(result)
            
            print(f"\nSuccess!")
            print(f"Output directory: {output_dir}")
            print(f"Run: cd {output_dir} && ./deploy.sh")
            
            # Show what was generated
            config = result["config"]
            print(f"\nGenerated configuration:")
            print(f"   • Application: {config.name}")
            print(f"   • Type: {config.type}")
            print(f"   • Port: {config.port}")
            print(f"   • Cloud: {config.cloud}")
            print(f"   • Files: {len(result['files'])} configuration files")
            
        else:
            print("Processing failed")
    
    except Exception as e:
        print(f"Error: {e}")

def demo():
    """Demo function"""
    print("Demo Mode - Auto Deployment Tool")
    print("=" * 50)
    
    # Demo scenarios
    scenarios = [
        ("Deploy my Flask app on AWS", "https://github.com/Arvo-AI/hello_world"),
        ("Deploy Node.js application using containers", None),
        ("Deploy Django web app", None)
    ]
    
    tool = AutoDeployTool()
    
    for i, (desc, repo) in enumerate(scenarios, 1):
        print(f"\nDemo Scenario {i}: {desc}")
        if repo:
            print(f"Repository: {repo}")
        
        try:
            result = tool.process(desc, repo)
            if result["success"]:
                config = result["config"]
                print("Configuration generated successfully")
                print(f"   • App: {config.name} ({config.type})")
                print(f"   • Port: {config.port}")
                print(f"   • Files: {len(result['files'])}")
                
                # Show snippet of generated Dockerfile
                dockerfile = result["files"]["Dockerfile"]
                print(f"Dockerfile preview:")
                print("   " + dockerfile.split('\n')[0])
                print("   " + dockerfile.split('\n')[1])
                print("   ...")
            else:
                print("Failed")
        except Exception as e:
            print(f"Error: {e}")
        
        if i < len(scenarios):
            print("-" * 40)

def test_basic_functionality():
    """Basic functionality test"""
    print("Running basic tests...")
    
    tool = AutoDeployTool()
    
    # Test 1: Basic NLP parsing
    config = tool.nlp.parse("Deploy my Flask app on AWS")
    assert config.type == "flask"
    assert config.cloud == "aws"
    print("Test 1 passed: NLP parsing")
    
    # Test 2: File generation
    result = tool.process("Deploy Flask application")
    assert result["success"] == True
    assert "Dockerfile" in result["files"]
    assert "main.tf" in result["files"]
    print("Test 2 passed: File generation")
    
    # Test 3: Repository analysis (without network call)
    analyzer = RepoAnalyzer()
    repo_info = analyzer._analyze_files(".")  # Current directory
    assert "type" in repo_info
    assert "port" in repo_info
    print("Test 3 passed: Repository analysis")
    
    print("All basic tests passed!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--demo":
            demo()
        elif sys.argv[1] == "--test":
            test_basic_functionality()
        elif sys.argv[1] == "--help":
            print("""
Auto Deployment Tool - Usage:

Interactive mode:
    python auto_deploy.py

Command line mode:
    python auto_deploy.py "Deploy Flask app" [repo_url]

Demo mode:
    python auto_deploy.py --demo

Test mode:
    python auto_deploy.py --test

Examples:
    python auto_deploy.py "Deploy my Flask app on AWS"
    python auto_deploy.py "Deploy Node.js API" https://github.com/user/repo
            """)
        else:
            # Command line mode with arguments
            desc = sys.argv[1]
            repo = sys.argv[2] if len(sys.argv) > 2 else None
            
            tool = AutoDeployTool()
            result = tool.process(desc, repo)
            
            if result["success"]:
                tool.save_files(result)
                print("Configuration generated successfully!")
            else:
                print("Processing failed")
    else:
        # Interactive mode
        main()
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--demo":
            demo()
        elif sys.argv[1] == "--test":
            test_basic_functionality()
        elif sys.argv[1] == "--help":
            print("""
Auto Deployment Tool - Usage:

Interactive mode:
    python auto_deploy.py

Command line mode:
    python auto_deploy.py "Deploy Flask app" [repo_url]

Demo mode:
    python auto_deploy.py --demo

Test mode:
    python auto_deploy.py --test

Examples:
    python auto_deploy.py "Deploy my Flask app on AWS"
    python auto_deploy.py "Deploy Node.js API" https://github.com/user/repo
            """)
        else:
            # Command line mode with arguments
            desc = sys.argv[1]
            repo = sys.argv[2] if len(sys.argv) > 2 else None
            
            tool = AutoDeployTool()
            result = tool.process(desc, repo)
            
            if result["success"]:
                tool.save_files(result)
                print("✅ Configuration generated successfully!")
            else:
                print("❌ Processing failed")
    else:
        # Interactive mode
        main()
