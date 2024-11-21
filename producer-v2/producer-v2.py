import pika
import avro.schema
import avro.io
import requests
from io import BytesIO
import time
import random
import string

# time.sleep(10)

###########################################################################################
##### Initialisation
###########################################################################################

# Rabbitmq Configurations
rabbitmq_host = 'rabbitmq'
queue_name = 'sctd_user_queue'

# Apicurio Configurations
group_id = "sctd"
schema_registry_url = 'http://apicurio-registry:8080'
schema_name = "User"
artifact_id = "sctd_systems_tower_demo_user"

schema_str = '''
{
  "type": "record",
  "name": "User",
  "fields": [
    {"name": "name", "type": "string"},
    {"name": "email", "type": "string"}
  ]
}
'''

# Register schema with Apicurio Schema Registry
headers = {
    "Content-Type": "application/json",
    "X-Registry-ArtifactType": "AVRO",
    "X-Registry-ArtifactId": artifact_id,
    "X-Registry-Name": schema_name
    }
param = "ifExists=UPDATE"
response = requests.post(
  url=f"{schema_registry_url}/apis/registry/v2/groups/{group_id}/artifacts?{param}", 
  headers=headers, 
  data=schema_str
  )
print(f"response.json(): {response.json()}", flush=True)
schema_id = response.json()['id']
schema_version = response.json()['version']
# print(f"schema_id: {schema_id}", flush=True)


# Create RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()
channel.queue_declare(queue=queue_name, durable=True)



###########################################################################################
#### Rabbitmq producer functionality
###########################################################################################

while True:

  # Simulate message
  name = random.choice(["Alice","Bob","Charlie"])
  email = f"{name.lower()}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=5))}@gmail.com"

  message = {
      "name": name, 
      "email": email
  }

  # Avro serializer
  schema = avro.schema.parse(schema_str)
  writer = avro.io.DatumWriter(schema)
  bytes_writer = BytesIO()
  encoder = avro.io.BinaryEncoder(bytes_writer)
  writer.write(message, encoder)
  serialized_message = bytes_writer.getvalue()

  # Send message
  channel.basic_publish(
    exchange='', 
    routing_key=queue_name, 
    body=serialized_message,
    properties=pika.BasicProperties(
        headers = {
          'schema_artifact_id':artifact_id,
          'schema_artifact_version':schema_version,
          }
    )
    )
  print(f"[x] Sent message: {message}", flush=True)
  # print(f"Serialized message: {serialized_message}", flush=True)

  time.sleep(5)

###########################################################################################
###########################################################################################

