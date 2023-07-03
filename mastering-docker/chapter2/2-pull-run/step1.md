# Chapter 2 - Run Nginx web server in Docker

## Pull the image

```bash
docker pull nginx:1.25-alpine
```{{exec}}

## Run the image

```bash
docker run --rm --name nginx -dp 8000:80 nginx:1.25-alpine
```{{exec}}

## Send HTTP request

```bash
curl localhost:8000
```{{exec}}
