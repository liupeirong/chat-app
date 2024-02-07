import os

# ACS Integration Settings
AZURE_SEARCH_SERVICE = os.environ.get("AZURE_SEARCH_SERVICE")
AZURE_SEARCH_INDEX = os.environ.get("AZURE_SEARCH_INDEX")
AZURE_SEARCH_KEY = os.environ.get("AZURE_SEARCH_KEY")
AZURE_SEARCH_USE_SEMANTIC_SEARCH = os.environ.get("AZURE_SEARCH_USE_SEMANTIC_SEARCH", "false")
AZURE_SEARCH_SEMANTIC_SEARCH_CONFIG = os.environ.get("AZURE_SEARCH_SEMANTIC_SEARCH_CONFIG", "default")
AZURE_SEARCH_TOP_K = os.environ.get("AZURE_SEARCH_TOP_K")
AZURE_SEARCH_ENABLE_IN_DOMAIN = os.environ.get("AZURE_SEARCH_ENABLE_IN_DOMAIN")
AZURE_SEARCH_CONTENT_COLUMNS = os.environ.get("AZURE_SEARCH_CONTENT_COLUMNS")
AZURE_SEARCH_FILENAME_COLUMN = os.environ.get("AZURE_SEARCH_FILENAME_COLUMN")
AZURE_SEARCH_TITLE_COLUMN = os.environ.get("AZURE_SEARCH_TITLE_COLUMN")
AZURE_SEARCH_URL_COLUMN = os.environ.get("AZURE_SEARCH_URL_COLUMN")
AZURE_SEARCH_VECTOR_COLUMNS = os.environ.get("AZURE_SEARCH_VECTOR_COLUMNS")
AZURE_SEARCH_QUERY_TYPE = os.environ.get("AZURE_SEARCH_QUERY_TYPE")
AZURE_SEARCH_STRICTNESS = os.environ.get("AZURE_SEARCH_STRICTNESS")
AZURE_SEARCH_PERMITTED_GROUPS_COLUMN = os.environ.get("AZURE_SEARCH_PERMITTED_GROUPS_COLUMN")

###
### TODO: Convert  search API call to SDK
###

  #       # Set query type
  #       query_type = "simple"
  #       if AZURE_SEARCH_QUERY_TYPE:
  #           query_type = AZURE_SEARCH_QUERY_TYPE
  #       elif AZURE_SEARCH_USE_SEMANTIC_SEARCH.lower() == "true" and AZURE_SEARCH_SEMANTIC_SEARCH_CONFIG:
  #           query_type = "semantic"

  #       # Set filter
  #       filter = None
  #       userToken = None
  #       if AZURE_SEARCH_PERMITTED_GROUPS_COLUMN:
  #           userToken = request.headers.get('X-MS-TOKEN-AAD-ACCESS-TOKEN', "")
  #           logging.debug(f"USER TOKEN is {'present' if userToken else 'not present'}")

  #           filter = generateFilterString(AZURE_SEARCH_PERMITTED_GROUPS_COLUMN, userToken)
  #           logging.debug(f"FILTER: {filter}")

  #       body["dataSources"].append(
  #           {
  #               "type": "AzureCognitiveSearch",
  #               "parameters": {
  #                   "endpoint": f"https://{AZURE_SEARCH_SERVICE}.search.windows.net",
  #                   "key": AZURE_SEARCH_KEY,
  #                   "indexName": AZURE_SEARCH_INDEX,
  #                   "fieldsMapping": {
  #                       "contentFields": parse_multi_columns(AZURE_SEARCH_CONTENT_COLUMNS) if AZURE_SEARCH_CONTENT_COLUMNS else [],
  #                       "titleField": AZURE_SEARCH_TITLE_COLUMN if AZURE_SEARCH_TITLE_COLUMN else None,
  #                       "urlField": AZURE_SEARCH_URL_COLUMN if AZURE_SEARCH_URL_COLUMN else None,
  #                       "filepathField": AZURE_SEARCH_FILENAME_COLUMN if AZURE_SEARCH_FILENAME_COLUMN else None,
  #                       "vectorFields": parse_multi_columns(AZURE_SEARCH_VECTOR_COLUMNS) if AZURE_SEARCH_VECTOR_COLUMNS else []
  #                   },
  #                   "inScope": True if AZURE_SEARCH_ENABLE_IN_DOMAIN.lower() == "true" else False,
  #                   "topNDocuments": AZURE_SEARCH_TOP_K,
  #                   "queryType": query_type,
  #                   "semanticConfiguration": AZURE_SEARCH_SEMANTIC_SEARCH_CONFIG if AZURE_SEARCH_SEMANTIC_SEARCH_CONFIG else "",
  #                   "roleInformation": AZURE_OPENAI_SYSTEM_MESSAGE,
  #                   "filter": filter,
  #                   "strictness": int(AZURE_SEARCH_STRICTNESS)
  #               }
  #           })
  #   else:
  #       raise Exception(f"DATASOURCE_TYPE is not configured or unknown: {DATASOURCE_TYPE}")

  #   if "vector" in query_type.lower():
  #       body["dataSources"][0]["parameters"]["embeddingDeploymentName"] = AZURE_OPENAI_EMBEDDING_DEPLOYMENT

  #   headers = {
  #       'Content-Type': 'application/json',
  #       'api-key': AZURE_OPENAI_KEY,
  #       "x-ms-useragent": "GitHubSampleWebApp/PublicAPI/3.0.0"
  #   }

  #   return body, headers

  # aoai = AzureOpenAI(
  #   api_version=llmConfig.embedding['api_version']
  # )
  # aoaiDeployment = llmConfig.embedding['deployment']
  # indexName = llmConfig.search['index_name']
  # searchClient = AAISearch().get_search_client(indexName)

  # queryEmbedding = aoai.embeddings.create(input=[query], model=aoaiDeployment).data[0].embedding
  # vectorQuery = VectorizedQuery(vector=queryEmbedding, k_nearest_neighbors=3, fields="contentVector")
  # results = searchClient.search(
  #   search_text=query,
  #   vector_queries=[vectorQuery],
  #   query_type=QueryType.SEMANTIC,
  #   semantic_configuration_name="default",
  #   query_caption=QueryCaptionType.EXTRACTIVE,
  #   query_answer=QueryAnswerType.EXTRACTIVE,
  #   top=3,
  #   filter=f"kind eq '{kind}'" if kind else None
  # )

  # docs = [{'title': result['title'], 'content': result['content']} for result in results]
  # return json.dumps(docs)