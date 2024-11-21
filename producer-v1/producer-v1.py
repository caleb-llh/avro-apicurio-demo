import pika
import avro.schema
import avro.io
import requests
from io import BytesIO
import time
import random

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
artifact_id = "sctd_systems_tower_demo_user"
schema_version = '1'


# Get schema from Apicurio Schema Registry
response = requests.get(f"{schema_registry_url}/apis/registry/v2/groups/{group_id}/artifacts/{artifact_id}/versions/{schema_version}")
schema_str = response.text
print(f"schema_str:{schema_str}", flush=True)


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
  age = random.randint(50, 70)

  message = {
      "name": name, 
      "age": age,
  }

  # Avro serializer
  bytes_writer = BytesIO()
  encoder = avro.io.BinaryEncoder(bytes_writer)
  schema = avro.schema.parse(schema_str)
  writer = avro.io.DatumWriter(schema)
  writer.write(message, encoder)
  serialized_message = bytes_writer.getvalue()

  # Send message
  channel.basic_publish(
    exchange='', 
    routing_key=queue_name, 
    body=serialized_message,
    )
  print(f"[x] Sent message: {message}", flush=True)
  # print(f"Serialized message: {serialized_message}", flush=True)

  time.sleep(5)

###########################################################################################
###########################################################################################

