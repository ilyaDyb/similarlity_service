package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"
	"syscall"


	"github.com/ilyaDyb/similarity_service/config/database"
	"github.com/ilyaDyb/similarity_service/internal/models"
	"golang.org/x/term"
)

func main() {
	scanner := bufio.NewScanner(os.Stdin)

	fmt.Println("Is the database local? Y if local and N if in an isolated container:")
	if !scanner.Scan() {
		fmt.Println("Failed to read input")
		return
	}
	choice := strings.ToLower(scanner.Text())
	switch choice {
	case "y":
		database.ExtraConnect()
	case "n":
		database.Connect()
	default:
		fmt.Println("Invalid choice, exiting the program.")
		return
	}

	fmt.Println("Enter admin's username:")
	if !scanner.Scan() {
		fmt.Println("Failed to read username")
		return
	}
	username := scanner.Text()

	fmt.Println("Enter your email (may be empty):")
	if !scanner.Scan() {
		fmt.Println("Failed to read email")
		return
	}
	email := scanner.Text()

	fmt.Println("Enter password:")
	passwordBytes1, err := term.ReadPassword(int(syscall.Stdin))
	if err != nil {
		fmt.Println("\nError reading password:", err.Error())
		return
	}
	fmt.Println() 
	fmt.Println("Repeat password:")
	passwordBytes2, err := term.ReadPassword(int(syscall.Stdin))
	if err != nil {
		fmt.Println("\nError reading password:", err.Error())
		return
	}
	fmt.Println()

	password1 := string(passwordBytes1)
	password2 := string(passwordBytes2)
	if password1 != password2 {
		fmt.Println("\nError: passwords do not match")
		return
	}
	fmt.Println(username, password1, email)
	user := models.User{
		Username: username,
		Password: password1,
		Email:    email,
		IsAdmin:  true,
	}
	
	err = user.SaveUserWithHashedPassword(database.DB)
	if err != nil {
		fmt.Println("\nError creating admin user:", err.Error())
		return
	}

	fmt.Println("Admin user created successfully")
}
