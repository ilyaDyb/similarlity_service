package routers

import (
	"github.com/gin-gonic/gin"
	"github.com/ilyaDyb/similarity_service/internal/handlers"
)

func SetupRouter(router *gin.Engine) {//, adminHandler *handlers.AdminHandler) {
    api := router.Group("/api")
    {
        admin := api.Group("/admin")
        {
            admin.POST("/select_artist/:id", handlers.SelectArtist)
        }
    }

}
