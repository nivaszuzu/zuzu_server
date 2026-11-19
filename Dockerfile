FROM python:3.12-alpine
WORKDIR /app
COPY index.html server.py manifest.json icon-192.png ./
VOLUME ["/data"]
EXPOSE 8080
CMD ["python3", "server.py"]
