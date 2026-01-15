import json
import asyncio
from aiokafka import AIOKafkaConsumer

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "telemetry-logs"

async def consume_logs():
    consumer = AIOKafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="rca-group",
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    await consumer.start()
    try:
        print(f"--- Listening for logs on {TOPIC} ---")
        async for msg in consumer:
            log = msg.value
            if log.get("level") == "ERROR":
                print(f"⚠️ [Anomalous Log Detected] Service: {log['service']}, Message: {log['message']}")
                # Here we would trigger the AI Agent
    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(consume_logs())
