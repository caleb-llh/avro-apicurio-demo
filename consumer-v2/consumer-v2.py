import pika
import avro.schema
import avro.io
import requests
from io import BytesIO
import time

time.sleep(5)

###########################################################################################
##### Initialisation
###########################################################################################

# Rabbitmq Configurations
rabbitmq_host = 'rabbitmq'
queue_name = 'sctd_user_queue'

# Apicurio Configurations
group_id = "sctd"
schema_registry_url = 'http://apicurio-registry:8080'

# Schema cache 
cache = {}

# Create RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()
channel.queue_declare(queue=queue_name, durable=True)


###########################################################################################
#### Rabbitmq consumer functionality
###########################################################################################

def callback(ch, method, properties, body):
    # Get schema ID and version from message header
    artifact_id = properties.headers['schema_artifact_id']
    schema_version = properties.headers['schema_artifact_version']
    
    # Get schema from Apicurio Schema Registry if not cached
    if artifact_id+schema_version not in cache:
        response = requests.get(f"{schema_registry_url}/apis/registry/v2/groups/{group_id}/artifacts/{artifact_id}/versions/{schema_version}")
        schema_str = response.text
        print(f"schema_str:{schema_str}", flush=True)
        cache[artifact_id+schema_version] = schema_str

    print(body, flush=True)

    # Avro deserialization
    bytes_reader = BytesIO(body)
    decoder = avro.io.BinaryDecoder(bytes_reader)
    schema = avro.schema.parse(cache[artifact_id+schema_version])
    reader = avro.io.DatumReader(schema)
    data = reader.read(decoder)

    print(data)
    print(f"[x] Hi I am {data['name']} and my email is {data['email']}!\n", flush=True)

# Consume messages
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
