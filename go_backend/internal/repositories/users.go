package repositories

import "gorm.io/gorm"

type UsersRepository struct {
	DB *gorm.DB
}

func NewUsersRepository(db *gorm.DB) *UsersRepository {
	return &UsersRepository{DB: db}
}
