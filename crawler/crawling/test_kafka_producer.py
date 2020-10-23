from kafka import KafkaProducer
from kafka.errors import KafkaError
import json

producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))
topic = 'demo.outbound_firehose'
# Asynchronous by default
json_obj = {'id':"100", 'name':'zzs'}
future = producer.send(topic, json_obj)

# Block for 'synchronous' sends
try:
    record_metadata = future.get(timeout=10)
except KafkaError:
    # Decide what to do if produce request failed...
    print('failed send')
    pass


def on_send_success(record_metadata):
    print(record_metadata.topic)
    print(record_metadata.partition)
    print(record_metadata.offset)

def on_send_error(excp):
    print('I am an errback')
    # handle exception

# produce asynchronously with callbacks
producer.send(topic, json_obj).add_callback(on_send_success).add_errback(on_send_error)

# block until all async messages are sent
producer.flush()

# configure multiple retries
producer = KafkaProducer(retries=5)