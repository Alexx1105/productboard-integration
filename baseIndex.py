from itertools import product
from glean.indexing.models import IndexingMode
from dataclasses import dataclass
from typing import List, Sequence
from glean.indexing.connectors import BaseStreamingDatasourceConnector
from glean.indexing.models import ContentDefinition, CustomDatasourceConfig, DocumentDefinition
from glean.api_client.models.documentpermissionsdefinition import DocumentPermissionsDefinition
from glean.api_client.models.userreferencedefinition import UserReferenceDefinition
from typing import Generator
from datetime import datetime
import requests
import typing
from typing import Union, Dict, Type
from glean.indexing.connectors.base_streaming_data_client import StreamingConnectorDataClient
from typing import TypedDict
import os

from dotenv import load_dotenv
load_dotenv()


@dataclass
class AllProducts(TypedDict):
    id: str
    name: str
    description: str
    owner: str
    email: str
    html: str

@dataclass
class ReleaseGroups(TypedDict):
    id: str
    name: str
    description: str
    archived: bool
    html: str
    releaseGroup: str
    
@dataclass
class Features(TypedDict):
     id: str
     name: str
     description: str
     type: str
     archived: bool
     status: str
     
@dataclass
class Notes(TypedDict):
    id: str
    title: str
    content: str
    displayUrl: str
    externalDisplayUrl: str
    company: str
    
baseTypes = Union[AllProducts, ReleaseGroups, Features, Notes]
mapEndpoints: Dict[str, Type[baseTypes]] = {
    "products" : AllProducts,
    "releases" : ReleaseGroups,
    "features" : Features,
    "notes" : Notes  
}

class BaseDataClient(StreamingConnectorDataClient[baseTypes]):
    def __init__(self, apiURL: str, apiKey: str):
        self.apiURL = apiURL
        self.apiKey = apiKey
        
    def get_source_data(self, since = None) -> Generator[baseTypes, None, None]:
        
     for i in mapEndpoints:
        nextPage = None
        while True:
         pageURL = nextPage if nextPage else f"{self.apiURL}/{i}" 
            
         response = requests.get(pageURL, headers = {"Authorization": f"Bearer {self.apiKey}", "X-Version":"1"})
         response.raise_for_status()
         data = response.json()
         products = data.get("data", [])
         print(f"PRODUCTS HERE {products}")

         if not products:
            break
       
         for i in data:
              yield i
         nextPage = data.get("links", {}).get("next")
              
         if not nextPage:
            break
    

if __name__ == "__main__":
     ##try: 
       data_client = BaseDataClient(apiURL = "https://api.productboard.com", apiKey = os.getenv("API_TOKEN"))
       for i in data_client.get_source_data():
         print(i)
     
         
       ##print("success ✅")
     ##except:
       ##print("failure ❗️")
    