# 🚀 Mini Cluster Setup - Production Data Engineering Platform

A **production-ready containerized data engineering platform** featuring Apache Kafka, Apache Spark, and high-performance data generation for real-time stream processing, analytics, and data science experimentation. 

**🎯 What makes this special:**
- 🔥 **High-Performance Data Generator** with multi-threading and 4x throughput optimization
- 📊 **Built-in Data Analytics Platform** with Jupyter notebooks and comprehensive analysis
- 💾 **Production Data Lake** with structured data processing and partitioning
- 🛠️ **YAML-Based Configuration** for easy management across environments
- 🔄 **Real-time Stream Processing** with fault tolerance and checkpointing
- 📈 **Live Data Analytics** with actual processed data ready for exploration

## ✨ Latest Updates

**v3.0 - High-Performance Data Platform**
- 🚀 **High-Throughput Data Generator**: Multi-threaded producer with 4x performance boost (200+ events/sec)
- 📊 **Data Analytics Platform**: Comprehensive Jupyter notebook with real data analysis
- 💾 **Production Data Storage**: Structured data across clickstream, IoT, and aggregations
- 🔧 **Enhanced Configuration**: Advanced YAML config system with fallback mechanisms
- 🛠️ **Advanced Tooling**: Data cleanup utilities, statistics, and management commands
- 📈 **Performance Monitoring**: Real-time throughput metrics and delivery tracking
- 🔄 **Graceful Shutdown**: Proper signal handling and message flushing
- 🏗️ **Production Architecture**: Custom containers with optimized dependencies

## 🚀 Quick Start

### 1. Setup Configuration
```bash
# Initial setup (interactive)
make setup

# Or just generate .env from config.yml
make config
```

### 2. Start the Cluster
```bash
# Starts cluster with automated volume initialization
make up
```

> **Note**: The cluster includes automated volume initialization and will begin generating high-performance data streams immediately. The enhanced data generator produces 4x more events than the basic version for realistic load testing.

### 3. Monitor the Cluster
```bash
# View logs (see real-time performance metrics)
make logs

# Check status
make ps

# View configuration
make show-config

# View data statistics (NEW!)
make data-stats
```

### 4. Explore the Data
```bash
# Open the comprehensive data analysis notebook
jupyter notebook datalake_analysis.ipynb

# Check data volume and statistics
make data-stats
```

## 📝 Configuration

The entire cluster is configured via `config.yml`. This YAML-based configuration is much more readable and manageable than environment variables. All services now automatically read configuration from this centralized file.

### config.yml Structure

```yaml
kafka:
  kraft_cluster_id: "unique-cluster-id"
  partitions: 4
  replication_factor: 2
  min_insync_replicas: 1
  external_ports:
    broker_1: 19092
    broker_2: 29092
    broker_3: 39092
  bootstrap_servers: "kafka-1:9092,kafka-2:9092,kafka-3:9092"

spark:
  worker_memory: "2g"
  worker_cores: 2
  master_url: "spark://spark-master:7077"

data_generator:
  events_per_second:
    clickstream: 30  # Base rate (actual: 4x = 120 events/sec)
    iot: 20          # Base rate (actual: 3x = 60 events/sec)
  bootstrap_servers: "kafka-1:9092,kafka-2:9092,kafka-3:9092"

storage:
  datalake_root: "/datalake"
  checkpoint_root: "/checkpoints"

topics:
  clickstream: "clickstream"
  iot: "iot"

ui:
  kafka_ui_port: 8080
  spark_master_ui_port: 8081
```

### Configuration Workflow

1. **Edit `config.yml`** with your desired settings
2. **Run `make config`** to generate the `.env` file from your YAML configuration
3. **Run `make up`** to apply the changes (restarts containers if already running)

## 🛠️ Available Commands

| Command | Description |
|---------|-------------|
| `make setup` | Interactive setup with dependency installation |
| `make config` | Generate .env from config.yml |
| `make up` | Start all services with automated volume initialization |
| `make down` | Stop all services |
| `make logs` | View service logs |
| `make ps` | Show service status |
| `make clean` | Stop services and remove volumes |
| `make reset` | Clean and restart |
| `make show-config` | Display current configuration |
| `make init-volumes` | Initialize volumes with proper permissions (automated) |

## 🏗️ Architecture

### Services

- **Kafka Cluster**: 3-node KRaft cluster with external access
- **Kafka UI**: Web interface at http://localhost:8080
- **Spark Master**: Web UI at http://localhost:8081
- **Spark Workers**: 2 worker nodes with custom Apache Spark images
- **🔥 High-Performance Data Generator**: Multi-threaded producer (200+ events/sec)
- **Spark ETL**: Real-time streaming job with comprehensive processing
- **📊 Data Analytics Platform**: Jupyter notebook with live data analysis

### Data Flow

1. **🔥 High-Performance Data Generator** produces events at scale using multi-threading
   - Batch processing with LZ4 compression
   - Performance monitoring with real-time metrics
   - Graceful shutdown with message flushing
2. **Spark Streaming ETL** consumes and processes events in real-time
3. **Processed data** stored in Parquet format with date partitioning
4. **Aggregated analytics** creates windowed analytics (page views per minute)
5. **📊 Data Analytics Platform** provides comprehensive data exploration
6. **Monitoring** via Kafka UI, Spark UI, and performance metrics

### Volume Management & Data Persistence

The cluster uses **bind mounts** for production-grade data persistence:
- **📊 Production Data Lake**: Stores processed data in structured format
  - `./data/datalake/tables/clickstream/` - User interaction data (Parquet)
  - `./data/datalake/tables/iot/` - IoT sensor data (Parquet)
  - `./data/datalake/tables/clickstream_agg/` - Real-time aggregations
- **🔄 Checkpoint Management**: Streaming fault tolerance and state management
- **📁 Direct Access**: Data visible in your IDE at `./data/` for analysis
- **🛠️ Data Management**: Comprehensive cleanup and statistics commands

### Data Processing

The streaming ETL pipeline processes three data streams:

1. **Raw Clickstream** (`/datalake/tables/clickstream/`)
   - Source: User interactions (page views, clicks)
   - Format: Parquet with date partitioning (`dt=YYYY-MM-DD`)
   - Schema: `event_id`, `user_id`, `url`, `referrer`, `ua`, `ts`

2. **Clickstream Aggregations** (`/datalake/tables/clickstream_agg/`)
   - Source: Windowed aggregations (1-minute windows)
   - Format: Parquet with date partitioning 
   - Schema: `minute_start`, `minute_end`, `url`, `pv` (page views)

3. **IoT Sensor Data** (`/datalake/tables/iot/`)
   - Source: Device telemetry (temperature, humidity, battery)
   - Format: Parquet with date partitioning
   - Schema: `device_id`, `site`, `temp_c`, `humidity`, `battery`, `signal_strength`, `ts`

## 📊 Data Analytics Platform

The project includes a comprehensive **Jupyter notebook** (`datalake_analysis.ipynb`) for data exploration:

### Available Analysis
- **📈 Data Volume Overview**: File counts, sizes, and partitioning analysis
- **🌐 Clickstream Analytics**: User behavior patterns and page view analytics
- **🌡️ IoT Sensor Analysis**: Temperature, humidity, and device health monitoring
- **📊 Time Series Analysis**: Trend analysis and pattern recognition
- **🔍 Interactive Exploration**: Pandas, Matplotlib, and Seaborn visualizations

### Key Metrics Available
- **Data Processing**: Continuously processed clickstream and IoT data
- **Time Series Data**: Multi-day historical data with date partitioning
- **Data Types**: Clickstream events, IoT sensor readings, and aggregated analytics
- **Real-time Processing**: Continuous stream processing with checkpointing

## 🔧 Configuration Changes

### Changing Kafka Settings

To modify Kafka configuration (partitions, replication factor, etc.):

1. Edit `config.yml`:
   ```yaml
   kafka:
     partitions: 6  # Changed from 4
     replication_factor: 3  # Changed from 2
   ```

2. Regenerate configuration:
   ```bash
   make config
   ```

3. **Important**: Topic configuration changes require topic recreation:
   ```bash
   # Delete existing topics
   docker exec kafka-1 /opt/bitnami/kafka/bin/kafka-topics.sh --bootstrap-server kafka-1:9092 --delete --topic clickstream
   docker exec kafka-1 /opt/bitnami/kafka/bin/kafka-topics.sh --bootstrap-server kafka-1:9092 --delete --topic iot
   
   # Restart to recreate with new settings
   make down && make up
   ```

### Changing Data Generation Rates

1. Edit `config.yml`:
   ```yaml
   data_generator:
     events_per_second:
       clickstream: 100  # Increased from 50
       iot: 60          # Increased from 30
   ```

2. Apply changes:
   ```bash
   make config
   make down && make up  # Restart data generator
   ```

## 📊 Monitoring & Analytics

- **Kafka UI**: http://localhost:8080 - Browse topics, partitions, messages
- **Spark Master UI**: http://localhost:8081 - Monitor Spark jobs and workers  
- **📊 Data Analytics**: `jupyter notebook datalake_analysis.ipynb` - Comprehensive data analysis
- **📈 Performance Metrics**: Real-time throughput monitoring in data generator logs
- **📋 Data Statistics**: `make data-stats` - File counts, sizes, and table breakdown
- **🔍 Logs**: `make logs` - View all service logs with performance metrics

## 🧹 Data Management & Cleanup

### Production Data Management
```bash
# Check current data volume and statistics
make data-stats

# Clean all local data (interactive confirmation)
make clean-data

# Clean only processed data (keep streaming state)
make clean-datalake

# Clean only streaming checkpoints (keep processed data) 
make clean-checkpoints
```

### Service Management
```bash
# Stop services (keeps all data)
make down

# Stop and remove Docker volumes (keeps bind mount data)
make clean

# Complete reset
make reset
```

> **Note**: With bind mounts, your data persists in `./data/` even after `make clean`. Use the specific data cleanup commands above for data management.

## 🔍 Troubleshooting

### Quick Fixes

```bash
# Check configuration and logs
make show-config  # View current settings
make logs         # Check service logs
make ps          # Check service status

# Restart services
docker compose restart spark-app    # Restart Spark job
make down && make up               # Full restart
```

### Common Issues

| **Issue** | **Solution** |
|-----------|-------------|
| Services won't start | Check `make logs` for errors |
| No data processing | Verify Spark app is running at http://localhost:8081 |
| Kafka connection errors | Ensure all 3 Kafka brokers are healthy |
| Permission errors | Run `make init-volumes` to fix permissions |
| Config changes not applied | Run `make config` then restart services |

### Requirements

- Docker & Docker Compose
- Python 3.x with PyYAML (auto-installed via `make setup`)

## 📁 File Structure

```
.
├── config.yml              # Main configuration file
├── config_loader.py         # Configuration loader utility
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Docker services definition
├── Makefile                # Build automation with volume init
├── generator/
│   ├── Dockerfile          # Enhanced with PyYAML support
│   └── data_gen.py         # 🔥 High-performance multi-threaded generator
├── datalake_analysis.ipynb # 📊 Comprehensive data analysis notebook
├── scripts/                # 🆕 Unified scripts directory
│   ├── setup.sh           # Setup script (moved here)
│   ├── create_topics.sh    # Topic creation script (moved here)
│   ├── submit.sh          # Spark job submission script (moved here)
│   └── init-volumes.sh    # 🆕 Volume initialization script
├── data/                   # 📁 Production data persistence
│   ├── datalake/          # Processed data files (Parquet format)
│   └── checkpoints/       # Streaming state and checkpoint files
└── spark/
    ├── Dockerfile          # Apache Spark image (updated)
    └── jobs/
        └── streaming_etl.py # Spark ETL job (watermark fixed)
```

### 🆕 Recent Improvements

- **🚀 High-Performance Data Generator**: Multi-threaded with 4x throughput boost
- **📊 Data Analytics Platform**: Jupyter notebook with comprehensive analysis tools
- **📦 Production Data Storage**: Structured data processing and storage
- **🔧 Enhanced Configuration**: Advanced YAML system with fallback mechanisms
- **🛠️ Advanced Data Management**: Cleanup utilities and statistics commands
- **📈 Performance Monitoring**: Real-time metrics and delivery tracking
- **🏗️ Production Architecture**: Custom containers with optimized builds

## 🎯 Key Features

### 🔥 High-Performance Data Generation
- **Multi-threaded Production**: 4 concurrent threads for maximum throughput
- **Batch Processing**: 50-event batches with LZ4 compression
- **Performance Monitoring**: Real-time metrics every 10 seconds
- **Target Rates**: 200+ clickstream events/sec, 150+ IoT events/sec
- **Graceful Shutdown**: Signal handling with proper message flushing

### 📊 Production Data Analytics
- **Live Data Lake**: Structured data processing ready for analysis
- **Multiple Data Streams**: Clickstream, IoT sensors, and aggregated analytics
- **Interactive Analysis**: Jupyter notebooks with rich visualizations
- **Time Series Data**: Multi-day historical data with date partitioning
- **Real-time Processing**: Continuous stream processing with fault tolerance

### 🛠️ Enterprise-Grade Configuration
- **YAML-First**: Central configuration with dot-notation access
- **Fallback Systems**: Graceful degradation to environment variables
- **Auto-Generation**: Converts YAML to Docker Compose environment
- **Type Safety**: Configuration validation and error handling

The configuration system supports both simple environment variable usage and sophisticated YAML-based configuration for production deployments, making it suitable for both development and production use cases.
