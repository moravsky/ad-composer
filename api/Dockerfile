FROM node:20-slim

# Add non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies including openai
RUN npm install

# Copy application files
COPY . .

# Set proper permissions
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

EXPOSE 3000
CMD ["node", "app.js"]