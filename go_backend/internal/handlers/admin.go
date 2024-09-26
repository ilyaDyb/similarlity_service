package handlers

import (
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	// "github.com/ilyaDyb/similarity_service/internal/service"
)

// type AdminHandler struct {
//     KafkaService *service.KafkaService
// }

// func NewAdminHandler() *AdminHandler {//kafkaService *service.KafkaService) *AdminHandler {
//     return &AdminHandler{}//KafkaService: kafkaService}
// }

// SelectArtist godoc
// @Summary Select Artist by ID
// @Description Select an artist by their ID and process it via Redis
// @Tags admin
// @Accept json
// @Produce json
// @Param id path int true "Artist ID"
// @Success 200 {object} string
// @Failure 400 {object} string
// @Failure 500 {object} string
// @Router /select_artist/{id} [post]
func SelectArtist(c *gin.Context) {//func (h *AdminHandler) SelectArtist(c *gin.Context) {
    artistID := c.Param("id")

    message := map[string]string{"artist_id": artistID}
    // err := h.KafkaService.Produce(message)
    // if err != nil {
    //     c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to send message to Kafka"})
    //     return
    // }
    log.Println(message)
    c.JSON(http.StatusOK, gin.H{"status": "Artist ID sent to processing"})
}

type loadTracksInput struct {
    ArtistId string `json:"artist_id"`
}

func LoadTracksFromArtist(c *gin.Context) {
    var input loadTracksInput

    err := c.ShouldBindJSON(&input)
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": err})
        return
    }
    
}