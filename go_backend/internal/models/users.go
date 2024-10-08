package models

import (
	"errors"

	"golang.org/x/crypto/bcrypt"
	"gorm.io/gorm"
)

type User struct {
	Id 		 int 	`json:"id"`
	Username string `json:"username"`
	Email    string `json:"email"`
	IsAdmin  bool 	`json:"is_admin"`
	Password string `json:"-"`
}

func (u *User) CheckPassword(db *gorm.DB) (*User, error) {
	var user User
	err := db.Where("username = ?", u.Username).First(&user).Error
	if err != nil {
		return nil, errors.New("invalid username or password")
	}
	if err := bcrypt.CompareHashAndPassword([]byte(user.Password), []byte(u.Password)); err != nil {
		return nil, errors.New("invalid username or password")
	}
	return &user, nil
}

func (u *User) SaveUserWithHashedPassword(db *gorm.DB) error {
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(u.Password), bcrypt.DefaultCost)
	if err != nil {
		return err
	}
	if !u.IsAdmin {
		err = db.Exec("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", u.Username, u.Email, hashedPassword).Error
	} else {
		err = db.Exec("INSERT INTO users (username, email, password, is_admin) VALUES (?, ?, ?, ?)", u.Username, u.Email, hashedPassword, u.IsAdmin).Error
	}
    if err != nil {
        return err
    }
	return nil
}
