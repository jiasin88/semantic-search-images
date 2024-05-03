#!/bin/bash

curl -X POST \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "Content-Type: application/json; charset=utf-8" \
    -d @request.json \
    "https://asia-southeast1-aiplatform.googleapis.com/v1/projects/serious-hall-371508/locations/asia-southeast1/indexEndpoints