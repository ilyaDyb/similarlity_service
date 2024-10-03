package utils

import (
	"errors"
	"regexp"
	"unicode"

	"github.com/ilyaDyb/similarity_service/config/database"
)

func PasswordIsValid(password string) error {
	if (len(password) < 8) {
		return errors.New("Password is too short")
	}

	var hasUpper bool
	// var hasSpecial bool
	var digitCount int

	for _, char := range password {
		switch {
		case unicode.IsUpper(char):
			hasUpper = true
		case unicode.IsDigit(char):
			digitCount++
		// case unicode.IsPunct(char) || unicode.IsSymbol(char):
		// 	hasSpecial = true
		}
	}

	if !hasUpper {
		return errors.New("The password must contain at least one capital letter")
	}

	if digitCount < 3 {
		return errors.New("The password must contain at least three digits")
	}

	return nil
}

func EmailIsValid(email string) error {
	var re = regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	if !re.MatchString(email) {
		return errors.New("Email format is not correct")
	}
	return nil
}

func UsernameEmailIsUnique(username, email string) error {
	query := `SELECT EXISTS (SELECT 1 FROM users WHERE username = ? OR email = ?)`
	var exists bool
	err := database.DB.Raw(query, username, email).Scan(&exists).Error
	if err != nil {
		return err
	}
	if exists {
		return errors.New("A user with that username or email already exists")
	}
	return nil
}