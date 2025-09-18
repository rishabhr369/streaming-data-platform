# 🚀 Streaming Data Platform

A **production-ready containerized data engineering platform** featuring Apache Kafka, Apache Spark, and high-performance data generation for real-time stream processing, analytics, and data science experimentation.

## 🎯 What Makes This Special

- 🔥 **High-Performance Data Generator** with multi-threading and 4x throughput optimization
- 📊 **Built-in Data Analytics Platform** with Jupyter notebooks and comprehensive analysis
- 💾 **Production Data Lake** with structured data processing and partitioning
- 🛠️ **YAML-Based Configuration** for easy management across environments
- 🔄 **Real-time Stream Processing** with fault tolerance and checkpointing
- 📈 **Live Data Analytics** with actual processed data ready for exploration

## ⚡ Quick Start

```bash
# 1. Setup configuration
make setup

# 2. Start the platform
make up

# 3. Open analytics
jupyter notebook datalake_analysis.ipynb
```

**Access Points:**
- 🖥️ Kafka UI: http://localhost:8080
- ⚡ Spark UI: http://localhost:8081  
- 📊 Data Analytics: `jupyter notebook datalake_analysis.ipynb`

## 🏗️ Architecture Overview

📊 **[View Complete System Architecture →](./architecture.md)**

The platform features interactive Mermaid diagrams showing:
- Component interactions and data flow
- Network topology and service connectivity  
- Technology stack and performance specifications

```
Data Generator → Kafka Cluster → Spark ETL → Data Lake → Analytics
     ↓              ↓             ↓          ↓         ↓
Multi-threaded   3-node KRaft   Streaming   Parquet   Jupyter
200+ events/sec  High-Avail.    Real-time   Partitioned  Interactive
```

## 🛠️ Key Features

### **High-Performance Data Generation**
- Multi-threaded producer with 200+ events/sec throughput
- LZ4 compression and batch processing optimization
- Real-time performance monitoring and graceful shutdown

### **Production Data Stack**
- **Apache Kafka 3.7**: 3-node KRaft cluster with external access
- **Apache Spark 3.5.1**: Custom containers with streaming ETL
- **Data Lake**: Parquet format with date partitioning
- **Analytics**: Jupyter notebooks with pandas, matplotlib, seaborn

### **Enterprise Configuration**
- YAML-based central configuration (`config.yml`)
- Environment variable auto-generation
- Fallback systems and validation

## 📖 Documentation

- 📊 **[Architecture Diagrams](./architecture.md)** - Complete system design with Mermaid diagrams
- 📚 **[Detailed Documentation](./DETAILED_README.md)** - Comprehensive setup, configuration, and troubleshooting
- ⚙️ **[Configuration Guide](./DETAILED_README.md#configuration-changes)** - Advanced configuration options
- 🔧 **[Troubleshooting](./DETAILED_README.md#troubleshooting)** - Common issues and solutions

## 🎯 Perfect For

- **Data Engineers** learning stream processing technologies
- **Developers** prototyping real-time analytics solutions  
- **Students** studying modern data architecture patterns
- **Teams** needing reference implementations for production deployments
- **Organizations** evaluating Kafka and Spark infrastructure

## 🚀 Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Streaming** | Apache Kafka 3.7 | Event streaming platform |
| **Processing** | Apache Spark 3.5.1 | Real-time data processing |
| **Storage** | Parquet, Local filesystem | Columnar data storage |
| **Analytics** | Jupyter, Pandas, Matplotlib | Interactive data analysis |
| **Orchestration** | Docker Compose | Service management |
| **Configuration** | YAML, Python | Centralized configuration |

## 📊 Quick Commands

```bash
make setup          # Interactive setup with dependencies
make up              # Start all services  
make logs            # View service logs
make data-stats      # Show data volume statistics
make clean-data      # Clean all data (interactive)
make down            # Stop services
```

## 🤝 Contributing

We welcome contributions! Please see our [detailed documentation](./DETAILED_README.md) for:
- Development setup and guidelines
- Architecture deep-dive and component details
- Configuration management and customization
- Troubleshooting and debugging guides

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

⭐ **Star this repository** if you find it useful for learning data engineering or building streaming applications!