package tasks

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/hibiken/asynq"
)

type PythonService struct {
	apiBaseUrl string
	client     *http.Client
}

func NewPythonService() *PythonService {
	return &PythonService{
		apiBaseUrl: os.Getenv("PYTHON_APP_URL"),
		client: &http.Client{Timeout: time.Second * 10},
	}
}

func (s *PythonService) InstallTracksByArtistHandler(ctx context.Context, task *asynq.Task) error {
	var artistId string
	if err := json.Unmarshal(task.Payload(), &artistId); err != nil {
		return err
	}

	type installTracksRequest struct {
		Id string `json:"artist_id"`
	}

	requestBody, err := json.Marshal(installTracksRequest{Id: artistId})
	if err != nil {
		return fmt.Errorf("failed to marshal request: %s", err.Error())
	}

	url := fmt.Sprintf("%s/install/artist", s.apiBaseUrl)
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(requestBody))
	if err != nil {
		return fmt.Errorf("failed to create request: %s", err.Error())
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := s.client.Do(req)
	if err != nil {
		return fmt.Errorf("failed to send request: %s", err.Error())
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusAccepted {
		return fmt.Errorf("API responded with status: %d", resp.StatusCode)
	}

	log.Println("Successfully installed tracks for album:", artistId)
	return nil
}

func (s *PythonService) InstallTracksByAlbumHandler(ctx context.Context, task *asynq.Task) error {
	var albumId string
	if err := json.Unmarshal(task.Payload(), &albumId); err != nil {
		return err
	}

	type installTracksRequest struct {
		Id string `json:"album_id"`
	}

	requestBody, err := json.Marshal(installTracksRequest{Id: albumId})
	if err != nil {
		return fmt.Errorf("failed to marshal request: %s", err.Error())
	}

	url := fmt.Sprintf("%s/install/album", s.apiBaseUrl)
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(requestBody))
	if err != nil {
		return fmt.Errorf("failed to create request: %s", err.Error())
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := s.client.Do(req)
	if err != nil {
		return fmt.Errorf("failed to send request: %s", err.Error())
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusAccepted {
		return fmt.Errorf("API responded with status: %d", resp.StatusCode)
	}

	log.Println("Successfully installed tracks for album:", albumId)
	return nil
}

func (s *PythonService) TestRequest(ctx context.Context, task *asynq.Task) error {
	resp, err := http.Get(fmt.Sprintf("%s/ping", s.apiBaseUrl))
	if err != nil {
		return err
	}
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return err
	}
	log.Println(string(body))
	return nil
}