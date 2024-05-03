#!/bin/bash
gcloud ai index-endpoints deploy-index INDEX_ENDPOINT_ID \
  --deployed-index-id=DEPLOYED_INDEX_ID \
  --display-name=DEPLOYED_INDEX_NAME \
  --index=INDEX_ID \
  --project=PROJECT_ID \
  --region=LOCATION


  //Note that INDEX_ENDPOINT_ID here should be the ID of the endpoint that we have just created and the INDEX_ID should be the ID of the index we created in the indexing steps above. For our current case, INDEX_ENDPOINT_ID would be 3656641422448132096 and INDEX_ID would be 5844634377350283264.