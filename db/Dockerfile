FROM postgres:16

# Install Python and required packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# RUN pip3 install psycopg2-binary --break-system-packages

# Set environment variable to indicate Python is available
ENV PYTHON_AVAILABLE=true

# Copy our custom entrypoint wrapper
COPY db-entrypoint.sh /usr/local/bin/
COPY init/data/requirements.txt /requirements.txt
RUN chmod +x /usr/local/bin/db-entrypoint.sh
RUN pip install -r /requirements.txt --break-system-packages

# Keep the default entrypoint but override the command
ENTRYPOINT ["db-entrypoint.sh"]
CMD ["postgres"]