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
    createdAt: str
    updatedAt: str

@dataclass
class ReleaseGroups(TypedDict):
    id: str
    name: str
    description: str
    archived: bool
    html: str
    releaseGroup: str
    createdAt: str
    updatedAt: str
    
@dataclass
class Features(TypedDict):
     id: str
     name: str
     description: str
     type: str
     archived: bool
     status: str
     createdAt: str
     updatedAt: str
     
@dataclass
class Notes(TypedDict):
    id: str
    title: str
    content: str
    displayUrl: str
    externalDisplayUrl: str
    company: str
    createdAt: str
    updatedAt: str
    
baseTypes = Union[AllProducts, ReleaseGroups, Features, Notes]
mapEndpoints: Dict[str, Type[baseTypes]] = {
    "products" : AllProducts,
    "releases" : ReleaseGroups,
    "features" : Features,
    "notes" : Notes,  
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
         allItems = data.get("data", [])
         
         returned = allItems[0]
         id = returned["id"]
         
         appenededURL = f"{self.apiURL}/{i}/{id}" 
         newResponse = requests.get(appenededURL, headers = {"Authorization": f"Bearer {self.apiKey}", "X-Version":"1"})
         newResponse.raise_for_status()
         data = newResponse.json()
         retrievedFeatures = data.get("data", [])
         print(f"ALL DATA TYPES: {retrievedFeatures}")
         
         if not allItems:
            break
       
         for i in allItems:
              yield i
        
         nextPage = data.get("links", {}).get("next")
              
         if not nextPage:
            break
    
    
class BaseConnector(BaseStreamingDatasourceConnector[baseTypes]):
    configuration: CustomDatasourceConfig = CustomDatasourceConfig( name = "productboard", display_name = "ProductBoard",
                                                   url_regex = r"https://.*\.productboard\.com/.*", trust_url_regex_for_view_activity = True)

    def __init__(self, name: str, data_client):
        super().__init__(name, data_client)
        self.batch_size = 80
        
    def transform(self, data: Sequence[baseTypes]) -> List[DocumentDefinition]:
         docs = []
         for i in data:
            ownerName = i.get("owner", {}).get("email")
            if not ownerName:
                continue
            
            contentType = i.get("description") or i.get("content")
            if not contentType:
                continue
                
            docs.append(DocumentDefinition(
                id = i["id"],
                title = i.get("name") or i.get("title"),
                datasource = self.configuration.name,
                view_url = i.get("links", {}).get("html") or i.get("releaseGroup", {}).get("links", {}).get("self") or i.get("links", {}).get("self") or i.get("displayUrl"),
                body = ContentDefinition(mime_type = "text/html", text_content = contentType),
                owner = UserReferenceDefinition(email = ownerName),
                created_at = self._parse_timestamp(i.get("createdAt")),
                updated_at = self._parse_timestamp(i.get("updatedAt")),
                permissions = DocumentPermissionsDefinition(allow_anonymous_access = True),   ## change to false in production
                )) 
         return docs
      
    def _parse_timestamp(self, timestamp: str) -> int: 
        if not timestamp:
         return None
        dateAndTime = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))      
        return int(dateAndTime.timestamp())
       
         

     
def runConnectorFull():    
    try: 
      data_client = BaseDataClient(apiURL = "https://api.productboard.com", apiKey = os.getenv("API_TOKEN"))
      data_client.get_source_data()
         
      connector = BaseConnector(name = "productboard", data_client = data_client)
      connector.index_data(IndexingMode.FULL, force_restart = False)   ##flip to true when needed
    
      print("successful indexing into glean ✅")
    except Exception as error:
      print("failed to index ❌", error)
                                              ##TO-DO: set up seperate crons for these 
  
def runConnectorIncremental():
    try: 
      data_client = BaseDataClient(apiURL = "https://api.productboard.com", apiKey = os.getenv("API_TOKEN"))
      data_client.get_source_data()
         
      connector = BaseConnector(name = "productboard", data_client = data_client)
      connector.index_data(IndexingMode.INCREMENTAL, force_restart = False)   
      
      print("successful indexing into glean ✅")
    except Exception as error:
      print("failed to index ❌", error)
      
  
      