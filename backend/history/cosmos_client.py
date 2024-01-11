import os
import logging
from azure.identity import DefaultAzureCredential
from .cosmosdbservice import CosmosConversationClient


def init_cosmosdb_client() -> CosmosConversationClient:
  # Initialize a CosmosDB client with AAD auth and containers for Chat History
  cosmos_conversation_client = None

  AZURE_COSMOSDB_DATABASE = os.environ.get("AZURE_COSMOSDB_DATABASE")
  AZURE_COSMOSDB_ACCOUNT = os.environ.get("AZURE_COSMOSDB_ACCOUNT")
  AZURE_COSMOSDB_CONVERSATIONS_CONTAINER = os.environ.get("AZURE_COSMOSDB_CONVERSATIONS_CONTAINER")
  AZURE_COSMOSDB_ACCOUNT_KEY = os.environ.get("AZURE_COSMOSDB_ACCOUNT_KEY")

  if AZURE_COSMOSDB_DATABASE and AZURE_COSMOSDB_ACCOUNT and AZURE_COSMOSDB_CONVERSATIONS_CONTAINER:
      try :
          cosmos_endpoint = f'https://{AZURE_COSMOSDB_ACCOUNT}.documents.azure.com:443/'

          if not AZURE_COSMOSDB_ACCOUNT_KEY:
              credential = DefaultAzureCredential()
          else:
              credential = AZURE_COSMOSDB_ACCOUNT_KEY

          cosmos_conversation_client = CosmosConversationClient(
              cosmosdb_endpoint=cosmos_endpoint, 
              credential=credential, 
              database_name=AZURE_COSMOSDB_DATABASE,
              container_name=AZURE_COSMOSDB_CONVERSATIONS_CONTAINER
          )
      except Exception as e:
          logging.exception("Exception in CosmosDB initialization", e)
  return cosmos_conversation_client
