package pythonintegration

import (
	"encoding/json"
	"fmt"
	"log"

	a "github.com/hibiken/asynq"
	"github.com/ilyaDyb/similarity_service/config/asynq"
)

func  InstallTracksByArtist(artistId string) error {
	payload, err := json.Marshal(map[string]string{"artist_id": artistId})
	if err != nil {
		return fmt.Errorf("failed to marshal payload: %s", err.Error())
	}
	task := a.NewTask("python:install_by_artist", payload, a.MaxRetry(0))
	_, err = asynq.Client.Enqueue(task)
	if err != nil {
		return fmt.Errorf("failed to enqueue task: %s", err.Error())
	}
	log.Println("Task enqueued for artist:", artistId)
    return nil
}

func InstallTracksByAlbum(artistId string) error {
	payload, err := json.Marshal(map[string]string{"album_id": artistId})
	if err != nil {
		return fmt.Errorf("failed to marshal payload: %s", err.Error())
	}
	task := a.NewTask("python:install_by_album", payload, a.MaxRetry(0))
	_, err = asynq.Client.Enqueue(task)
	if err != nil {
		return fmt.Errorf("failed to enqueue task: %s", err.Error())
	}
	log.Println("Task enqueued for artist:", artistId)
    return nil
}

func SetSignatures() error {
	task := a.NewTask("python:set_signatures", []byte{})
	_, err := asynq.Client.Enqueue(task)
	if err != nil {
		return fmt.Errorf("failed to enqueue task: %s", err.Error())
	}
	log.Println("Task enqueued: set_signatures")
	return nil
}

func TestRequest() error {
	task := a.NewTask("python:ping", []byte{})
	_, err := asynq.Client.Enqueue(task)
	if err != nil {
		return fmt.Errorf("failed to enqueue task: %s", err.Error())
	}
	log.Println("Test task enqueued")
	return nil
}