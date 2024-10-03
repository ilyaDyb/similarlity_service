package repositories

import "gorm.io/gorm"

type AdminRepo struct {
	DB *gorm.DB
}

func NewAdminRepository(db *gorm.DB) *AdminRepo {
	return &AdminRepo{DB: db}
}

func (r *AdminRepo) CheckAdminRole(userId string) (bool, error) {
	var isAdmin bool
	err := r.DB.Raw("SELECT is_admin FROM users WHERE id = ?", userId).Scan(&isAdmin).Error
	if err != nil {
		return false, err
	}
	if isAdmin {
		return true, nil
	}
	return false, nil	
}