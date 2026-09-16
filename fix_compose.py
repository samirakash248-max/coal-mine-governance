import re

filepath = "docker-compose.yml"
with open(filepath, 'r') as f:
    content = f.read()

# Replace frontend build config
old_frontend = """  frontend:
    build:
      context: ./frontend
    ports:
      - "5173:80"
    environment:
      - VITE_API_URL=http://localhost:8002/api/v1
    depends_on:
      - backend"""

new_frontend = """  frontend:
    build:
      context: ./frontend
      args:
        - VITE_API_URL=/api/v1
    ports:
      - "5173:80"
    depends_on:
      - backend"""

content = content.replace(old_frontend, new_frontend)
with open(filepath, 'w') as f:
    f.write(content)
