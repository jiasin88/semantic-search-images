
import streamlit as st
from predict_request_gapic import *
import json

st.set_page_config(
     layout="wide",
     page_title="JS Lab",
     page_icon="https://api.dicebear.com/5.x/bottts-neutral/svg?seed=gptLAb"
)

# Sidebar
st.sidebar.header("About")
st.sidebar.markdown(
    "A place for me to experiment different LLM use cases, models, application frameworks and etc."
)


st.title("Performing Semantic Searches for Images with Vertex AI")
st.subheader("Powered by Vertex AI Multimodal Embeddings and Vertex AI Matching Engine")





#client to access multimodal-embeddings model to convert text to embeddings
client = EmbeddingPredictionClient(project="serious-hall-371508")


scopes = ["https://www.googleapis.com/auth/cloud-platform"]
sa_file_path = "serious-hall-371508-b584a49b4817.json"
credentials = service_account.Credentials.from_service_account_file(sa_file_path, scopes=scopes)
client_options = { "api_endpoint": "1256643097.asia-southeast1-712487506603.vdb.vertexai.goog"}

#client to access GCS bucket
storage_client = storage.Client(credentials=credentials)
bucket = storage_client.bucket("js-multimodal-embeddings")

#vertex ai client to do similarity matching
vertex_ai_client = aiplatform_v1beta1.MatchServiceClient(
      credentials=credentials,
      client_options=client_options,
  )

request = aiplatform_v1beta1.FindNeighborsRequest(
      index_endpoint="projects/serious-hall-371508/locations/asia-southeast1/indexEndpoints/3656641422448132096",
      deployed_index_id="js_index_id_unique",
)


allResults=[]

search_term = 'a picture of ' + st.text_input('Search: ')
if search_term !="a picture of ":
 converted_query_to_embedding = client.get_embedding(text=search_term)

 dp1 = aiplatform_v1beta1.IndexDatapoint(
      datapoint_id="0",
      feature_vector=converted_query_to_embedding[0])
 #pass the embedding to do matching
 query = aiplatform_v1beta1.FindNeighborsRequest.Query(
      datapoint=dp1,
  )
 request.queries.append(query)
 response = vertex_ai_client.find_neighbors(request)

 
 for r in response.nearest_neighbors:
    for n in r.neighbors:
        id = n.datapoint.datapoint_id
        path=id.split("'")[1]
        distance = n.distance
        if distance<0.91:
         allResults.append(bucket.blob(path).download_as_bytes())
         #st.write(distance)


if len(allResults)>=1:
 st.write("")
 st.write("These are the most relevant results matching your search query:")
 st.image(allResults, width=300)
elif search_term =="a picture of ":
 st.write("Please type in a search query above")
else:
 st.write("Sorry! There are no images matching your query. Please try again.")



