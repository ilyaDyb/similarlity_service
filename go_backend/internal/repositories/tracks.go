package repositories

import (
	"errors"
	"fmt"

	"github.com/ilyaDyb/similarity_service/internal/models"
	"gorm.io/gorm"
)

type TracksRepository struct {
	DB *gorm.DB
}

func NewTracksRepository(db *gorm.DB) *TracksRepository {
	return &TracksRepository{DB: db}
}

func (r *TracksRepository) GetTrackById(id string) (models.Track, error) {
	var track models.Track
	query := "SELECT * FROM tracks WHERE id = ?"
	err := r.DB.Raw(query, id).Scan(&track)
	return track, err.Error
}

func (r *TracksRepository) SearchTracksByStr(str string) ([]models.Track, error) {
	var tracks []models.Track
	searchStr := "%" + str + "%"
	query := `SELECT * FROM tracks WHERE artists ILIKE ? OR title ILIKE ? LIMIT 30;`
	err := r.DB.Raw(query, searchStr, searchStr).Scan(&tracks)
	return tracks, err.Error
}

func (r *TracksRepository) GetSimilarTracks(trackId string) ([]models.Track, error) {
	var tracks []models.Track

	query := `
		SELECT id, artists, title, preview_url
		FROM tracks
		ORDER BY signature <-> (SELECT signature FROM tracks WHERE id = ?)::vector
		LIMIT 20;
	`
	err := r.DB.Raw(query, trackId).Scan(&tracks).Error

	return tracks, err
}

func (r *TracksRepository) CheckSignature(trackId string) error {
	var track struct {
		Title string
	}
	err := r.DB.Table("tracks").
		Select("title").
		Where("id = ? AND signature IS NOT NULL", trackId).
		Take(&track).Error

	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return fmt.Errorf("Track with id: %s has not a signature")
		}
		return fmt.Errorf("Error db query: %v", err)
	}
	return nil
}