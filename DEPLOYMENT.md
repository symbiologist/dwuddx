# Deployment Guide

This guide provides instructions for deploying the Medical AI Assistant application to Render using Docker.

## Prerequisites

- A [Render](https://render.com/) account
- A Git repository (GitHub, GitLab, etc.) containing your application code
- API keys for the LLM providers (Gemini, Claude)

## Deployment Steps

### 1. Push Your Code to a Git Repository

Ensure all your code, including the Docker configuration files, is pushed to your Git repository.

```bash
git add .
git commit -m "Prepare for Render deployment"
git push
```

### 2. Create a New Web Service on Render

1. Log in to your Render account
2. Click on "New" and select "Web Service"
3. Connect your Git repository
4. Select the repository containing your application

### 3. Configure the Web Service

1. Select "Use render.yaml from repository" if prompted
2. If not prompted, configure the service manually:
   - **Name**: medical-ai-assistant (or your preferred name)
   - **Environment**: Docker
   - **Region**: Choose the region closest to your users
   - **Branch**: main (or your default branch)
   - **Plan**: Free (or select a paid plan for better performance)

### 4. Set Environment Variables

Add your API keys as environment variables in the Render dashboard:

1. Scroll down to the "Environment" section
2. Add the following environment variables:
   - `GEMINI_API_KEY`: Your Gemini API key
   - `ANTHROPIC_API_KEY`: Your Claude API key
   - `PORT`: 8000

### 5. Deploy the Service

1. Click "Create Web Service"
2. Render will automatically build and deploy your application
3. Once the deployment is complete, you can access your application at the provided Render URL (e.g., https://medical-ai-assistant.onrender.com)

## Troubleshooting

### Application Not Starting

If your application fails to start, check the logs in the Render dashboard for error messages. Common issues include:

- Missing environment variables
- Incorrect port configuration
- Dependency installation failures

### API Key Issues

If the application starts but fails to generate responses, verify that your API keys are correctly set in the Render dashboard and that they have the necessary permissions.

### Performance Issues

If you experience slow response times or timeouts, consider upgrading to a paid plan on Render for better performance.

## Updating Your Deployment

When you make changes to your application:

1. Push the changes to your Git repository
2. Render will automatically detect the changes and redeploy your application (if auto-deploy is enabled)
3. If auto-deploy is disabled, manually trigger a deploy from the Render dashboard

## Local Testing Before Deployment

To test your Docker setup locally before deploying to Render, you need to have Docker installed on your machine:

```bash
# Build the Docker image
docker build -t medical-ai-assistant .

# Run the container
docker run -p 8000:8000 -e GEMINI_API_KEY=your_key -e ANTHROPIC_API_KEY=your_key medical-ai-assistant
```

Then access the application at http://localhost:8000
