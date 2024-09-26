package repositories

import (
	"github.com/ilyaDyb/similarity_service/internal/models"
	"gorm.io/gorm"
)

type TracksRepository struct {
	db *gorm.DB
}

func NewTracksRepository(db *gorm.DB) *TracksRepository {
	return &TracksRepository{db: db}
}

func (r *TracksRepository) GetTrackById(id string) (models.Track, error) {
	var track models.Track
	query := "SELECT * FROM tracks WHERE id = ?"
	err := r.db.Raw(query, id).Scan(&track)
	return track, err.Error
}

func (r *TracksRepository) SearchTracksByStr(str string) ([]models.Track, error) {
	var tracks []models.Track
	searchStr := "%" + str + "%"
	query := `SELECT * FROM tracks WHERE artists ILIKE ? OR title ILIKE ? LIMIT 30;`
	err := r.db.Raw(query, searchStr, searchStr).Scan(&tracks)
	return tracks, err.Error
}

func (r *TracksRepository) GetSimilarTracks(trackID string) ([]models.Track, error) {
	var tracks []models.Track

	// err := r.db.Exec("SET ivfflat.probes = 20").Error
	// if err != nil {
	// 	return nil, err
	// }

	query := `
		SELECT id, artists, title, preview_url
		FROM tracks
		ORDER BY signature <=> (SELECT signature FROM tracks WHERE id = ?)::vector
		LIMIT 20;
	`
	res := r.db.Raw(query, trackID).Scan(&tracks)

	return tracks, res.Error
}