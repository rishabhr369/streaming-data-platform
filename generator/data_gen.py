import os, json, random, time, sys, yaml, threading
from datetime import datetime, timezone, timedelta
from faker import Faker
from confluent_kafka import Producer
from pathlib import Path
from collections import defaultdict
import signal
from concurrent.futures import ThreadPoolExecutor

# Add parent directory to path to import config_loader
sys.path.append(str(Path(__file__).parent.parent))
from config_loader import ConfigLoader

# Load configuration from config.yml, fallback to environment variables
try:
    config = ConfigLoader("/app/../config.yml")
    bootstrap = config.get("data_generator.bootstrap_servers", "kafka-1:9092")
    eps_click = config.get("data_generator.events_per_second.clickstream", 50)
    eps_iot = config.get("data_generator.events_per_second.iot", 30)
    partitions = config.get("kafka.partitions", 6)
    print(f"✅ Loaded configuration from config.yml")
except Exception as e:
    print(f"⚠️  Failed to load config.yml ({e}), falling back to environment variables")
    bootstrap = os.getenv("BOOTSTRAP_SERVERS", "kafka-1:9092")
    eps_click = int(os.getenv("EPS_CLICK", "50"))
    eps_iot = int(os.getenv("EPS_IOT", "30"))
    partitions = int(os.getenv("PARTITIONS", "6"))


# Simplified Kafka Producer Configuration for Learning
conf = {
    # === CONNECTION SETTINGS ===
    'bootstrap.servers': bootstrap,
    'client.id': 'learning-producer',
    
    # === BATCHING OPTIMIZATIONS ===
    # Increase batch size for better throughput (default: 16384 bytes)
    # Larger batches = fewer network requests = higher throughput
    'batch.size': 32768,  # 32KB batches (2x default, good starting point)
    
    # Wait time to batch more messages together (default: 0ms)
    # Small delay allows more messages to accumulate in batches
    'linger.ms': 5,  # Wait max 5ms to batch messages
    
    # === COMPRESSION ===
    # Reduce network bandwidth and improve throughput
    # Options: none, gzip, snappy, lz4, zstd
    'compression.type': 'lz4',  # Fast compression with good ratio
    
    # === RELIABILITY vs PERFORMANCE ===
    # acks=0: No acknowledgment (fastest, but data loss possible)
    # acks=1: Leader acknowledges (good balance) ← RECOMMENDED FOR LEARNING
    # acks=all: All replicas acknowledge (slowest, but most reliable)
    'acks': 1,
    
    # === MEMORY BUFFERING ===
    # Maximum number of messages buffered per partition (Python client)
    # More buffer = more batching opportunities  
    'queue.buffering.max.messages': 100000,  # Max messages to buffer
    
    # === RETRY LOGIC (IMPORTANT TO UNDERSTAND!) ===
    # How many times to retry failed sends (default: 2147483647)
    'retries': 5,  # Retry up to 5 times if send fails
    
    # How long to wait between retries (default: 100ms)
    'retry.backoff.ms': 1000,  # Wait 1 second between retries
}


# Add connection retry logic
print(f"🔄 Attempting to connect to Kafka brokers: {bootstrap}")
for attempt in range(10):
    try:
        producer = Producer(conf)
        # Test the connection by getting metadata
        metadata = producer.list_topics(timeout=10)
        print(f"✅ Successfully connected to Kafka! Topics: {list(metadata.topics.keys())}")
        break
    except Exception as e:
        print(f"⚠️  Connection attempt {attempt + 1}/10 failed: {e}")
        if attempt < 9:
            time.sleep(5)
        else:
            print("❌ Failed to connect to Kafka after 10 attempts")
            exit(1)

# === PERFORMANCE MONITORING ===
class PerformanceMonitor:
    def __init__(self):
        self.stats = defaultdict(int)
        self.start_time = time.time()
        self.last_report = time.time()
        self.lock = threading.Lock()
    
    def increment(self, metric, count=1):
        with self.lock:
            self.stats[metric] += count
    
    def report(self):
        current_time = time.time()
        elapsed = current_time - self.last_report
        total_elapsed = current_time - self.start_time
        
        with self.lock:
            total_events = self.stats['clickstream_sent'] + self.stats['iot_sent']
            events_per_sec = total_events / total_elapsed if total_elapsed > 0 else 0
            recent_rate = total_events / elapsed if elapsed > 0 else 0
            
            print(f"📊 THROUGHPUT STATS:")
            print(f"   Total Events: {total_events:,}")
            print(f"   Events/sec: {events_per_sec:.1f} (avg) | {recent_rate:.1f} (recent)")
            print(f"   Clickstream: {self.stats['clickstream_sent']:,} | IoT: {self.stats['iot_sent']:,}")
            print(f"   Errors: {self.stats['errors']}")
            print(f"   Delivery Success: {self.stats['delivered']:,}")
            
            self.last_report = current_time

monitor = PerformanceMonitor()

# === OPTIMIZED DATA GENERATION ===
fake = Faker()

# Pre-generate static data for efficiency
urls = ["/home", "/search", "/product", "/cart", "/checkout", "/help", "/about", "/contact", "/api/v1/products", "/api/v1/users"]
user_agents = [fake.user_agent() for _ in range(100)]  # Pool of user agents
cities = [fake.city() for _ in range(50)]  # Pool of cities

# Optimized timestamp generation with slight delay to ensure past timestamps
def now_iso():
    # Subtract 30 seconds to ensure events are in the past for watermark processing
    return (datetime.now(timezone.utc) - timedelta(seconds=30)).isoformat()

# Pre-generate IDs for better performance
user_ids = [f"u{str(i).zfill(5)}" for i in range(1, 10000)]  # Increased pool size
device_ids = [f"d{str(i).zfill(5)}" for i in range(1, 5000)]

# Optimized key generation
click_key = lambda uid: uid.encode()
iot_key = lambda did: did.encode()

# === DELIVERY CALLBACK FOR MONITORING ===
def delivery_callback(err, msg):
    if err:
        monitor.increment('errors')
        print(f"❌ Delivery failed: {err}")
    else:
        monitor.increment('delivered')

# === BATCH EVENT GENERATION ===
class EventGenerator:
    def __init__(self):
        self.timestamp_cache = ""
        self.last_timestamp_update = 0
    
    def get_timestamp(self):
        # Reduce cache time to 1 second and ensure fresh timestamps
        current_time = time.time()
        if current_time - self.last_timestamp_update > 1.0:  # Cache for 1 second instead of 100ms
            self.timestamp_cache = now_iso()
            self.last_timestamp_update = current_time
        return self.timestamp_cache
    
    def generate_clickstream_batch(self, count):
        """Generate multiple clickstream events efficiently"""
        events = []
        timestamp = self.get_timestamp()
        
        for _ in range(count):
            uid = random.choice(user_ids)
            evt = {
                "event_id": fake.uuid4(),
                "user_id": uid,
                "url": random.choice(urls),
                "referrer": fake.uri(),
                "ua": random.choice(user_agents),  # Use pre-generated user agents
                "session_id": f"s{random.randint(100000, 999999)}",  # Add session tracking
                "ts": timestamp
            }
            events.append((uid, evt))
        return events
    
    def generate_iot_batch(self, count):
        """Generate multiple IoT events efficiently"""
        events = []
        timestamp = self.get_timestamp()
        
        for _ in range(count):
            did = random.choice(device_ids)
            evt = {
                "device_id": did,
                "site": random.choice(cities),  # Use pre-generated cities
                "temp_c": round(random.uniform(15, 40), 2),
                "humidity": round(random.uniform(10, 90), 2),
                "battery": round(random.uniform(20, 100), 1),
                "signal_strength": random.randint(-100, -30),  # Add more sensor data
                "ts": timestamp
            }
            events.append((did, evt))
        return events

event_generator = EventGenerator()


# === HIGH-THROUGHPUT ASYNC PRODUCTION ===
class HighThroughputProducer:
    def __init__(self, producer, target_eps_click=200, target_eps_iot=150):
        self.producer = producer
        self.target_eps_click = target_eps_click
        self.target_eps_iot = target_eps_iot
        self.running = True
        self.batch_size = 50  # Send events in batches for efficiency
        
    def stop(self):
        self.running = False
    
    def produce_clickstream_batch(self):
        """Produce clickstream events in batches for maximum throughput"""
        while self.running:
            try:
                # Generate batch of events
                events = event_generator.generate_clickstream_batch(self.batch_size)
                
                # Produce all events in the batch
                for uid, evt in events:
                    self.producer.produce(
                        "clickstream",
                        key=click_key(uid),
                        value=json.dumps(evt).encode(),
                        callback=delivery_callback
                    )
                    monitor.increment('clickstream_sent')
                
                # Non-blocking poll to handle delivery callbacks
                self.producer.poll(0)
                
                # Dynamic sleep to achieve target throughput
                # Calculate sleep time based on target events per second
                sleep_time = self.batch_size / self.target_eps_click
                time.sleep(max(0.001, sleep_time))  # Minimum 1ms sleep
                
            except Exception as e:
                print(f"❌ Error in clickstream production: {e}")
                monitor.increment('errors')
                time.sleep(0.1)
    
    def produce_iot_batch(self):
        """Produce IoT events in batches for maximum throughput"""
        while self.running:
            try:
                # Generate batch of events
                events = event_generator.generate_iot_batch(self.batch_size)
                
                # Produce all events in the batch
                for did, evt in events:
                    self.producer.produce(
                        "iot",
                        key=iot_key(did),
                        value=json.dumps(evt).encode(),
                        callback=delivery_callback
                    )
                    monitor.increment('iot_sent')
                
                # Non-blocking poll to handle delivery callbacks
                self.producer.poll(0)
                
                # Dynamic sleep to achieve target throughput
                sleep_time = self.batch_size / self.target_eps_iot
                time.sleep(max(0.001, sleep_time))
                
            except Exception as e:
                print(f"❌ Error in IoT production: {e}")
                monitor.increment('errors')
                time.sleep(0.1)
    
    def monitor_performance(self):
        """Background thread to monitor and report performance"""
        while self.running:
            time.sleep(10)  # Report every 10 seconds
            monitor.report()
    
    def flush_producer(self):
        """Background thread to periodically flush the producer"""
        while self.running:
            time.sleep(5)  # Flush every 5 seconds
            remaining = self.producer.flush(timeout=1.0)
            if remaining > 0:
                print(f"⚠️  {remaining} messages still in queue after flush")

# === GRACEFUL SHUTDOWN ===
def signal_handler(signum, frame):
    print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
    high_throughput_producer.stop()
    
    # Final flush
    print("🔄 Flushing remaining messages...")
    remaining = producer.flush(timeout=30.0)
    if remaining > 0:
        print(f"⚠️  {remaining} messages were not delivered")
    else:
        print("✅ All messages delivered successfully")
    
    # Final stats
    monitor.report()
    exit(0)

# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# === MAIN EXECUTION ===
# Create high-throughput producer with increased target rates
# You can adjust these values based on your system's capacity
target_clickstream_eps = eps_click * 4  # 4x the original rate
target_iot_eps = eps_iot * 3  # 3x the original rate

print(f"🚀 Starting ENHANCED producer for learning:")
print(f"   Target Clickstream: {target_clickstream_eps} events/sec")
print(f"   Target IoT: {target_iot_eps} events/sec")
print(f"   Kafka Configuration: LZ4 compression, 32KB batches, 5ms linger")
print(f"   Retry Logic: 5 retries with 1 second backoff")
print(f"   Press Ctrl+C for graceful shutdown\n")

high_throughput_producer = HighThroughputProducer(
    producer, 
    target_clickstream_eps, 
    target_iot_eps
)

# Start producer threads
with ThreadPoolExecutor(max_workers=4, thread_name_prefix="KafkaProducer") as executor:
    # Submit all production tasks
    futures = [
        executor.submit(high_throughput_producer.produce_clickstream_batch),
        executor.submit(high_throughput_producer.produce_iot_batch),
        executor.submit(high_throughput_producer.monitor_performance),
        executor.submit(high_throughput_producer.flush_producer)
    ]
    
    # Wait for threads to complete (or interruption)
    try:
        for future in futures:
            future.result()
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)