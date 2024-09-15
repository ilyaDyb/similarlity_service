package database

import (
	"log"

	"github.com/joho/godotenv"
	"gorm.io/gorm"
)

var db *gorm.DB

func init() {
	if err := godotenv.Load(); err != nil {
		log.Panic("No .env file found")
	}
}

func Connect() {
	return
}