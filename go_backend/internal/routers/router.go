package routers

import (
    swaggerfiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"
	"github.com/gin-gonic/gin"
	"github.com/ilyaDyb/similarity_service/config/database"
	"github.com/ilyaDyb/similarity_service/internal/handlers"
	"github.com/ilyaDyb/similarity_service/internal/middleware"
	"github.com/ilyaDyb/similarity_service/internal/repositories"
)

func SetupRouter(router *gin.Engine) {//, adminHandler *handlers.AdminHandler) {
    api := router.Group("/api")
    db := database.DB

    router.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerfiles.Handler))

    // ADMIN
    {
        admin := api.Group("/admin")
        admin.Use(middleware.JWTAuthMiddleware())
        {

        }
    }

    // TRACKS
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

    // AUTH
    {
        auth_repo := repositories.NewUsersRepository(db)
        auth_hand := handlers.NewUsersHandler(auth_repo)
        auth := api.Group("/auth")
        {
            auth.POST("/register", auth_hand.RegisterHandler)
            auth.POST("/login", auth_hand.LoginHandler)
            auth.POST("/refresh", auth_hand.RefreshHandler)
        }
    }
}
