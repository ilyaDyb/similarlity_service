package asynq

import (
	"os"
	"time"

	"github.com/hibiken/asynq"
	"github.com/ilyaDyb/similarity_service/internal/tasks"
)

var (
	Client *asynq.Client
	RedisAddr string
)

func init() {
	RedisAddr = os.Getenv("REDIS_ADDR")
	Client = asynq.NewClient(asynq.RedisClientOpt{Addr: RedisAddr})
}

func StartAsynq() error {
	srv := asynq.NewServer(
		asynq.RedisClientOpt{Addr: RedisAddr},
		asynq.Config{
			Concurrency: 10,
			Queues: map[string]int{
				"default": 6,
				"critical": 3,
				"low": 1,
			},
			RetryDelayFunc: func(n int, e error, t *asynq.Task) time.Duration {return 0},
		},
	)

	mux := asynq.NewServeMux()
	pythonService := tasks.NewPythonService()
	mux.HandleFunc("python:install_by_artist", pythonService.InstallTracksByArtistHandler)
	mux.HandleFunc("python:install_by_album", pythonService.InstallTracksByAlbumHandler)
	mux.HandleFunc("python:set_signatures", pythonService.SetSignatures)
	mux.HandleFunc("python:ping", pythonService.TestRequest)
	// mux.HandleFunc("python:set_signatures")
	if err := srv.Run(mux); err != nil {
		return err
	}
	return nil
}