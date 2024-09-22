FROM golang:1.23-alpine

RUN apk update && apk add --no-cache git

WORKDIR /app

COPY go.mod go.sum ./

RUN go mod download

COPY . .

RUN go build -o main ./cmd

EXPOSE 8000

CMD ["./main"]