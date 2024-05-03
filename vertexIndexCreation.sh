#!/bin/bash
gcloud ai indexes create \
  --metadata-file=index_metadata.json \
  --display-name=MultiModal-Embeddings \
  --project=serious-hall-371508 \
  --region=asia-southeast1