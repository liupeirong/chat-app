# Sample Chat App with AOAI

This repo contains sample code for a simple chat webapp that integrates with Azure OpenAI.

## Prerequisites

- An existing Azure OpenAI resource and model deployment of a chat model (e.g. `gpt-35-turbo-16k`, `gpt-4`)
- To use Azure OpenAI on your data: an existing Azure AI Search resource and index.

## Run the app

### Basic Chat Experience

1. Update the environment variables listed in `app.py` as described in the [Environment variables](#environment-variables) section.

    | App Setting | Value | Note |
    | --- | --- | ------------- |
    |AZURE_OPENAI_DEPLOYMENT||The name of your model deployment|
    |AZURE_OPENAI_ENDPOINT||The endpoint of your Azure OpenAI resource.|
    |AZURE_OPENAI_KEY||One of the API keys of your Azure OpenAI resource|
    |AZURE_OPENAI_TEMPERATURE|0|What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. A value of 0 is recommended when using your data.|
    |AZURE_OPENAI_TOP_P|1.0|An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. We recommend setting this to 1.0 when using your data.|
    |AZURE_OPENAI_MAX_TOKENS|1000|The maximum number of tokens allowed for the generated answer.|
    |AZURE_OPENAI_SYSTEM_MESSAGE|You are an AI assistant that helps people find information.|A brief description of the role and tone the model should use|
    |AZURE_OPENAI_API_VERSION|2023-12-01-preview|API version when using Azure OpenAI on your data|
    |AZURE_OPENAI_STREAM|True|Whether or not to use streaming for the response|
    |AZURE_OPENAI_EMBEDDING_DEPLOYMENT||The name of your embedding model deployment if using vector search.|

2. Start the app with `start.cmd`. This will build the frontend, install backend dependencies, and then start the app.
3. You can see the local running app at http://127.0.0.1:5000.

### Chat with data in Azure AI Search

1. Update the `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` environment variable to point to your embedding model.
2. To connect to your data, you need to specify an Azure AI Search index to use. You can [create this index yourself](https://learn.microsoft.com/en-us/azure/search/search-get-started-portal) or use the [Azure AI Studio](https://oai.azure.com/portal/chat) to create the index for you.

    | App Setting | Value | Note |
    | --- | --- | ------------- |
    |AZURE_SEARCH_SERVICE||The name of your Azure Cognitive Search resource|
    |AZURE_SEARCH_INDEX||The name of your Azure Cognitive Search Index|
    |AZURE_SEARCH_KEY||An **admin key** for your Azure Cognitive Search resource|
    |AZURE_SEARCH_USE_SEMANTIC_SEARCH|False|Whether or not to use semantic search|
    |AZURE_SEARCH_QUERY_TYPE|simple|Query type: simple, semantic, vector, vectorSimpleHybrid, or vectorSemanticHybrid. Takes precedence over AZURE_SEARCH_USE_SEMANTIC_SEARCH|
    |AZURE_SEARCH_SEMANTIC_SEARCH_CONFIG||The name of the semantic search configuration to use if using semantic search.|
    |AZURE_SEARCH_TOP_K|5|The number of documents to retrieve from Azure Cognitive Search.|
    |AZURE_SEARCH_ENABLE_IN_DOMAIN|True|Limits responses to only queries relating to your data.|
    |AZURE_SEARCH_CONTENT_COLUMNS||List of fields in your Azure Cognitive Search index that contains the text content of your documents to use when formulating a bot response. Represent these as a string joined with "|", e.g. `"product_description|product_manual"`|
    |AZURE_SEARCH_FILENAME_COLUMN|| Field from your Azure Cognitive Search index that gives a unique idenitfier of the source of your data to display in the UI.|
    |AZURE_SEARCH_TITLE_COLUMN||Field from your Azure Cognitive Search index that gives a relevant title or header for your data content to display in the UI.|
    |AZURE_SEARCH_URL_COLUMN||Field from your Azure Cognitive Search index that contains a URL for the document, e.g. an Azure Blob Storage URI. This value is not currently used.|
    |AZURE_SEARCH_VECTOR_COLUMNS||List of fields in your Azure Cognitive Search index that contain vector embeddings of your documents to use when formulating a bot response. Represent these as a string joined with "|", e.g. `"product_description|product_manual"`|
    |AZURE_SEARCH_PERMITTED_GROUPS_COLUMN||Field from your Azure Cognitive Search index that contains AAD group IDs that determine document-level access control.|
    |AZURE_SEARCH_STRICTNESS|3|Integer from 1 to 5 specifying the strictness for the model limiting responses to your data.|

3. Start the app with `start.cmd`. This will build the frontend, install backend dependencies, and then start the app.
4. You can see the local running app at http://127.0.0.1:5000.

### Enable Chat History

To enable chat history, you will need to set up CosmosDB resources.

1. If you provision CosmosDB container without using the provided ARM template, make sure the partition key is `/userId`.
2. Specify these additional environment variables:

    - `AZURE_COSMOSDB_ACCOUNT`
    - `AZURE_COSMOSDB_DATABASE`
    - `AZURE_COSMOSDB_CONVERSATIONS_CONTAINER`
    - `AZURE_COSMOSDB_ACCOUNT_KEY`

3. Start the app with `start.cmd`, then visit the local running app at http://127.0.0.1:5000.

### Add an identity provider

If you run this app on a fully qualified domain or IP other than localhost, you will need to add an identity provider to
 provide authentication support in your app. See [this tutorial](https://learn.microsoft.com/en-us/azure/app-service/scenario-secure-app-authentication-app-service) for more information.

If you don't add an identity provider, the chat functionality of your app will be blocked to prevent unauthorized access to your resources and data.

To remove this restriction, you can add `AUTH_ENABLED=False` to the environment variables. This will disable authentication and allow anyone to access the chat functionality of your app. **This is not recommended for production apps.**

To add further access controls, update the logic in `getUserInfoList` in `frontend/src/pages/chat/Chat.tsx`.

### Updating the default chat logo and headers

The landing chat page logo and headers are specified in `frontend/src/pages/chat/Chat.tsx`:

```html
<Stack className={styles.chatEmptyState}>
    <img
        src={Azure}
        className={styles.chatIcon}
        aria-hidden="true"
    />
    <h1 className={styles.chatEmptyStateTitle}>Start chatting</h1>
    <h2 className={styles.chatEmptyStateSubtitle}>This chatbot is configured to answer your questions</h2>
</Stack>
```

To update the logo, change `src={Azure}` to point to your own SVG file, which you can put in `frontend/src/assets`/
To update the headers, change the strings "Start chatting" and "This chatbot is configured to answer your questions" to your desired values.

### Changing Citation Display

The Citation panel is defined at the end of `frontend/src/pages/chat/Chat.tsx`. The citations returned from Azure OpenAI On Your Data will include `content`, `title`, `filepath`, and in some cases `url`. You can customize the Citation section to use and display these as you like. For example, the title element is a clickable hyperlink if `url` is not a blob URL.

```js
    <h5 
        className={styles.citationPanelTitle} 
        tabIndex={0} 
        title={activeCitation.url && !activeCitation.url.includes("blob.core") ? activeCitation.url : activeCitation.title ?? ""} 
        onClick={() => onViewSource(activeCitation)}
    >{activeCitation.title}</h5>

    const onViewSource = (citation: Citation) => {
        if (citation.url && !citation.url.includes("blob.core")) {
            window.open(citation.url, "_blank");
        }
    };

```
