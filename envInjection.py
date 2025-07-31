## Inject .env variables into EC2 instance at runtime 
import boto3
from botocore.exceptions import ClientError
import os
import re
from dotenv import load_dotenv


varIgnore = [] ##populate later
newVarIgnore = [] ## dynamic list 

def getENV(file_path):
    envVars = {}
    
    with open(file_path, "r") as file:
        for i in file:
            line = i.strip()
            
            if not i or i.startswith("#"):   ##continue if theres whitespace
              continue
          
            replaceLine = re.sub(r"\s+#.*$", "", i)
            if "=" in file:                    ##split key-value pair env lines
                key, value = i.split("=", 1)
                key = key.strip()
                
            if key not in varIgnore:
                envVars[key] = value.strip()
            else:
                newVarIgnore.append(key)
    return envVars
          
        
def createUpdateSectrets(client, gleanID, secretValue, region): 
          try:
            response = client.create_secret(
                Name=gleanID,
                SecretString=secretValue,
            )
            print(f"Created secret: {gleanID}")
          except client.exceptions.ResourceExistsException:
            # Secret already exists, update it
            response = client.update_secret(
                SecretId = gleanID,
                SecretString = secretValue,
            )
            print(f"Updated secret: {gleanID}")
          except Exception as error:
           print(f"Error creating/updating secret {gleanID}: {error}")
        
          
def sendENV(): 
   
  load_dotenv() 
  envPath = ".env"        
  awsRegion = os.getenv("")            ##neeed aws credentials and EC2 access
  gleanDatasourceID= os.getenv("")

  try: 
    initAWSClient = boto3.Session(region_name = awsRegion)
    sendToClient = initAWSClient.client("secretsmanager")
    parseEnv = getENV(envPath)
    
    for key, value in parseEnv.items():
     gleanID = f"glean datasource id {gleanDatasourceID}_{key}"
     createUpdateSectrets(sendToClient, gleanID, value, awsRegion)
    
    print("successful initialization and push to aws secrets manager ✅")
  except Exception as error:
    print("failed to send secrets to aws manager ❌", error)


if __name__ == "__main__":
    sendENV()