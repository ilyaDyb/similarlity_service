package pythonintegration

import (
	"fmt"
	"log"
	a "github.com/hibiken/asynq"
	"github.com/ilyaDyb/similarity_service/config/asynq"
)

func  InstallTracksByArtist(artistId string) error {
	task := a.NewTask("python:install_by_artist", []byte(artistId))
	_, err := asynq.Client.Enqueue(task)
	if err != nil {
		return fmt.Errorf("failed to enqueue task: %s", err.Error())
	}
	log.Println("Task enqueued for artist:", artistId)
    return nil
}

func InstallTracksByAlbum(artistId string) error {
	task := a.NewTask("python:install_by_album", []byte(artistId))
	_, err := asynq.Client.Enqueue(task)
	if err != nil {
		return fmt.Errorf("failed to enqueue task: %s", err.Error())
	}
	log.Println("Task enqueued for artist:", artistId)
    return nil
}

func  TestRequest() error {
	task := a.NewTask("python:ping", []byte{})
	_, err := asynq.Client.Enqueue(task)
	if err != nil {
		return fmt.Errorf("failed to enqueue task: %s", err.Error())
	}
	log.Println("Test task enqueued")
	return nil
}