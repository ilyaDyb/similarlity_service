package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/ilyaDyb/similarity_service/internal/repositories"
	pythonintegration "github.com/ilyaDyb/similarity_service/internal/service/python_integration"
	// "github.com/ilyaDyb/similarity_service/internal/service"
)

type AdminHandler struct {
	Repo *repositories.AdminRepo
}

func NewAdminHandler(repo *repositories.AdminRepo) *AdminHandler {
	return &AdminHandler{Repo: repo}
}

type loadTracksByAlbum struct {
	AlbumId string `json:"album_id"`
}
// @Summary load tracks by album
// @Description -
// @Tags admin
// @Produce json
// @Param AlbumId body loadTracksByAlbum true "album_id"
// @Success 202 {object} int
// @Failure 400 {object} map[string]string
// @Failure 403 {object} map[string]string
// @Failure 500 {object} map[string]string
// @Router /admin/load-album [post]
func (h *AdminHandler) LoadTracksByAlbumHandler(c *gin.Context) {
	// currentUsrId := c.MustGet("user_id").(string)
	// isAdmin, err := h.Repo.CheckAdminRole(currentUsrId)
	// if err != nil || !isAdmin {
	// 	c.JSON(http.StatusForbidden, gin.H{"error": err.Error()})
	// 	return
	// }

	var input loadTracksByAlbum
	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err})
		return
	}

	err := pythonintegration.InstallTracksByAlbum(input.AlbumId)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.Status(http.StatusAccepted)
}

type loadTracksByArtist struct {
	ArtistId string `json:"artist_id"`
}
// @Summary load tracks by album
// @Description -
// @Tags admin
// @Produce json
// @Param ArtistId body loadTracksByArtist true "artist_id"
// @Success 202 {object} int
// @Failure 400 {object} map[string]string
// @Failure 403 {object} map[string]string
// @Failure 500 {object} map[string]string
// @Router /admin/load-artist [post]
func (h *AdminHandler) LoadTracksByArtistHandler(c *gin.Context) {
	// currentUsrId := c.MustGet("user_id").(string)
	// isAdmin, err := h.Repo.CheckAdminRole(currentUsrId)
	// if err != nil || !isAdmin {
	// 	c.JSON(http.StatusForbidden, gin.H{"error": err.Error()})
	// 	return
	// }

	var input loadTracksByArtist
	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err})
		return
	}

	err := pythonintegration.InstallTracksByArtist(input.ArtistId)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.Status(http.StatusAccepted)
}

// @Summary setting signatures
// @Description load all audios without signatures and set it
// @Tags admin
// @Produce json
// @Success 202 {object} int
// @Failure 400 {object} map[string]string
// @Failure 403 {object} map[string]string
// @Failure 500 {object} map[string]string
// @Router /admin/set-signatures [post]
func (h *AdminHandler) SetSignaturesHandler(c *gin.Context) {
	err := pythonintegration.SetSignatures()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.Status(http.StatusAccepted)
}

func (h *AdminHandler) TestRequest(c *gin.Context) {
	err := pythonintegration.TestRequest()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.Status(http.StatusAccepted)
}
