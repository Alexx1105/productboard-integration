
  ![CleanShot 2025-07-01 at 11 21 03](https://github.com/user-attachments/assets/c8b64c12-b072-4192-b8a5-eb7e04da10d6)

  # Productboard | glean indexing #
  
  ### Summary flow - current iteration as of (7/1/25) ###

  This glean indexing logic has been refactored to conform to gleans latest SDK release found in https://pypi.org/project/glean-indexing-sdk/
  the request and indexing logic are bundled into one file.
  ___
  ### (1) Initializing Productboard as client ###
  (after creating the productboard dataclass `ProductboardData`)
  
  The subclass `ProductboardDataClient` inits instances of the productboard api key and endpoint url, it takes the method `StreamingConnectorDataClient` with a list of `ProductboardData` elements declared in the dataclass.
  ___
  ### (2) Retrieving productboard data ###
  Returns list of productboard data via the `Generator` method, `get_source_data()` will check for the next page to load in after iterating through the products after a successful get request has been completed.
  ___
  ### (3) Building the productboard connector ###
  Another subclass `ProductboardConnector` which created the connector to glean using `BaseStreamingDatasourceConnector` configs productboard as a datasource with `CustomDatasourceConfig` method, inits the display name, and sets a cap to 80 for the batch size of pages to index.
  ___
   ### (4) mapping dicts into a list, setting timestamps ###
   `ProductboardData` is iterated upon to append to `DocumentDefinition` with the dicts mapped to the JSON structure glean expects, user permissions are also set within this list.
    A timestamp is also generated via `getTimestamp()` to assign a `created_at` & `updated_at` value to be used later to update time-sensitive data in glean, and for incremental updates.
  ___
   ### (5) Main() func invokations ###
   Request + indexing functionality pulled together by calling `ProductboardDataClient` and instantiating it which contains the hardcoded productboard endpoint, and the `apiKey` fetched from .env,
   and subsequently calling `ProductboardConnector` before instantiating and indexing it via `index_data`, which takes an argument to fully index all pages.
***
### Whats currently indexed from productboard ###
- Release Groups: `https://api.productboard.com/releases/{id}`
- Products: `https://api.productboard.com/products/{id}`
- features: `https://api.productboard.com/features/{id}`
- Notes: `https://api.productboard.com/notes/{id}`
- Custom fields: `https://api.productboard.com/hierarchy-entities/custom-fields{id}`

***
### Main retrieval + indexing logic ###
All the productboard endpoints are consolidated in `baseIndexing.py` to handle the endpoint calls and indexing in one place, previously each endpoint was called and indexed in its own file for the sake of testing.
***
***Changes for Aug 1st 2025***

- Indexing functions inside of `baseIndexing.py` are called from `index.py` which is the entry point for docker.

- Connector is dockerized so it can be hosted in an EC2 instacne and other features like cron functionality for full and incremental indexing can be added.

To dockerize connector, first have docker desktop running, then build the image with `docker build -t glean-productboard-integration:latest .`

Then run with: `docker run --env-file .env -p 8000:8000 --name glean_prodboard_latest glean-productboard-integration:latest`

***⚠️ Note: you must change `index.py` specified port number for production, currently configured to localhost 8000 for testing***
***

<img width="2536" height="1736" alt="CleanShot 2025-08-05 at 14 23 02@2x" src="https://github.com/user-attachments/assets/56e21860-4547-4a79-8bf3-42dfabbbdde2" />
 
 ### High level project flow ###
 
The screenshot above shows what the respective .py files and directories do and what are the main entry points for the indexing and retrieval logic, this does not incorporate the cron schedulers or EC2 as those will still need to be created. 

❗️ It's worth noting the existence of the`envInjection.py` file, this file is currently as WIP as AWS access is still needed.
When access is granted to an EC2 instance where the docker container and the cron schedulers will be hosted, you can use `envInjection.py` to inject, create, or update .env values into AWS secrets manager at runtime for authentication.
___
 ### Generating env credentials ###
 (1) In your project's directory, run `touch .env` to later add glean & productboard credentials

 (2) In the new .env file, create three variables: `API_TOKEN` , `GLEAN_INDEXING_API_TOKEN` and `GLEAN_INSTANCE` | API_TOKEN is where the productboard token will go, GLEAN_INDEXING_API_TOKEN is for your glean indexing token, and GLEAN_INSTANCE will be the maximus instance from the glean URL

 (3) Generate the credentials from the glean and productboard admin dashboard and add them to the associated env variables like so API_TOKEN=<ADD_TOKEN_HERE> | GLEAN_INDEXING_API_TOKEN=<ADD_GLEAN_TOKEN_HERE> | GLEAN_INSTANCE=maximus

 (4) In the CLI, run `export GLEAN_INSTANCE=maximus` in the project's directory 

  ### For glean ###
<img width="1988" height="485" alt="CleanShot 2025-08-06 at 12 08 53" src="https://github.com/user-attachments/assets/87fcadc3-4fcd-4a73-9c46-415f9d77c403" />

***Hit the tool icon at the bottom left, hit "Platform", then access "API Tokens" to generate your glean indexing token under the "Indexing API Tokens" tab***

 ### For Productboard ###
<img width="772" height="197" alt="CleanShot 2025-08-06 at 12 21 20" src="https://github.com/user-attachments/assets/7cb76912-27f4-4bfc-905c-301d07e4448e" />

Your env file should look like this:
```
API_TOKEN=<PRODUCTBOARD_TOKEN_HERE>
GLEAN_INDEXING_API_TOKEN=<GLEAN_INDEXING_TOKEN_HERE>
GLEAN_INSTANCE=maximus
```

___

***- For Maximus internal use only***
