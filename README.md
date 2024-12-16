# Receipt Processor
This is a programming solution for Fetch's receipt processor challenge from https://github.com/fetch-rewards/receipt-processor-challenge.

## Design
The solution uses Python's Fast API web framework on python 3.12.  I'm most comrfortable with the python programming language, and Fast API is a the de facto web framework for Python.  The python application is built into a Docker image based on AWS's amazonlinux:2023, which is a typical choice for services that may be deployed on AWS.  

## Implementation and Assumptions

- Fast API has some out of the box validation that needed to be disabled to meet the error handling specifications of the api.yml.
- No fastapi code generator from swagger: I tried the code generator and wasn't happy with the results, so I built the endpoints myself.  The Swagger UI doesn't match 100% exactly the output of the api.yml in Swagger UI.
- Basic logging implemented
- Ping endpoint instead of readiness/liveness endpoints
- No HTTPS or Proxy: I assume basic HTTP and no specialized web server is needed for an example like this, and that in production the SSL termination would happen upstream and it would be attached to a full web server with configurations tuned for performance.

## Build the project

Build the image using 2 step process
```
docker build -f Dockerfile.builder -t receipt-processor-builder:latest .

docker build -f Dockerfile -t receipt-processor:latest .
```

## Run Container and Test Application

Run the Docker image as a container, expose port 80, and map to system port 80
```
docker run -d -p 80:80 --name receiptprocessor receipt-processor:latest
```

Check the ping endpoint that the container is up
```
curl http://localhost/ping
```

Submit a receipt (the Target example)
```
curl -s --header "Content-Type: application/json" --request POST --data '{"retailer":"Target","purchaseDate":"2022-01-01","purchaseTime":"13:01","items":[{"shortDescription":"Mountain Dew 12PK","price":"6.49"},{"shortDescription":"Emils Cheese Pizza","price":"12.25"},{"shortDescription":"Knorr Creamy Chicken","price":"1.26"},{"shortDescription":"Doritos Nacho Cheese","price":"3.35"},{"shortDescription":"   Klarbrunn 12-PK 12 FL OZ  ","price":"12.00"}],"total":"35.35"}' http://localhost:80/receipts/process
```

A response like the following should be returned:
```
{"id":"a0aedcec-f384-482a-a4df-b4ff55c79568"}
```

Using the "id" from above respnse, call the GET points endpoint
```
 curl http://localhost:80/receipts/{ID_FROM_PREVIOUS_STEP}/points
 ```

 Which should return a response containing the points
 ```
 {"points":28}
 ```


Check logs for debugging
```
docker logs receiptprocessor
```

Cleanup docker container when complete
```
docker stop receiptprocessor

docker rm receiptprocessor
```







