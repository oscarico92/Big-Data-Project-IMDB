"""Send live Wikipedia changes (Wikimedia EventStreams) to a Kafka topic.

Adapted from lab 5. Runs on the host (not in Docker), Kafka is reached on
localhost:9092. Requirements: pip install pywikibot confluent-kafka

Examples:
    python streaming/admin.py                                 # create the topic once
    python streaming/wikistream_producer.py --minutes 25      # live test window
    python streaming/wikistream_producer.py --late-ratio 0    # no simulated late data
"""
import os

# pywikibot looks for a user-config.py at import time: we only read the public
# event stream (no login, no edit), so we tell it to skip the config
os.environ.setdefault("PYWIKIBOT_NO_USER_CONFIG", "1")

import argparse
import json
import random
import socket
import time
from datetime import datetime, timedelta

from confluent_kafka import Producer
from pywikibot.comms.eventstreams import EventStreams

parser = argparse.ArgumentParser(description="Send Wikipedia recent changes to Kafka")
parser.add_argument("--wiki", nargs="+", default=["en.wikipedia.org"],
                    help="server_name(s) to follow, e.g. en.wikipedia.org fr.wikipedia.org")
parser.add_argument("--type", nargs="+", default=["edit", "new"],
                    help="change types to follow: edit, new, log, categorize")
parser.add_argument("--minutes", type=float, default=25, help="duration of the test window")
parser.add_argument("--topic", default="wiki-changes")
parser.add_argument("--bootstrap", default="localhost:9092")
# late data simulation: a share of the events is held back before being sent,
# as if it had been delayed on the network. Used to test the watermark.
parser.add_argument("--late-ratio", type=float, default=0.03,
                    help="share of events sent late (0 = none)")
parser.add_argument("--late-minutes", type=float, default=12,
                    help="delay of the late events, in minutes")
args = parser.parse_args()

producer = Producer({
    "bootstrap.servers": args.bootstrap,
    "client.id": socket.gethostname(),
    "compression.type": "lz4",
})


def send(change):
    # key = page title: all the changes of one page go to the same partition
    producer.produce(args.topic, key=change["title"].encode("utf-8"),
                     value=json.dumps(change).encode("utf-8"))
    producer.poll(0)


stream = EventStreams(streams=["recentchange"])
stream.register_filter(server_name=list(args.wiki), type=list(args.type))
print(f"wikis {args.wiki} | types {args.type} | topic {args.topic} | "
      f"late {args.late_ratio:.0%} of events delayed {args.late_minutes} min")

stop_time = datetime.now() + timedelta(minutes=args.minutes)
held_back = []  # (send_at, change)
sent = late_sent = 0

while datetime.now() < stop_time:
    change = next(stream)
    if random.random() < args.late_ratio:
        change["simulated_delay_s"] = int(args.late_minutes * 60)
        held_back.append((time.time() + args.late_minutes * 60, change))
    else:
        send(change)
        sent += 1

    now = time.time()
    for item in [h for h in held_back if h[0] <= now]:
        send(item[1])
        held_back.remove(item)
        late_sent += 1

    if (sent + late_sent) % 100 == 0:
        print(f"{datetime.now():%H:%M:%S} sent {sent} on time, {late_sent} late, "
              f"{len(held_back)} waiting | last: {change['title']}")

# events still held back are sent at the end (very late)
for _, change in held_back:
    send(change)
    late_sent += 1
producer.flush()
print(f"done: {sent} on time and {late_sent} late events sent to '{args.topic}'")
