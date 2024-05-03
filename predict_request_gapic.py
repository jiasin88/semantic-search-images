# Copyright 2023 Google LLC.
# SPDX-License-Identifier: Apache-2.0
from absl import app
#from absl import flags
#import requests
from google.oauth2 import service_account
#import google.cloud.aiplatform.aiplatform_v1beta1 as aiplatform_v1beta1
from google.cloud import aiplatform_v1beta1
from google.cloud import aiplatform_v1
import base64
# Need to do pip install google-cloud-aiplatform for the following two imports.
# Also run: gcloud auth application-default login.
from google.cloud import aiplatform
from google.cloud import storage
from google.protobuf import struct_pb2
import sys
import time
import typing

"""
_IMAGE_FILE = flags.DEFINE_string('image_file', None, 'Image filename')
_TEXT = flags.DEFINE_string('text', None, 'Text to input')
_PROJECT = flags.DEFINE_string('project', None, 'Project id')
"""

# Inspired from https://stackoverflow.com/questions/34269772/type-hints-in-namedtuple.
class EmbeddingResponse(typing.NamedTuple):
  text_embedding: typing.Sequence[float]
  image_embedding: typing.Sequence[float]


class EmbeddingPredictionClient:
  """Wrapper around Prediction Service Client."""
  def __init__(self, project : str,
    location : str = "us-central1",
    api_regional_endpoint: str = "us-central1-aiplatform.googleapis.com"):
    client_options = {"api_endpoint": api_regional_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    self.client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)  
    self.location = location
    self.project = project

  """def insert_index_REST(self, vector_id:str, vector_embeddings:dict):
    #insert into index
    api_url="https://326965318.asia-southeast1-712487506603.vdb.vertexai.goog/v1/projects/${PROJECT_ID}/locations/${REGION}/indexes/${INDEX_ID}:upsertDatapoints"

    DATAPOINT_ID_1=
          DATAPOINT_ID_2=
          curl -H "Content-Type: application/json" -H "Authorization: Bearer `gcloud auth print-access-token`" https://${ENDPOINT}/v1/projects/${PROJECT_ID}/locations/${REGION}/indexes/${INDEX_ID}:upsertDatapoints \
          -d '{datapoints: [{datapoint_id: "'${DATAPOINT_ID_1}'", feature_vector: [...]},
          datapoint_id: "'${DATAPOINT_ID_2}'", feature_vector: [...]}]}'

  """

  def get_embedding(self, text : str = None, image_bytes : bytes = None):
    if not text and not image_bytes:
      raise ValueError('At least one of text or image_bytes must be specified.')

    instance = struct_pb2.Struct()
    if text:
      instance.fields['text'].string_value = text

    if image_bytes:
      encoded_content = base64.b64encode(image_bytes).decode("utf-8")
      image_struct = instance.fields['image'].struct_value
      image_struct.fields['bytesBase64Encoded'].string_value = encoded_content

    instances = [instance]
    endpoint = (f"projects/{self.project}/locations/{self.location}"
      "/publishers/google/models/multimodalembedding@001")
    response = self.client.predict(endpoint=endpoint, instances=instances)

    text_embedding = None
    if text:    
      text_emb_value = response.predictions[0]['textEmbedding']
      text_embedding = [v for v in text_emb_value]

    image_embedding = None
    if image_bytes:    
      image_emb_value = response.predictions[0]['imageEmbedding']
      image_embedding = [v for v in image_emb_value]

    return EmbeddingResponse(
      text_embedding=text_embedding,
      image_embedding=image_embedding)
        

  
def main(argv):
 
  gcs_image_path = "js-multimodal-embeddings/images"

  storage_client = storage.Client()
  bucket = storage_client.get_bucket("js-multimodal-embeddings")
  delimter="/"
  file_id="/images"
  files = bucket.list_blobs(prefix="images")


  client = EmbeddingPredictionClient(project="serious-hall-371508")

    # The AI Platform services require regional API endpoints.
  scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  
  # create a service account with `Vertex AI User` role granted in IAM page.
  # download the service account key https://developers.google.com/identity/protocols/oauth2/service-account#authorizingrequests
  sa_file_path = "serious-hall-371508-b584a49b4817.json"
 
  credentials = service_account.Credentials.from_service_account_file(
      sa_file_path, scopes=scopes
  )
  client_options = {
      "api_endpoint": "326965318.asia-southeast1-712487506603.vdb.vertexai.goog"
  }

  #print(len(files))
  dpList=[]

  for file in files:
      if "image" in file.content_type:
        print(file.public_url)
        with file.open('rb') as image_file:
          image_file_contents =image_file.read()
        response = client.get_embedding(image_bytes=image_file_contents)

        dp = aiplatform_v1beta1.IndexDatapoint(datapoint_id="123", feature_vector=response[0])
        dpList.append(dp)
  print(len(dpList))
  vertex_ai_index_client = aiplatform_v1.IndexServiceClient(
      credentials=credentials,
      client_options=client_options,
  )
  upsert_request = aiplatform_v1beta1.UpsertDatapointsRequest(index="js_deployed_index", datapoints=dpList)

  
  #aiplatform_v1beta1.IndexService.upsert_datapoints(request=upsert_request)

  insert_response=vertex_ai_index_client.upsert_datapoints(request=upsert_request)
  print("Insert Response:", insert_response)

  """
        if(file.metadata is not None):
          #there is a caption for this image
          print(file.metadata["caption"])
        

          response = client.get_embedding(text=file.metadata["caption"],image_bytes=image_file_contents)
          print("Response:", response[0:100])
          print("Text:",response[0][0:100])
          print("Image:",response[1][0:100])
          #call Rest API to upsert into index
          #responseCode = client.insert_index_REST(file.id, response[0])
          #write to json file
          with open("embeddingData3.json", "a") as f:
            f.write('{"id":"' + file.id + '",')
            #f.write('"text_embedding":[' + ",".join(str(x) for x in response[0]) + "], ")
            f.write('"embedding":[' + ",".join(str(x) for x in response[1]) + "]}")
            f.write("\n")
        else:
          response = client.get_embedding(image_bytes=image_file_contents)
          #write to json file
          with open("embeddingData3.json", "a") as f:
            f.write('{"id":"' + file.id + '",')
            f.write('"embedding":[' + ",".join(str(x) for x in response[0]) + "]}")
            f.write("\n")
        end = time.time()

        #i = len()
        
        with open("embeddingData.json", "a") as f:
          f.write('{"id":"' + file.id + '",')
          f.write('"embedding":[' + ",".join(str(x) for x in response[0]) + "]}")
          f.write("\n")
        """

  #js-multimodal-embeddings

  #gsutil cp data.json gs://js-multimodal-embeddings/data/data.json


if __name__ == "__main__":
    app.run(main)
