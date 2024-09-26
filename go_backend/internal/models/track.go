package models

type Track struct {
	ID         int       `json:"id"`
	ArtistID   string    `json:"artist_id"`
	Artists    string    `json:"artists"`
	Title      string    `json:"title"`
	PreviewUrl string    `json:"preview_url"`
	// Signature  []float64 `json:"-"`
}
