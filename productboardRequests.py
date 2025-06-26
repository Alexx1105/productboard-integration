import requests 
from requests import RequestException
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import httpx
from dotenv import load_dotenv
load_dotenv()


@dataclass
class ProductboardData:
    id: str
    name: str
    description: str
    owner: str
    email: str
    

@staticmethod
def productboardReq() -> ProductboardData:
  token = os.getenv("API_TOKEN")
 
  try:
     requestHeaders = { "accept" : "application/json", "X-Version": "1", "authorization" : f"Bearer {token}"}
     response = requests.get("https://api.productboard.com/products", headers = requestHeaders)
     products = response.json()  
     jsonResponse = products.get("data", [])     
                             
     first = jsonResponse[0]
     product_id = first["id"]
    
     endpointAppended = f"https://api.productboard.com/products/{product_id}"
     resp = requests.get(endpointAppended, headers = requestHeaders)
    
     dicts = resp.json().get("data", resp.json())         ## pull out top level JSON object 
     return(ProductboardData(
          id = dicts.get("id"),
          name = dicts.get("name"),
          description = dicts.get("description"),
          owner = dicts.get("owner"),
          email = dicts.get("email")
     ))
    
  except TypeError as typeError:
     print("request to productboard failed ❌", typeError)    
  except ImportError as importError:
    print("page data could not be retrieved", importError)
  except RequestException as requestError:
    print("bad request", requestError)
    
    
if __name__ == "__main__":
   print(productboardReq())
   
   
      