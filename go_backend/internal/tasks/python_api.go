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
		client: &http.Client{Timeout: time.Minute * 2},
	}
}

func (s *PythonService) InstallTracksByArtistHandler(ctx context.Context, task *asynq.Task) error {
	log.Println("InstallTracksByArtistHandler: received task")
	var input struct {
		ArtistId string `json:"artist_id"`
	}

	if err := json.Unmarshal(task.Payload(), &input); err != nil {
		log.Println(err.Error())
		return err
	}

	type installTracksRequest struct {
		Id string `json:"artist_id"`
	}

	requestBody, err := json.Marshal(installTracksRequest{Id: input.ArtistId})
	if err != nil {
		log.Println(err.Error())
		return fmt.Errorf("failed to marshal request: %s", err.Error())
	}

	url := fmt.Sprintf("%s/install/artist", s.apiBaseUrl)
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(requestBody))
	if err != nil {
		log.Println(err.Error())
		return fmt.Errorf("failed to create request: %s", err.Error())
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := s.client.Do(req)
	if err != nil {
		log.Println(err.Error())
		return fmt.Errorf("failed to send request: %s", err.Error())
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != http.StatusOK {
		log.Printf("Error: received non-OK status code %d from Python API\n", resp.StatusCode)
		return fmt.Errorf("API responded with status code %d", resp.StatusCode)
	}

	log.Println("Successfully installed tracks for album:", input.ArtistId)
	return nil
}


func (s *PythonService) InstallTracksByAlbumHandler(ctx context.Context, task *asynq.Task) error {
	log.Println("InstallTracksByAlbumHandler: received task")
	var input struct {
		AlbumId string `json:"album_id"`
	}

	if err := json.Unmarshal(task.Payload(), &input); err != nil {
		log.Println(err.Error())
		return err
	}

	type installTracksRequest struct {
		Id string `json:"album_id"`
	}

	requestBody, err := json.Marshal(installTracksRequest{Id: input.AlbumId})
	if err != nil {
		log.Println(err.Error())
		return fmt.Errorf("failed to marshal request: %s", err.Error())
	}

	url := fmt.Sprintf("%s/install/album", s.apiBaseUrl)
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(requestBody))
	if err != nil {
		log.Println(err.Error())
		return fmt.Errorf("failed to create request: %s", err.Error())
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := s.client.Do(req)
	if err != nil {
		log.Println(err.Error())
		return fmt.Errorf("failed to send request: %s", err.Error())
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != http.StatusOK {
		log.Printf("Error: received non-OK status code %d from Python API\n", resp.StatusCode)
		return fmt.Errorf("API responded with status code %d", resp.StatusCode)
	}

	log.Println("Successfully installed tracks for album:", input.AlbumId)
	return nil
}

func (s *PythonService) SetSignatures(ctx context.Context, task *asynq.Task) error {
	resp, err := http.Post(fmt.Sprintf("%s/signatures/set", s.apiBaseUrl), "application/json", bytes.NewBuffer([]byte{}))
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		log.Printf("error: received non-OK status code %d from Python API\n", resp.StatusCode)
		return err
	}

	log.Println("Successfully signatures was set")
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