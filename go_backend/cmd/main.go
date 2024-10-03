package main

import (
	"github.com/gin-gonic/gin"
	_ "github.com/ilyaDyb/similarity_service/api"
	"github.com/ilyaDyb/similarity_service/config/database"
	"github.com/ilyaDyb/similarity_service/internal/routers"
)

// @title           Swagger REST API
// @version         1.0
// @termsOfService  http://swagger.io/terms/

// @contact.name   API Support
// @contact.url    http://www.swagger.io/support
// @contact.email  support@swagger.io

// @license.name  Apache 2.0
// @license.url   http://www.apache.org/licenses/LICENSE-2.0.html

// @host      localhost:8000
// @BasePath  /api

// @securityDefinitions.basic  JWT

// @externalDocs.description  OpenAPI
// @externalDocs.url          https://swagger.io/resources/open-api/

func main() {
	database.Connect()

	r := gin.Default()
	
	routers.SetupRouter(r)
	StartApp(r)
}