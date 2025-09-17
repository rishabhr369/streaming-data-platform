#!/usr/bin/env python3
"""
Configuration loader for the Mini Cluster Setup
Loads configuration from config.yml and provides utilities for environment variable export
"""

import yaml
import os
import sys
from pathlib import Path


class ConfigLoader:
    def __init__(self, config_path="config.yml"):
        """Initialize configuration loader with path to YAML config file"""
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def get(self, key_path, default=None):
        """
        Get configuration value using dot notation
        Example: get('kafka.partitions') returns config['kafka']['partitions']
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_kafka_config(self):
        """Get all Kafka-related configuration"""
        return self.config.get('kafka', {})
    
    def get_spark_config(self):
        """Get all Spark-related configuration"""
        return self.config.get('spark', {})
    
    def get_generator_config(self):
        """Get all data generator configuration"""
        return self.config.get('data_generator', {})
    
    def to_env_vars(self):
        """
        Convert configuration to environment variables format
        Returns dictionary of environment variable names to values
        """
        env_vars = {}
        
        # Kafka configuration
        kafka = self.config.get('kafka', {})
        env_vars['KAFKA_KRAFT_CLUSTER_ID'] = kafka.get('kraft_cluster_id', '')
        env_vars['KAFKA_PARTITIONS'] = str(kafka.get('partitions', 6))
        env_vars['KAFKA_REPLICATION_FACTOR'] = str(kafka.get('replication_factor', 3))
        env_vars['KAFKA_MIN_INSYNC'] = str(kafka.get('min_insync_replicas', 2))
        
        # Kafka external ports
        external_ports = kafka.get('external_ports', {})
        env_vars['KAFKA_1_EXTERNAL'] = str(external_ports.get('broker_1', 19092))
        env_vars['KAFKA_2_EXTERNAL'] = str(external_ports.get('broker_2', 29092))
        env_vars['KAFKA_3_EXTERNAL'] = str(external_ports.get('broker_3', 39092))
        
        # Spark configuration
        spark = self.config.get('spark', {})
        env_vars['SPARK_WORKER_MEMORY'] = spark.get('worker_memory', '2g')
        env_vars['SPARK_WORKER_CORES'] = str(spark.get('worker_cores', 2))
        
        # Data generator configuration
        generator = self.config.get('data_generator', {})
        eps = generator.get('events_per_second', {})
        env_vars['EVENTS_PER_SEC_CLICK'] = str(eps.get('clickstream', 50))
        env_vars['EVENTS_PER_SEC_IOT'] = str(eps.get('iot', 30))
        
        return env_vars
    
    def export_to_env_file(self, output_path=".env"):
        """
        Export configuration to .env file format
        """
        env_vars = self.to_env_vars()
        
        with open(output_path, 'w') as f:
            f.write("# Auto-generated from config.yml - DO NOT EDIT MANUALLY\n")
            f.write("# Edit config.yml instead and regenerate this file\n\n")
            
            # Group related variables
            f.write("# ===== Kafka =====\n")
            for key in ['KAFKA_KRAFT_CLUSTER_ID', 'KAFKA_PARTITIONS', 'KAFKA_REPLICATION_FACTOR', 'KAFKA_MIN_INSYNC']:
                if key in env_vars:
                    f.write(f"{key}={env_vars[key]}\n")
            
            f.write("\n# Host-exposed ports for each broker\n")
            for key in ['KAFKA_1_EXTERNAL', 'KAFKA_2_EXTERNAL', 'KAFKA_3_EXTERNAL']:
                if key in env_vars:
                    f.write(f"{key}={env_vars[key]}\n")
            
            f.write("\n# ===== Spark =====\n")
            for key in ['SPARK_WORKER_MEMORY', 'SPARK_WORKER_CORES']:
                if key in env_vars:
                    f.write(f"{key}={env_vars[key]}\n")
            
            f.write("\n# ===== Generator =====\n")
            for key in ['EVENTS_PER_SEC_CLICK', 'EVENTS_PER_SEC_IOT']:
                if key in env_vars:
                    f.write(f"{key}={env_vars[key]}\n")
    
    def export_to_shell(self):
        """
        Export configuration as shell export statements
        """
        env_vars = self.to_env_vars()
        commands = []
        
        for key, value in env_vars.items():
            commands.append(f"export {key}={value}")
        
        return "\n".join(commands)


def main():
    """CLI interface for config loader"""
    if len(sys.argv) < 2:
        print("Usage: python config_loader.py <command>")
        print("Commands:")
        print("  generate-env    - Generate .env file from config.yml")
        print("  export-shell    - Print shell export commands")
        print("  get <key>       - Get specific config value")
        return
    
    try:
        config = ConfigLoader()
        command = sys.argv[1]
        
        if command == "generate-env":
            config.export_to_env_file()
            print("Generated .env file from config.yml")
        
        elif command == "export-shell":
            print(config.export_to_shell())
        
        elif command == "get" and len(sys.argv) > 2:
            key = sys.argv[2]
            value = config.get(key)
            print(value if value is not None else "")
        
        else:
            print(f"Unknown command: {command}")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
