#!/bin/bash

# Start container and save the container id
CID=$(docker run -d swaggerapi/swagger-generator)

# allow for startup
sleep 5

# Get the IP of the running container
GEN_IP=$(docker inspect --format '{{.NetworkSettings.IPAddress}}' $CID)

# Execute an HTTP request and store the download link
RESULT=$(curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d '{
  "swaggerUrl": "http://petstore.swagger.io/v2/swagger.json"
}' 'http://localhost:8188/api/gen/clients/python' | jq '.link' | tr -d '"')

# Download the generated zip and redirect to a file
curl $RESULT > result.zip

# Shutdown the swagger generator image
docker stop $CID && docker rm $CID
