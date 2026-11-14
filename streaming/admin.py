"""Create (or list) the Kafka topic used by the streaming pipeline. Runs on the host."""
import argparse

from confluent_kafka.admin import AdminClient, NewTopic

parser = argparse.ArgumentParser()
parser.add_argument("--topic", default="wiki-changes")
parser.add_argument("--partitions", type=int, default=3)
parser.add_argument("--bootstrap", default="localhost:9092")
parser.add_argument("--delete", action="store_true", help="delete the topic instead")
args = parser.parse_args()

admin = AdminClient({"bootstrap.servers": args.bootstrap})

if args.delete:
    futures = admin.delete_topics([args.topic])
else:
    futures = admin.create_topics([NewTopic(args.topic, num_partitions=args.partitions,
                                            replication_factor=1)])
for name, future in futures.items():
    try:
        future.result()
        print(f"topic '{name}' {'deleted' if args.delete else 'created'}")
    except Exception as error:  # e.g. the topic already exists
        print(f"topic '{name}': {error}")

print("topics:", sorted(admin.list_topics(timeout=10).topics))
