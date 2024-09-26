package handlers

import (
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/ilyaDyb/similarity_service/internal/repositories"
)

type TracksHandler struct {
	tracksRepo *repositories.TracksRepository
}

func NewTracksHandler(tracksRepo *repositories.TracksRepository) *TracksHandler {
	return &TracksHandler{tracksRepo: tracksRepo}
}

// @Summary Get track by id
// @Description -
// @Tags tracks
// @Produce json
// @Param id path string true "track ID"
// @Success 200 {object} models.Track
// @Failure 500 {object} map[string]string
// @Router /tracks/{id} [get]
func (h *TracksHandler) GetTrackByIdHandler(c *gin.Context) {
	artistId := c.Param("id")

	track, err := h.tracksRepo.GetTrackById(artistId)
	if err != nil {
		log.Println(err.Error())
		c.JSON(http.StatusInternalServerError, gin.H{"error": err})
		return
	}

	c.JSON(http.StatusOK, track)
}

// @Summary Search tracks by query
// @Description -
// @Tags tracks
// @Produce json
// @Param query query string true "query"
// @Success 200 {object} models.Track
// @Failure 500 {object} map[string]string
// @Router /tracks [get]
func (h *TracksHandler) SearchTracksHandler(c *gin.Context) {
	search := c.Query("query")

	tracks, err := h.tracksRepo.SearchTracksByStr(search)
	if err != nil {
		log.Println(err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": err})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{"tracks": tracks})
}

// @Summary  Get similar tracks by track_id
// @Description -
// @Tags tracks
// @Produce json
// @Param id path string true "track_id"
// @Success 200 {object} models.Track
// @Failure 500 {object} map[string]string
// @Router /tracks/similar/{id} [get]
func (h *TracksHandler) GetSimilarTracksHandler(c *gin.Context) {
	id := c.Param("id")

	tracks, err := h.tracksRepo.GetSimilarTracks(id)
	if err != nil {
		log.Println(err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": err})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{"tracks": tracks})
}