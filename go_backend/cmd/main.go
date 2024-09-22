package main

import (
	"log"
	// "sync"

	"github.com/gin-gonic/gin"
	"github.com/ilyaDyb/similarity_service/config/database"
	ginSwagger "github.com/swaggo/gin-swagger"
	swaggerfiles "github.com/swaggo/files"
	_ "github.com/ilyaDyb/similarity_service/api"

	// "github.com/ilyaDyb/similarity_service/internal/consumer"
	// "github.com/ilyaDyb/similarity_service/internal/handlers"
	"github.com/ilyaDyb/similarity_service/internal/routers"
	// "github.com/ilyaDyb/similarity_service/internal/service"
)

// @title           Swagger REST API
// @version         1.0
// @termsOfService  http://swagger.io/terms/

// @contact.name   API Support
// @contact.url    http://www.swagger.io/support
// @contact.email  support@swagger.io

// @license.name  Apache 2.0
// @license.url   http://www.apache.org/licenses/LICENSE-2.0.html

// @host      localhost:8080
// @BasePath  /api/v1

// @securityDefinitions.basic  JWT

// @externalDocs.description  OpenAPI
// @externalDocs.url          https://swagger.io/resources/open-api/

func main() {
	database.Connect()
	// kafkaService := service.NewKafkaService()

	
	r := gin.Default()
	r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerfiles.Handler))
	// adminHandler := handlers.SelectArtist()//kafkaService)

	// kafkaConsumer := consumer.NewConsumer()
    // var wg sync.WaitGroup
    // wg.Add(1)
    // go kafkaConsumer.Start(&wg)

	routers.SetupRouter(r)
	if err := r.Run(":8000"); err != nil {
		log.Fatalf("Could not run server: %v", err)
	}
	// wg.Wait()
}