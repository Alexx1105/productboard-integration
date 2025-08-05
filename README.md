
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
-Custom fields: `https://api.productboard.com/hierarchy-entities/custom-fields{id}`

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

***- For Maximus internal use only***
