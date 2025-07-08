##TEST FOR THIS DATASOURCE ONLY
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
class ReleaseGroups(TypedDict):
    id: str
    name: str
    description: str
    archived: bool
    html: str
    
    
class ReleaseGroupsDataClient(StreamingConnectorDataClient[ReleaseGroups]):
    def __init__(self, apiURL: str, apiKey: str):
        self.apiURL = apiURL
        self.apiKey = apiKey
        
    def get_source_data(self, since = None) -> Generator[ReleaseGroups, None, None]:
        
           nextPage = None
           while  True:
                if nextPage:
                   pageURL = nextPage
                else: 
                    pageURL = f"{self.apiURL}/releases"
            
                response = requests.get(pageURL, headers = {"Authorization": f"Bearer {self.apiKey}", "X-Version":"1"})
                response.raise_for_status()
                data = response.json()
                releaseGroups = data.get("data", [])
                
                if not releaseGroups:
                    break
                
                for i in releaseGroups:
                    yield ReleaseGroups(i)
                    ##print(f"RELEASE GROUPS HERE: {i}")
                
                nextPage = data.get("links", {}).get("next")
                if not nextPage:
                    break
                

class ReleaseGroupsConnector(BaseStreamingDatasourceConnector[ReleaseGroups]):
        configuration: CustomDatasourceConfig = CustomDatasourceConfig( name = "productboard", display_name = "ProductBoard",
                                                   url_regex = r"https://.*\.productboard\.com/.*", trust_url_regex_for_view_activity = True)
        def __init__(self, name: str, data_client):
          super().__init__(name, data_client)
          self.batch_size = 80      
          
        def transform(self, data: Sequence[ReleaseGroups]) -> List[DocumentDefinition]:
             docs = []
             for i in data:
                docs.append(DocumentDefinition(
                    id = i["id"],
                    name = i["name"],
                    datasource = self.configuration.name,
                    view_url = i["links"]["self"],
                    description = i["description"],
                    archived = i["archived"],
                    permissions = DocumentPermissionsDefinition(allow_anonymous_access = True) 
                    )
                )   
             return docs  
         
             
if __name__ == "__main__":
    
 try:
    data_client = ReleaseGroupsDataClient(apiURL = "https://api.productboard.com", apiKey = os.getenv("API_TOKEN"))
    d = data_client.get_source_data()
    for i in d:
      print(f"{i}")
      break
  
    connector = ReleaseGroupsConnector(name = "productboard", data_client = data_client)
    connector.index_data(mode = IndexingMode.FULL)
  
    print("successful indexing of release groups into glean ✅")
 except:
    print("failed to index release groups ❗️")