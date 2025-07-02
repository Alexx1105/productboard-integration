
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
***- For Maximus internal use only***
