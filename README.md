# Similarity Service

A microservice designed to analyze and compare audio files, particularly music tracks, based on their audio features. This project includes audio processing, signature generation, and comparison features to find similar tracks in a database.

## Technologies
* Python
* Go
* Flask
* Docker
* Docker Compose
* PostgreSQL
* Kafka
* NumPy
* librosa
* scipy

## Getting Started

### Installation
1. Clone the repository:
    ```
    git clone https://github.com/yourusername/similarity_service.git
    ```
2. Navigate to the project directory:
    ```
    cd similarity_service
    ```
3. Set up the Python environment:
    ```
    cd audio_processing
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
4. Set up the Go backend:
    ```
    cd go_backend
    go mod tidy
    ```

<!-- ### Running the Services
1. Start the services using Docker Compose:
    ```
    docker-compose up --build
    ```
2. Access the service at `http://localhost` once all services are running. -->

## Contributing
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.

## License
`This project is licensed under the MIT License.`