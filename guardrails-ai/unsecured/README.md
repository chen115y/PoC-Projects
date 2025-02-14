Title: OpenAI functions streaming with Chainlit
Tags: [openai-functions]

# OpenAI Functions Streaming with Chainlit

This directory contains an example of how to integrate OpenAI's powerful language model with Chainlit to create an interactive chat application that can call custom functions defined in your code. The example demonstrates a simple function that fetches the current weather for a specified location.
## How to run the app locally

```bash
pip3 install -r requirements.txt
chainlit run app.py
```

## How to build the Docker image and run the app

```bash
docker buildx build --platform linux/amd64 -t ai-agent-1 . --progress=plain
docker run -p 8089:8089 ai-agent-1
```

## How to deploy the app to Azure

### Create Azure Container Registry

```bash
# azure login
az login
# Create Azure container registry
az acr create --resource-group ContainerRegistry --name analytixaicontainerregistry --sku Basic --location eastus
# Sign in to container registry
az acr login --name analytixaicontainerregistry
# Tag container image
az acr show --name analytixaicontainerregistry --query loginServer --output table
docker tag ai-agent-1 analytixaicontainerregistry.azurecr.io/ai-agent-1:v1
# Push image to Azure Container Registry
docker push analytixaicontainerregistry.azurecr.io/ai-agent-1:v1
# List images in Azure Container Registry
az acr repository list --name analytixaicontainerregistry --output table
# Update container registry settings to have admin enable true
az acr update --name analytixaicontainerregistry --admin-enabled true
```

### Deploy to Azure Container Instance

Get the password from the webpage of Azure Container Registry "analytixaicontainerregistry" | Access keys.

```bash
# az login
az login
az extension add --name containerapp --upgrade
az acr login --name analytixaicontainerregistry
# Create container app environment
az containerapp env create \
  --name managedEnvironment-Container-Analytix-AI \
  --resource-group ContainerRegistry \
  --location eastus
# Add/Create a workload profile to increase number of CPU cores and memory for the application
az containerapp env workload-profile add \
    --name managedEnvironment-Container-Analytix-AI \
    --resource-group ContainerRegistry \
    --workload-profile-name analytix-ai \
    --workload-profile-type D4 \
    --max-nodes 4 \
    --min-nodes 2
```

```bash
# Create container app
az containerapp create \
  --name aiagent1 \
  --resource-group ContainerRegistry \
  --registry-server analytixaicontainerregistry.azurecr.io \
  --image analytixaicontainerregistry.azurecr.io/ai-agent-1:v1 \
  --environment managedEnvironment-Container-Analytix-AI \
  --workload-profile-name analytix-ai\
  --cpu 4 \
  --memory 16Gi \
  --target-port 8089 \
  --ingress external \
  --query properties.configuration.ingress.fqdn
```

After the deployment is complete, you can access the application using the Fully Qualified Domain Name (FQDN) provided in the output of the last command.
Find the __Outbound Ip Addresses__ from the Azure portal under the "analytixaiagents" resource in the "Networking" section. Use this IP address to configure Networking firewall rules on the SQL server to allow access from the application. You can find the guidance of configuring firewall rules in the Azure documentation by visiting https://docs.microsoft.com/en-us/azure/azure-sql/database/firewall-configure or visiting this [tutorial](https://learn.microsoft.com/en-us/azure/azure-sql/database/secure-database-tutorial?view=azuresql)