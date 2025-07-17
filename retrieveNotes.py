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
from glean.indexing.connectors.base_streaming_data_client import StreamingConnectorDataClient
from typing import TypedDict
import os

from dotenv import load_dotenv
load_dotenv()


@dataclass
class Notes(TypedDict):
    id: str
    title: str
    content: str
    displayUrl: str
    externalDisplayUrl: str
    company: str
    
    
class NotesDataClient(StreamingConnectorDataClient[Notes]):
    def __init__(self, apiURL: str, apiKey: str):
        self.apiURL = apiURL
        self.apiKey = apiKey 
        
    def get_source_data(self, since = None) -> Generator[Notes, None, None]:
         
         nextPage = None 
         while True: 
             if nextPage:
                 pageURL = nextPage
             else: 
                 pageURL = f"{self.apiURL}/notes"
                 
             response = requests.get(pageURL, headers = {"Authorization": f"Bearer {self.apiKey}", "X-Version":"1"})
             response.raise_for_status()
             data = response.json()
             features = data.get("data", [])
             
             returned = features[0]
             id = returned["id"]
         
             appenededURL = f"{self.apiURL}/notes/{id}" 
             newResponse = requests.get(appenededURL, headers = {"Authorization": f"Bearer {self.apiKey}", "X-Version":"1"})
             newResponse.raise_for_status()
             data = response.json()
             retrievedFeatures = data.get("data", [])
   
             if not retrievedFeatures:
                 break
             
             for i in retrievedFeatures:
               yield i
            
             nextPage = data.get("links", {}).get("next") 
             if not nextPage:
                 break
             
class NotesConnector(BaseStreamingDatasourceConnector[Notes]):
    configuration: CustomDatasourceConfig = CustomDatasourceConfig( name = "productboard", display_name = "ProductBoard",
                                                   url_regex = r"https://.*\.productboard\.com/.*", trust_url_regex_for_view_activity = True)

    def __init__(self, name: str, data_client):
        super().__init__(name, data_client)
        self.batch_size = 80
        
    def transform(self, data: Sequence[Notes]) -> List[DocumentDefinition]:
        docs = []
        for i in data:
            docs.append(DocumentDefinition(
                id = i["id"],
                title = i["title"],
                datasource = self.configuration.name,
                view_url = i["displayUrl"],
                body = ContentDefinition(mime_type = "text/html", text_content = i["content"]),
                permissions = DocumentPermissionsDefinition(allow_anonymous_access = True) 
            ))
        print(f"MAPPED FOR GLEAN: {docs}")
        return docs


if __name__ == "__main__":
    
    try:
       data_client = NotesDataClient(apiURL = "https://api.productboard.com", apiKey = os.getenv("API_TOKEN"))
       data_client.get_source_data()
       
       connector = NotesConnector(name = "productboard", data_client = data_client)
       connector.index_data(mode = IndexingMode.INCREMENTAL)
     
       print("successful indexing into glean ✅")
    except Exception as error:
       print("failed to index ❌", error)