FROM apache/spark:3.5.1-scala2.12-java11-python3-ubuntu

# Switch to root to install dependencies
USER root

# Install PyYAML for configuration loading
RUN pip install PyYAML==6.0.1

# Create necessary directories
RUN mkdir -p /opt/spark/work-dir /opt/spark/logs

# Set proper permissions
RUN chown -R spark:spark /opt/spark

# Switch back to spark user
USER spark

# Set SPARK_HOME environment variable
ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
