package main

// import (
// 	"encoding/json"
// 	"log"
// 	"os"

// 	"github.com/IBM/sarama"
// 	"github.com/ilyaDyb/similarity_service/internal/models"
// )

// func main() {
//     kafkaBroker := os.Getenv("KAFKA_BOOTSTRAP_SERVERS")
//     topic := os.Getenv("KAFKA_TRACK_TOPIC")

//     config := sarama.NewConfig()
//     config.Producer.Return.Successes = true

//     producer, err := sarama.NewSyncProducer([]string{kafkaBroker}, config)
//     if err != nil {
//         log.Fatalf("Failed to start Sarama producer: %v", err)
//     }
//     defer producer.Close()

//     // Тестовое сообщение
//     track := models.Track{
//         ArtistID:  10,
//         Title:     "Test Track",
//         Signature: "test-signature",
//     }

//     msgBytes, err := json.Marshal(track)
//     if err != nil {
//         log.Fatalf("Failed to marshal message: %v", err)
//     }

//     msg := &sarama.ProducerMessage{
//         Topic: topic,
//         Value: sarama.ByteEncoder(msgBytes),
//     }

//     partition, offset, err := producer.SendMessage(msg)
//     if err != nil {
//         log.Fatalf("Failed to send message: %v", err)
//     }

//     log.Printf("Message sent to partition %d with offset %d", partition, offset)
// }