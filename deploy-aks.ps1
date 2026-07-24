<#
Provisiona RG + ACR + AKS do zero, builda as imagens no ACR e publica backend/frontend no cluster.
Revise as variaveis abaixo antes de rodar. Execute linha a linha na primeira vez.
#>

$ErrorActionPreference = "Stop"

# ---- variaveis: ajuste antes de rodar ----
$RESOURCE_GROUP = "poc-agent-rg"
$LOCATION       = "brazilsouth"
$ACR_NAME       = "pocagentacr$((Get-Random -Maximum 9999))"   # precisa ser globalmente unico
$AKS_NAME       = "poc-agent-aks"
$NODE_COUNT     = 2
$IMAGE_TAG      = "v1"
# -------------------------------------------

az login

az group create --name $RESOURCE_GROUP --location $LOCATION

az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic

# build das imagens direto no ACR (nao precisa de docker local)
az acr build --registry $ACR_NAME --image backend:$IMAGE_TAG ./backend
az acr build --registry $ACR_NAME --image frontend:$IMAGE_TAG ./frontend

az aks create `
  --resource-group $RESOURCE_GROUP `
  --name $AKS_NAME `
  --node-count $NODE_COUNT `
  --generate-ssh-keys `
  --attach-acr $ACR_NAME

az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_NAME --overwrite-existing

# --- secret com a OPENAI_API_KEY: crie manualmente, nao vai para o git ---
# kubectl create secret generic backend-secret --from-literal=OPENAI_API_KEY=<sua-chave>

kubectl apply -f k8s/backend-configmap.yaml

# substitui o placeholder <ACR_NAME> pelo nome real do registry antes de aplicar
(Get-Content k8s/backend-deployment.yaml)  -replace '<ACR_NAME>', $ACR_NAME | kubectl apply -f -
(Get-Content k8s/frontend-deployment.yaml) -replace '<ACR_NAME>', $ACR_NAME | kubectl apply -f -

kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-service.yaml

Write-Host "Aguardando IP publico do frontend..."
kubectl get svc frontend-svc --watch
