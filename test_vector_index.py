import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.operations import SearchIndexModel
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connect to your Atlas deployment
uri = "mongodb+srv://jnuts74:iuU0UkaK7UCzpBKn@cluster0.punniuo.mongodb.net/"
client = MongoClient(uri)

# Access your database and collection
database = client["searchDb"]
collection = database["documents"]

# Create your index model, then create the search index
search_index_model = SearchIndexModel(
  definition={
    "fields": [
      {
        "type": "vector",
        "numDimensions": 1536,
        "path": "chunks.embedding",
        "similarity": "cosine"
      }
    ]
  },
  name="vector-search-index",
  type="vectorSearch"
)

result = collection.create_search_index(model=search_index_model)
print("New search index named " + result + " is building.")

# Wait for initial sync to complete
print("Polling to check if the index is ready. This may take up to a minute.")
predicate=None
if predicate is None:
  predicate = lambda index: index.get("queryable") is True

while True:
  indices = list(collection.list_search_indexes(result))
  if len(indices) and predicate(indices[0]):
    break
  time.sleep(5)
print(result + " is ready for querying.")

client.close() 