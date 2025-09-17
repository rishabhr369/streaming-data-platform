#!/bin/bash
# Host directory initialization script for Mini Cluster Setup
# This script sets up local host directories for datalake and checkpoints (bind mounts)

set -euo pipefail

echo "🔧 Initializing host directories for Mini Cluster Setup..."

# Define the base data directory
DATA_DIR="./data"

# Function to create host directories with proper permissions
create_host_directory() {
    local dir_path=$1
    local description=$2
    
    echo "📁 Creating directory: $dir_path ($description)"
    
    # Create the directory if it doesn't exist
    mkdir -p "$dir_path"
    
    # Set permissions to allow Docker containers to write
    chmod 755 "$dir_path"
    
    echo "✅ Created: $dir_path"
}

echo "🗂️  Setting up data directories..."

# Create base data directory
create_host_directory "$DATA_DIR" "Base data directory"

# Create datalake subdirectories for different table types
create_host_directory "$DATA_DIR/datalake" "Data lake root"
create_host_directory "$DATA_DIR/datalake/tables" "Tables directory"
create_host_directory "$DATA_DIR/datalake/tables/clickstream" "Clickstream data"
create_host_directory "$DATA_DIR/datalake/tables/clickstream_agg" "Clickstream aggregations"
create_host_directory "$DATA_DIR/datalake/tables/iot" "IoT sensor data"

# Create checkpoints subdirectories for streaming jobs (matches Spark structure)
create_host_directory "$DATA_DIR/checkpoints" "Checkpoints root"
create_host_directory "$DATA_DIR/checkpoints/streaming_etl" "Streaming ETL job root"
create_host_directory "$DATA_DIR/checkpoints/streaming_etl/clickstream" "Clickstream job checkpoints"
create_host_directory "$DATA_DIR/checkpoints/streaming_etl/clickstream_agg" "Clickstream aggregation checkpoints"
create_host_directory "$DATA_DIR/checkpoints/streaming_etl/iot" "IoT job checkpoints"

echo ""
echo "✅ Host directory initialization complete!"
echo ""
echo "📋 Directory Structure Created:"
echo "   $DATA_DIR/"
echo "   ├── datalake/"
echo "   │   └── tables/"
echo "   │       ├── clickstream/       # Raw clickstream events (Parquet)"
echo "   │       ├── clickstream_agg/   # Aggregated clickstream data (Parquet)"
echo "   │       └── iot/               # IoT sensor data (Parquet)"
echo "   └── checkpoints/"
echo "       └── streaming_etl/         # Streaming ETL job root"
echo "           ├── clickstream/       # Clickstream job state"
echo "           ├── clickstream_agg/   # Aggregation job state"
echo "           └── iot/               # IoT job state"
echo ""
echo "🎯 Benefits of Bind Mounts:"
echo "   • Data is visible in your IDE at: $(pwd)/$DATA_DIR/"
echo "   • Parquet files can be inspected directly"
echo "   • Checkpoint metadata is accessible for debugging"
echo "   • Data persists across container restarts"
echo "   • No Docker volume cleanup needed"
echo ""