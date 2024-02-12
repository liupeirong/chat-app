import os

class AzureAISearchConfig(object):
  _instance = None
  SERVICE: str
  INDEX: str
  KEY: str
  USE_SEMANTIC_SEARCH: bool
  SEMANTIC_SEARCH_CONFIG: str
  TOP_K: int
  CONTENT_COLUMNS: str
  FILENAME_COLUMN: str
  TITLE_COLUMN: str
  URL_COLUMN: str
  VECTOR_COLUMNS: str
  QUERY_TYPE: str
  PERMITTED_GROUPS_COLUMN: str
  TOOL_NAME: str
  TOOL_DESCRIPTION: str

  def __new__(cls):
    if cls._instance is None:
      cls._instance = super(AzureAISearchConfig, cls).__new__(cls)
      cls._instance.SERVICE = os.environ.get("AZURE_SEARCH_SERVICE")
      cls._instance.INDEX = os.environ.get("AZURE_SEARCH_INDEX")
      cls._instance.KEY = os.environ.get("AZURE_SEARCH_KEY")
      cls._instance.TOOL_NAME = os.environ.get("AZURE_SEARCH_TOOL_NAME")
      cls._instance.TOOL_DESCRIPTION = os.environ.get("AZURE_SEARCH_TOOL_DESCRIPTION")
      cls._instance.USE_SEMANTIC_SEARCH = True if os.environ.get("AZURE_SEARCH_USE_SEMANTIC_SEARCH", "true").lower() == "true" else False
      cls._instance.SEMANTIC_SEARCH_CONFIG = os.environ.get("AZURE_SEARCH_SEMANTIC_SEARCH_CONFIG", "default")
      cls._instance.TOP_K = os.environ.get("AZURE_SEARCH_TOP_K", 3)
      cls._instance.CONTENT_COLUMNS = os.environ.get("AZURE_SEARCH_CONTENT_COLUMNS", "content")
      cls._instance.FILENAME_COLUMN = os.environ.get("AZURE_SEARCH_FILENAME_COLUMN", "filename")
      cls._instance.TITLE_COLUMN = os.environ.get("AZURE_SEARCH_TITLE_COLUMN", "title")
      cls._instance.URL_COLUMN = os.environ.get("AZURE_SEARCH_URL_COLUMN", "url")
      cls._instance.VECTOR_COLUMNS = os.environ.get("AZURE_SEARCH_VECTOR_COLUMNS", "contentVector")
      cls._instance.PERMITTED_GROUPS_COLUMN = os.environ.get("AZURE_SEARCH_PERMITTED_GROUPS_COLUMN", None)
    return cls._instance
  

class AzureOpenAPIConfig(object):
  _instance = None
  API_VERSION: str
  KEY: str
  DEPLOYMENT: str
  EMBEDDING_DEPLOYMENT: str
  TEMPERATURE: int
  TOP_P: float
  MAX_TOKENS: int
  STREAM: bool
  SYSTEM_MESSAGE: str

  def __new__(cls):
    if cls._instance is None:
      cls._instance = super(AzureOpenAPIConfig, cls).__new__(cls)
      cls._instance.API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION")
      cls._instance.DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT")
      cls._instance.EMBEDDING_DEPLOYMENT = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
      cls._instance.TEMPERATURE = os.environ.get("AZURE_OPENAI_TEMPERATURE", 0)
      cls._instance.TOP_P = os.environ.get("AZURE_OPENAI_TOP_P", 1.0)
      cls._instance.MAX_TOKENS = os.environ.get("AZURE_OPENAI_MAX_TOKENS", 1000)
      cls._instance.STREAM = True if os.environ.get("AZURE_OPENAI_STREAM", "true").lower() == "true" else False
      cls._instance.SYSTEM_MESSAGE = os.environ.get("AZURE_OPENAI_SYSTEM_MESSAGE")
    return cls._instance