FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y git pip