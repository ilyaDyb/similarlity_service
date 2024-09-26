package routers

import (
	"github.com/gin-gonic/gin"
	"github.com/ilyaDyb/similarity_service/config/database"
	"github.com/ilyaDyb/similarity_service/internal/handlers"
	// "github.com/ilyaDyb/similarity_service/internal/middleware"
	"github.com/ilyaDyb/similarity_service/internal/repositories"
)

func SetupRouter(router *gin.Engine) {//, adminHandler *handlers.AdminHandler) {
    api := router.Group("/api")
    db := database.DB

    // ADMIN
    {
        admin := api.Group("/admin")
        {
            admin.POST("/select_artist/:id", handlers.SelectArtist)
        }
    }

    //TRACKS
    {
        tr_repo := repositories.NewTracksRepository(db)
        tr_hand := handlers.NewTracksHandler(tr_repo)
        tracks := api.Group("/tracks")
        // tracks.Use(middleware.JWTAuthMiddleware())
        {
            tracks.GET("/:id", tr_hand.GetTrackByIdHandler)
            tracks.GET("/", tr_hand.SearchTracksHandler)
            tracks.GET("/similar/:id", tr_hand.GetSimilarTracksHandler)
        }
    }    
}
