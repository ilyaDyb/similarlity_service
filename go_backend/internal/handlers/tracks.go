package handlers

import (
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/ilyaDyb/similarity_service/internal/repositories"
)

type TracksHandler struct {
	Repo *repositories.TracksRepository
}

func NewTracksHandler(repo *repositories.TracksRepository) *TracksHandler {
	return &TracksHandler{Repo: repo}
}

// @Summary Get track by id
// @Description -
// @Tags tracks
// @Produce json
// @Param Authorization header string true "With the Bearer started"
// @Param id path string true "track ID"
// @Success 200 {object} models.Track
// @Failure 500 {object} map[string]string
// @Router /tracks/{id} [get]
func (h *TracksHandler) GetTrackByIdHandler(c *gin.Context) {
	artistId := c.Param("id")

	track, err := h.Repo.GetTrackById(artistId)
	if err != nil {
		log.Println(err.Error())
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, track)
}

// @Summary Search tracks by query
// @Description -
// @Tags tracks
// @Produce json
// @Param Authorization header string true "With the Bearer started"
// @Param query query string true "query"
// @Success 200 {object} models.Track
// @Failure 500 {object} map[string]string
// @Router /tracks [get]
func (h *TracksHandler) SearchTracksHandler(c *gin.Context) {
	search := c.Query("query")

	tracks, err := h.Repo.SearchTracksByStr(search)
	if err != nil {
		log.Println(err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"tracks": tracks})
}

// @Summary  Get similar tracks by track_id
// @Description -
// @Tags tracks
// @Produce json
// @Param Authorization header string true "With the Bearer started"
// @Param id path string true "track_id"
// @Success 200 {object} models.Track
// @Failure 500 {object} map[string]string
// @Router /tracks/similar/{id} [get]
func (h *TracksHandler) GetSimilarTracksHandler(c *gin.Context) {
	id := c.Param("id")

	tracks, err := h.Repo.GetSimilarTracks(id)
	if err != nil {
		log.Println(err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"tracks": tracks})
}