# semantic-search-images
Using Vertex AI to perform Semantic Searches for images - Powered by Vertex AI Matching Engine and Vertex AI Multimodal Embeddings

More details can be found in this blog post: https://medium.com/google-cloud/how-to-perform-semantic-searches-for-images-with-vertex-ai-c7dacf8ee8ac

High-level Steps:
1) Upload of Images to GCS Bucket
2) Creation of image embeddings with `indexing.py`
3) Copy of embedding data to GCS bucket with `copyEmbeddingsToGCS.sh`
4) Creation of Index in Vertex AI Matching Engine with `vertexIndexCreation.sh`
5) Creation of Index Endpoint in Vertex AI Matching Engine with `vertexEndpointCreation.sh`
6) Deployment of Index in Vertex AI Matching Engine with `vertexIndexDeployment.sh`
7) Creation of Search Engine Web App with `main.py`
