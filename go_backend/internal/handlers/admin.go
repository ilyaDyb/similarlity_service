package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/ilyaDyb/similarity_service/internal/repositories"
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

func (h *AdminHandler) LoadTracksByAlbum(c *gin.Context) {
	currentUsrId := c.MustGet("user_id").(string)
	isAdmin, err := h.Repo.CheckAdminRole(currentUsrId)
	if err != nil || !isAdmin {
		c.JSON(http.StatusForbidden, gin.H{"error": err.Error()})
		return
	}

	var input loadTracksByAlbum
	if err := c.ShouldBindJSON(&input).Error; err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err})
		return
	}

}