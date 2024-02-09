from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import VectorizedQuery
from openai import AzureOpenAI

from utils.config import AzureAISearchConfig, AzureOpenAPIConfig


def ai_search(query: str, user_groups: list(str)) -> list:
  search_config = AzureAISearchConfig()
  credential = AzureKeyCredential(search_config.KEY)
  search_index_client = SearchIndexClient(endpoint=search_config.SERVICE, credential=credential)
  search_client = search_index_client.get_search_client(search_config.INDEX)

  aoai_config = AzureOpenAPIConfig()
  aoai = AzureOpenAI(api_version=aoai_config.API_VERSION)

  # If the user is not a member of any groups, search is not allowed 
  if search_config.PERMITTED_GROUPS_COLUMN and (user_groups is None or len(user_groups) == 0):
    return []

  group_ids = ", ".join([g['id'] for g in user_groups]) if user_groups else None
  query_embedding = aoai.embeddings.create(input=[query], model=aoai_config.EMBEDDING_DEPLOYMENT).data[0].embedding
  vector_query = VectorizedQuery(vector=query_embedding, k_nearest_neighbors=search_config.TOP_K, fields=search_config.VECTOR_COLUMNS)
  results = search_client.search(
    search_text=query,
    vector_queries=[vector_query],
    query_type=search_config.QUERY_TYPE,
    semantic_configuration_name=search_config.SEMANTIC_SEARCH_CONFIG,
    top=search_config.TOP_K,
    filter= f"{search_config.PERMITTED_GROUPS_COLUMN}/any(g:search.in(g, '{group_ids}'))" if search_config.PERMITTED_GROUPS_COLUMN else None
  )

  return results
