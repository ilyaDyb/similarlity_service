package main

import (
	"log"

	"github.com/gin-gonic/gin"
	"github.com/ilyaDyb/similarity_service/config/asynq"
)

func StartApp(r *gin.Engine) {
	go func() {
		if err := r.Run(":8000"); err != nil {
			log.Fatalf("Could not run server: %s", err.Error())
		}
	}()

	if err := asynq.StartAsynq(); err != nil {
		log.Fatalf("Could not run asynq server: %s", err.Error())
	}
	
}