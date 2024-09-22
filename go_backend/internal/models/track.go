package models

type Track struct {
    ArtistID   string `gorm:"column:artist_id" json:"artist_id"`
    Artists    string `gorm:"column:artists" json:"artists"`
    Title      string `gorm:"column:title" json:"title"`
    PreviewUrl string `gorm:"column:preview_url;unique;not null" json:"preview_url"`
    Signature  string `gorm:"column:signature" json:"signature"`
}
