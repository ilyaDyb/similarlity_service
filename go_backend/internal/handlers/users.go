package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/ilyaDyb/similarity_service/internal/auth"
	"github.com/ilyaDyb/similarity_service/internal/models"
	"github.com/ilyaDyb/similarity_service/internal/repositories"
	"github.com/ilyaDyb/similarity_service/internal/utils"
)

type UsersHanlder struct {
	Repo *repositories.UsersRepository
}

func NewUsersHandler(repo *repositories.UsersRepository) *UsersHanlder {
	return &UsersHanlder{Repo: repo}
}

type RegisterInput struct {
	Username string `json:"username"`
	Email    string `json:"email"`
	Password string `json:"password"`
}

// @Summary Register a new user
// @Description -
// @Tags auth
// @Accept json
// @Produce json
// @Param RegisterInput body RegisterInput true "Register Input"
// @Success 200 {object} map[string]string
// @Failure 400 {object} map[string]string
// @Failure 500 {object} map[string]string
// @Router /auth/register [POST]
func (r *UsersHanlder) RegisterHandler(c *gin.Context) {
	var registerInput RegisterInput

	if err := c.ShouldBindBodyWithJSON(&registerInput); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := utils.PasswordIsValid(registerInput.Password); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := utils.EmailIsValid(registerInput.Email); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := utils.UsernameEmailIsUnique(registerInput.Username, registerInput.Email); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	user := models.User{
		Username: registerInput.Username,
		Email:    registerInput.Email,
		Password: registerInput.Password,
		IsAdmin:  false,
	}

	if err := user.SaveUserWithHashedPassword(r.Repo.DB); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, user)
}

type LoginInput struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

// @Summary Login user
// @Description -
// @Tags auth
// @Accept json
// @Produce json
// @Param LoginInput body LoginInput true "Login input"
// @Success 200 {object} map[string]string
// @Failure 400 {object} map[string]string
// @Failure 401 {object} map[string]string
// @Failure 500 {object} map[string]string
// @Router /auth/login [POST]
func (r *UsersHanlder) LoginHandler(c *gin.Context) {
	var loginInput LoginInput
	if err := c.ShouldBindJSON(&loginInput); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	u := models.User{
		Username: loginInput.Username,
		Password: loginInput.Password,
	}

	user, err := u.CheckPassword(r.Repo.DB)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}

	accessToken, err := auth.GenerateJWT(user.Id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	refreshToken, err := auth.GenerateRefresh(user.Id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"access_token":  accessToken,
		"refresh_token": refreshToken,
	})
}

type InputRefresh struct {
	RefreshToken string `json:"refresh_token"`
}

// @Summary Refreshing access Token
// @Tags    auth
// @Accept  json
// @Produce json
// @Param   InputRefresh body InputRefresh true "InputRefresh"
// @Success 200 {object} map[string]string
// @Success 401 {object} map[string]string
// @Success 500 {object} map[string]string
// @Router  /auth/refresh [POST]
func (r *UsersHanlder) RefreshHandler(c *gin.Context) {
	var inputRefresh InputRefresh
	if err := c.ShouldBindJSON(&inputRefresh); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	claims, err := auth.ParseJWT(inputRefresh.RefreshToken)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid refresh token"})
		return
	}
	newToken, err := auth.GenerateJWT(claims.UserId)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"access_token": newToken})
}