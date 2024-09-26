package models

import (
	"golang.org/x/crypto/bcrypt"
	"gorm.io/gorm"
)

type User struct {
	Username string `json:"username"`
	Email    string `json:"email"`
	IsAdmin  bool 	`json:"is_admin"`
	Password string `json:"-"`
}

func (u *User) CheckPassword(db *gorm.DB, password string) error {
	var hashedPassword string
	err := db.Raw(`SELECT password FROM users WHERE username = ?`, u.Username).Scan(&hashedPassword)
	if err != nil {
		return err.Error
	}
	if err := bcrypt.CompareHashAndPassword([]byte(hashedPassword), []byte(password)); err != nil {
		return err
	}
	return nil
}

func (u *User) SaveUserWithHashedPassword(db *gorm.DB) error {
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(u.Password), bcrypt.DefaultCost)
	if err != nil {
		return err
	}
    err = db.Exec("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", u.Username, u.Email, hashedPassword).Error
    if err != nil {
        return err
    }
	return nil
}
