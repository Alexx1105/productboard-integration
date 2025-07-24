
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
class AllProducts(TypedDict):
    id: str
    name: str
    description: str
    owner: str
    email: str
    html: str


class ProductsDataClient(StreamingConnectorDataClient[AllProducts]):
    def __init__(self, apiURL: str, apiKey: str):
        self.apiURL = apiURL
        self.apiKey = apiKey
        
    
    def get_source_data(self, since = None) -> Generator[AllProducts, None, None]:
      
        nextPage = None
        while True:
            if nextPage:
                pageURL = nextPage
            else: 
                pageURL = f"{self.apiURL}/products"
                
            response = requests.get(pageURL, headers = {"Authorization": f"Bearer {self.apiKey}", "X-Version":"1"})
            response.raise_for_status()
            
            data = response.json()
            products = data.get("data", [])
            
            if not products:
                break
            
            for i in products:
                yield AllProducts(i)
                print(f"PRODUCTS HERE: {i}")
            nextPage = data.get("links", {}).get("next") 
            if not nextPage:
                break
            
             
class ProductboardConnector(BaseStreamingDatasourceConnector[AllProducts]):
      configuration: CustomDatasourceConfig = CustomDatasourceConfig( name = "productboard", display_name = "ProductBoard",
                                                   url_regex = r"https://.*\.productboard\.com/.*", trust_url_regex_for_view_activity = True)
      def __init__(self, name: str, data_client):
          super().__init__(name, data_client)
          self.batch_size = 80
          
      def transform(self, data: Sequence[AllProducts]) -> List[DocumentDefinition]:
             docs = []
             for i in data:
                 docs.append(
                     DocumentDefinition(
                         id = i["id"],
                         title = i["name"],
                         datasource = self.configuration.name,  ##from CustomDataSource config method
                         view_url = i["links"]["html"],
                         body = ContentDefinition(mime_type = "text/html", text_content = i["description"]),
                         owner = UserReferenceDefinition(email = i["owner"]["email"]),
                         created_at = self.getTimestamp(i["createdAt"]),
                         updated_at = self.getTimestamp(i["updatedAt"]),
                         permissions = DocumentPermissionsDefinition(allow_anonymous_access = True)  ##TO-DO: change later?                       
          
                         )
                     )
             return docs
        
      def getTimestamp(self, time_stamp: str) -> int:
          dateAndTime = datetime.fromisoformat(time_stamp.replace("Z", "+00:00"))
          return int(dateAndTime.timestamp())
      

def main():
  try:
    data_client = ProductsDataClient(apiURL = "https://api.productboard.com", apiKey = os.getenv("API_TOKEN"))
    connector = ProductboardConnector(name = "productboard", data_client = data_client)
    connector.index_data(mode = IndexingMode.INCREMENTAL)   ##TO-DO: toggle to incremental later?

    print("successful indexing of products into glean ✅")
  except: 
    print("failed to index ❗️")
    
    
if __name__ == "__main__":
    main()