
import os
from dotenv import load_dotenv

from glean.api_client import Glean, models as client_models
from glean.api_client.models import (
    CustomDatasourceConfig,
    DatasourceCategory,
    DocumentDefinition,
    DocumentPermissionsDefinition,
    ContentDefinition,
    UserReferenceDefinition,
)
import os
from dotenv import load_dotenv
from typing import TypedDict
from productboardRequests import productboardReq
from productboardRequests import ProductboardData
import requests

##from permissions import permissions
load_dotenv()

class IndexData:
    
    @staticmethod
    def productboardConfig():
        
        try:
          datasourceConfig = CustomDatasourceConfig( name = "productboard", display_name = "Productboard", datasource_category = DatasourceCategory.KNOWLEDGE_HUB,
                                                        url_regex = r"^https://api\.productboard\.com/products/[0-9A-Fa-f\-]+$", indexing_mode = client_models.IndexingMode.BULK,)
          print("datasource config success ✅")
        except:
          print("datasource manual config is failing ❗️")
          
        try:   
          with Glean(api_token = os.getenv("GLEAN_API_TOKEN"), instance = os.getenv("GLEAN_INSTANCE")) as client:
            client.indexing.datasources.add(request = datasourceConfig)
          
          print("successful initialization of productboard datasource ✅") 
        except:
          print("failed to config datasource ❌")
      
          
    @staticmethod
    def productboardBulkIndex(items: list[ProductboardData]) -> list[DocumentDefinition]:
             ##TO-DO: add booleans for first and last page
        try:
          docs: list[DocumentDefinition] = []
          
          for item in items: 
              docs.append(DocumentDefinition(
              id = item.id,
              datasource = "productboard",
              
              view_url = item.link,
              title = item.name,
              body = ContentDefinition(mime_type = "text/html", text_content = item.description), 
              author = UserReferenceDefinition(email=item.email),
              permissions = client_models.DocumentPermissionsDefinition(
                    allow_anonymous_access=True)))
              
              
          with Glean(api_token = os.getenv("GLEAN_API_TOKEN"), instance = os.getenv("GLEAN_INSTANCE")) as client:
           client.indexing.documents.index( datasource = "productboard", documents = docs)
          return docs
      
          print("productboard data successfully bulk-indexed ✅")
        except TypeError as error: 
          print("data could not be indexed into glean ❌", error)
        exit(1)
          
          
if __name__ == "__main__":
   
   IndexData.productboardConfig()               # register first
   items = productboardReq()                  # fetch your data
   IndexData.productboardBulkIndex(items)  
    