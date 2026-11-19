URL Shortener – DevOps Project
A containerized URL Shortener application built using Python Flask, MongoDB, Docker, and Nginx, with an automated CI/CD pipeline and 
infrastructure provisioning using Terraform.
The project demonstrates an end-to-end DevOps workflow, including application containerization, automated testing, Docker image publishing, 
deployment, infrastructure as code and monitoring using Prometheus and Grafana.

Key objective: To build, deploy, monitor, and manage a web application using practical DevOps tools and workflows.

## Features

### Application Features
- Shorten long URLs using unique short codes.
- Redirect users from short URLs to their original destinations.
- Retrieve URL information using a REST API.
- Health check endpoint for application availability.
- MongoDB integration for persistent URL storage.

### DevOps Features
- Docker:Containerized the Flask application and its supporting services.
- Docker Compose: Managed the multi-container application stack.
- Nginx:Configured as a reverse proxy for incoming requests.
- GitHub Actions:Automated code quality checks and application tests through CI.
- GitHub Container Registry (GHCR):Built and published Docker images through the CI/CD workflow.
- Deployment Automation:Created a deployment script with rollback support.
- Terraform:Provisioned Docker infrastructure using Infrastructure as Code.
- Prometheus:Collected application metrics for monitoring.
- Grafana:Built dashboards to visualize application performance and request metrics.

## Technology Stack
- Python, Flask : Building the URL Shortener REST API 
- MongoDB : Storing original URLs and their short codes 
- Gunicorn : Running the Flask application in production 
- Nginx : Handling incoming HTTP requests and forwarding them to the application 
- Docker : Packaging the application and its dependencies 
- Docker Compose : Managing the application and supporting containers 
- GitHub Actions : Automating code quality checks, tests, and image publishing 
- GitHub Container Registry (GHCR) : Storing and distributing Docker images 
- Terraform : Provisioning Docker infrastructure through configuration files 
- Prometheus : Collecting and querying application metrics 
- Grafana : Creating dashboards for monitoring application performance 
- Pytest, Ruff : Running automated tests and checking code quality

APPLICATION FLOW 
Step 1: User:Sends an HTTP request.
Step 2: Nginx:Receives the request on port 8080.
Step 3: Gunicorn:Forwards the request to the Flask application
Step 4: Flask:Processes the URL Shortener request.
Step 5: MongoDB:Stores or retrieves URL information.
Step 6: Response:Flask returns the result through Nginx to the user.

CI/CD and Deployment Flow
1.Developer:Makes code changes
2.GitHub Repository:Receives pushed code
3.GitHub Actions:Triggers the CI/CD workflow
4.Ruff and Pytest:Check code quality and run tests
5.Docker Build:Builds the application image
6.GHCR:Stores the published Docker image
7.Deployment Script:Deploys the selected image version
8.Running Application:Application is deployed and available

Docker and Containerization
The application and its supporting services are containerized using Docker and managed through Docker Compose.
1.Dockerfile
The Flask application is packaged using a custom Dockerfile based on `python:3.12-slim`.

Key configurations include:
- Installing application dependencies.
- Copying application source code into the image.
- Running the application as a non-root user.
- Using Gunicorn as the production WSGI server.
- Exposing the application on port `8000`.

2.Docker Compose

Docker Compose manages the multi-container application environment.
Flask App - Handles URL shortening and API requests 
MongoDB - Provides persistent database storage 
Nginx - Acts as a reverse proxy 
Prometheus - Collects application metrics 
Grafana - Visualizes monitoring metrics 

3.Nginx Reverse Proxy
Nginx receives external HTTP requests on port `8080` and forwards them to the Flask application running through Gunicorn on port `8000`.

4.Docker Volumes and Networking
- Named volumes: Preserve MongoDB data, Prometheus metrics, and Grafana configuration and dashboard data across container restarts and recreation.
- Docker network: Allows application services to communicate using their Compose service names instead of external IP addresses.
This setup provides an isolated, reproducible environment where application components run independently but communicate with each other.

 CI/CD Pipeline with GitHub Actions

GitHub Actions is used to automate code quality checks, application testing, Docker image building, and image publishing.

1.Pipeline Workflow

1. Code Push: A developer pushes changes to the GitHub repository.
2. Workflow Trigger:GitHub Actions automatically starts the CI/CD workflow.
3. Code Quality:Ruff checks the Python code for formatting and linting issues.
4. Automated Testing:Pytest executes the application test suite.
5. Docker Build:A Docker image is built if the checks and tests pass.
6. Image Publishing:The Docker image is published to GitHub Container Registry (GHCR).

 2.Docker Image Versioning

Images are published with:
- A unique Git commit SHA tag for version-specific deployments.
- A `latest` tag representing the most recently published image.

3. Deployment Automation

A deployment script (`scripts/deploy.sh`) automates application deployment using a selected Docker image version.
It also maintains the previous deployment version to support rollback if a deployment needs to be reversed.
This workflow reduces manual effort and provides a consistent process for testing, building, publishing, and deploying application updates.

Infrastructure as Code with Terraform

Terraform is used to provision and manage the application's Docker infrastructure through configuration files.
The Docker provider (`kreuzwerker/docker`) allows Terraform to manage Docker resources.

1.Infrastructure Provisioned
- Docker Network: Creates a dedicated network for application communication.
- Docker Volume: Creates persistent storage for MongoDB.
- Docker Images: Manages the required application and service images.
- Docker Containers: Provisions MongoDB, the Flask application, and Nginx containers.

2.Terraform Workflow
The infrastructure is managed using the following Terraform commands:
terraform init
terraform plan
terraform apply

To remove the infrastructure managed by Terraform:
terraform destroy

Terraform maintains a state file (`terraform.tfstate`) to track the resources it manages.

Prometheus Monitoring

Prometheus is used to collect and store metrics from the URL Shortener application. 
It periodically scrapes the application's `/metrics` endpoint and makes the collected data available for monitoring and analysis.

1. Monitoring Configuration
- Metrics Endpoint: The Flask application exposes metrics through `/metrics`.
- Scrape Target: Prometheus connects to the application using the Docker Compose service address `app:8000`.
- Scrape Interval: Prometheus collects metrics every 15 seconds.
- Configuration File: `monitoring/prometheus.yml` defines the scrape configuration.

2. Metrics Collection Flow
1. The Flask application exposes metrics through `/metrics`.
2. Prometheus periodically sends requests to the metrics endpoint.
3. Prometheus collects and stores the metrics as time-series data.
4. Grafana uses Prometheus as its data source to visualize the collected metrics.

Grafana Dashboard

Grafana is used to visualize application metrics collected by Prometheus. 
A dashboard was created with panels to monitor request traffic, errors, endpoint activity, and response time.

Dashboard Panels

1. Requests Per Second (Total):
Displays the total number of HTTP requests received by the application per second. This helps understand overall application traffic.
2. Error Rate:
Displays the rate of application errors over time. This helps identify periods when requests are failing.
3. Requests Per Second by Endpoint:
Shows the request rate for individual API endpoints. This helps identify which endpoints receive the most traffic.
4. 95th Percentile Response Time (P95):
Displays the 95th percentile response time. This means 95% of recorded requests were completed within the displayed time, while the remaining 5% took longer.

Future Improvements

Deploy the application to a cloud platform such as AWS.
Introduce HTTPS using SSL/TLS certificates.
Add alert notifications.
Configure automated deployment to a cloud environment.
Strengthen application security with additional authentication and access controls.




Application is deployed and available
