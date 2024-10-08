package database

import (
	"fmt"
	"log"
	"os"

	"github.com/ilyaDyb/similarity_service/internal/models"
	"github.com/joho/godotenv"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

var DB *gorm.DB

func init() {
	if err := godotenv.Load(); err != nil {
		log.Panic("No .env file found")
	}
}

func Connect() {
	dbUser := os.Getenv("DB_USER")
	dbPassword := os.Getenv("DB_PASSWORD")
	dbHost := os.Getenv("DB_HOST")
	dbPort := os.Getenv("DB_PORT")
	dbName := os.Getenv("DB_NAME")
	dsn := fmt.Sprintf("host=%v user=%v password=%v dbname=%v port=%v sslmode=disable", dbHost, dbUser, dbPassword, dbName, dbPort)
	var err error
	DB, err = gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatalf("Error connecting to database: %v", err)
	}

	if err := DB.Exec("SET ivfflat.probes = 100").Error; err != nil {
		log.Fatalf("Error setting ivfflat probes in database: %v", err)
	}
}

func ExtraConnect() error {
	dbUser := os.Getenv("DB_USER")
	dbPassword := os.Getenv("DB_PASSWORD")
	dbHost := "localhost"
	dbPort := os.Getenv("DB_PORT")
	dbName := os.Getenv("DB_NAME")
	dsn := fmt.Sprintf("host=%v user=%v password=%v dbname=%v port=%v sslmode=disable", dbHost, dbUser, dbPassword, dbName, dbPort)
	var err error
	DB, err = gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatalf("Error connecting to database: %v", err)
		return err
	}

	if err := DB.Exec("SET ivfflat.probes = 100").Error; err != nil {
		log.Fatalf("Error setting ivfflat probes in database: %v", err)
		return err
	}
	return nil
}

func Migrate(db *gorm.DB) error {
	DB.AutoMigrate(&models.Track{}, &models.User{})
	return nil
}