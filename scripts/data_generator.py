import asyncio
from aiokafka import AIOKafkaProducer
import json
import time
import random

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "telemetry-logs"

async def produce_mock_logs():
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    try:
        services = ["payment-service", "order-service", "user-service", "streaming-node"]
        error_types = ["TIMEOUT", "DB_ERROR", "500_INTERNAL_SERVER", "LATENCY_SPIKE"]
        
        print(f"--- Starting mock log production to {TOPIC} ---")
        while True:
            service = random.choice(services)
            error = random.choice(error_types)
            log_event = {
                "timestamp": time.time(),
                "service": service,
                "level": "ERROR" if random.random() > 0.8 else "INFO",
                "message": f"Sample log from {service}: {error}" if random.random() > 0.8 else f"Heartbeat from {service}",
                "trace_id": f"trace-{random.randint(1000, 9999)}"
            }
            
            await producer.send_and_wait(TOPIC, json.dumps(log_event).encode('utf-8'))
            await asyncio.sleep(0.5)  # Simulate high-concurrency flow
    finally:
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(produce_mock_logs())
