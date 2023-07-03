# Chapter 2 - Create a simple web server

## Build docker image

```bash
docker build -t greeter .
```{{exec}}

## Run docker image

```bash
docker run --rm --name greeter -dp 8000:8000 greeter
```{{exec}}

## Send HTTP request

```bash
curl localhost:8000
```{{exec}}
