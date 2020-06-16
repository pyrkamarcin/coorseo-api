from pykafka import KafkaClient

client = KafkaClient(hosts="kafka1:19092")
topic = client.topics['example_topic']
