const apiUrl = 'http://localhost:8000/api'; // Замените на ваш URL бэкенда

// Функция для отображения формы регистрации
function showRegister() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <h2>Регистрация</h2>
        <div id="error"></div>
        <form>
            <div class="form-group">
                <label for="username">Имя пользователя</label>
                <input type="text" class="form-control" id="username" placeholder="Введите имя пользователя">
            </div>
            <div class="form-group">
                <label for="email">Электронная почта</label>
                <input type="email" class="form-control" id="email" placeholder="Введите email">
            </div>
            <div class="form-group">
                <label for="password">Пароль</label>
                <input type="password" class="form-control" id="password" placeholder="Введите пароль">
            </div>
            <button type="button" class="btn btn-primary" onclick="register()">Зарегистрироваться</button>
        </form>
    `;
}


// Функция для регистрации пользователя
async function register() {
    const username = document.getElementById('username').value;
    const email    = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch(`${apiUrl}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });

        const data = await response.json();

        if (!response.ok) {
            showError(data.error || 'Ошибка регистрации');
        } else {
            showSuccess('Регистрация прошла успешно! Теперь вы можете войти.');
            showLogin();
        }
    } catch (error) {
        console.error(error);
    }
}

// Функция для отображения формы входа
function showLogin() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <h2>Вход</h2>
        <div id="error"></div>
        <form>
            <div class="form-group">
                <label for="username">Имя пользователя</label>
                <input type="text" class="form-control" id="username" placeholder="Введите имя пользователя">
            </div>
            <div class="form-group">
                <label for="password">Пароль</label>
                <input type="password" class="form-control" id="password" placeholder="Введите пароль">
            </div>
            <button type="button" class="btn btn-primary" onclick="login()">Войти</button>
        </form>
    `;
}


// Функция для входа пользователя
async function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch(`${apiUrl}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (!response.ok) {
            showError(data.error || 'Ошибка входа');
        } else {
            // Сохраняем токены в localStorage
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);
            showSuccess('Вход выполнен успешно!');
            showSearch();
        }
    } catch (error) {
        console.error(error);
    }
}

// Функция для отображения поиска треков
function showSearch() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <h2>Поиск треков</h2>
        <div id="error"></div>
        <form class="form-inline">
            <input type="text" class="form-control mr-sm-2" id="searchQuery" placeholder="Введите запрос">
            <button type="button" class="btn btn-success my-2 my-sm-0" onclick="searchTracks()">Поиск</button>
        </form>
        <div id="results" class="mt-4"></div>
    `;
}


// Функция для поиска треков
async function searchTracks() {
    const query = document.getElementById('searchQuery').value;
    const token = localStorage.getItem('access_token');

    try {
        const response = await fetch(`${apiUrl}/tracks?query=${encodeURIComponent(query)}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.status === 401) {
            // Обновляем токен и повторяем запрос
            await refreshToken();
            return searchTracks();
        }

        const data = await response.json();

        if (!response.ok) {
            document.getElementById('error').innerText = data.error || 'Ошибка поиска';
        } else {
            displayTracks(data.tracks);
        }
    } catch (error) {
        console.error(error);
    }
}

// Функция для отображения списка треков
function displayTracks(tracks) {
    const results = document.getElementById('results');
    if (tracks.length === 0) {
        results.innerHTML = '<p>Ничего не найдено</p>';
        return;
    }
    results.innerHTML = tracks.map(track => `
        <div class="card mb-3">
            <div class="card-body">
                <h5 class="card-title">${track.title}</h5>
                <p class="card-text">Исполнители: ${track.artists}</p>
                <button class="btn btn-info mr-2" onclick="getTrack('${track.id}')">Подробнее</button>
                <button class="btn btn-secondary" onclick="getSimilarTracks('${track.id}')">Похожие треки</button>
            </div>
        </div>
    `).join('');
}


// Функция для получения информации о треке
async function getTrack(id) {
    const token = localStorage.getItem('access_token');
    try {
        const response = await fetch(`${apiUrl}/tracks/${id}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.status === 401) {
            await refreshToken();
            return getTrack(id);
        }

        const track = await response.json();

        if (!response.ok) {
            showError(track.error || 'Ошибка получения трека');
        } else {
            const content = document.getElementById('content');
            content.innerHTML = `
                <h2>${track.title}</h2>
                <p>Исполнители: ${track.artists}</p>
                <audio controls src="${track.preview_url}"></audio>
                <br><br>
                <button class="btn btn-primary" onclick="showSearch()">Назад к поиску</button>
            `;
        }
    } catch (error) {
        console.error(error);
    }
}


// Функция для получения похожих треков
async function getSimilarTracks(id) {
    const token = localStorage.getItem('access_token');
    try {
        const response = await fetch(`${apiUrl}/tracks/similar/${id}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.status === 401) {
            await refreshToken();
            return getSimilarTracks(id);
        }

        const data = await response.json();

        if (!response.ok) {
            alert(data.error || 'Ошибка получения похожих треков');
        } else {
            displayTracks(data.tracks);
        }
    } catch (error) {
        console.error(error);
    }
}

// Функция для обновления токена
async function refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    try {
        const response = await fetch(`${apiUrl}/auth/refresh`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken })
        });

        const data = await response.json();

        if (!response.ok) {
            alert('Сессия истекла. Пожалуйста, войдите снова.');
            showLogin();
        } else {
            localStorage.setItem('access_token', data.access_token);
        }
    } catch (error) {
        console.error(error);
    }
}

// Функция для отображения админских функций
function showAdmin() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <h2>Админские функции</h2>
        <div id="error"></div>

        <div class="card mb-3">
            <div class="card-body">
                <h5 class="card-title">Загрузить треки по альбому</h5>
                <div class="form-group">
                    <label for="albumId">ID альбома</label>
                    <input type="text" class="form-control" id="albumId" placeholder="Введите ID альбома">
                </div>
                <button class="btn btn-primary" onclick="loadTracksByAlbum()">Загрузить</button>
            </div>
        </div>

        <div class="card mb-3">
            <div class="card-body">
                <h5 class="card-title">Загрузить треки по артисту</h5>
                <div class="form-group">
                    <label for="artistId">ID артиста</label>
                    <input type="text" class="form-control" id="artistId" placeholder="Введите ID артиста">
                </div>
                <button class="btn btn-primary" onclick="loadTracksByArtist()">Загрузить</button>
            </div>
        </div>

        <div class="card mb-3">
            <div class="card-body">
                <h5 class="card-title">Установить подписи</h5>
                <button class="btn btn-danger" onclick="setSignatures()">Запустить</button>
            </div>
        </div>
    `;
}


// Функция для загрузки треков по альбому
async function loadTracksByAlbum() {
    const albumId = document.getElementById('albumId').value;
    const token = localStorage.getItem('access_token');

    try {
        const response = await fetch(`${apiUrl}/admin/load-album`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ album_id: albumId })
        });

        if (response.status === 401) {
            await refreshToken();
            return loadTracksByAlbum();
        }

        if (!response.ok) {
            const data = await response.json();
            alert(data.error || 'Ошибка загрузки треков');
        } else {
            alert('Треки загружаются в фоне');
        }
    } catch (error) {
        console.error(error);
    }
}

// Функция для загрузки треков по артисту
async function loadTracksByArtist() {
    const artistId = document.getElementById('artistId').value;
    const token = localStorage.getItem('access_token');

    try {
        const response = await fetch(`${apiUrl}/admin/load-artist`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ artist_id: artistId })
        });

        if (response.status === 401) {
            await refreshToken();
            return loadTracksByArtist();
        }

        if (!response.ok) {
            const data = await response.json();
            alert(data.error || 'Ошибка загрузки треков');
        } else {
            alert('Треки загружаются в фоне');
        }
    } catch (error) {
        console.error(error);
    }
}

// Функция для установки подписей
async function setSignatures() {
    const token = localStorage.getItem('access_token');

    try {
        const response = await fetch(`${apiUrl}/admin/set-signatures`, {
            method: 'POST',
            headers: { 
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.status === 401) {
            await refreshToken();
            return setSignatures();
        }

        if (!response.ok) {
            const data = await response.json();
            alert(data.error || 'Ошибка установки подписей');
        } else {
            alert('Процесс установки подписей запущен');
        }
    } catch (error) {
        console.error(error);
    }
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.innerHTML = `<div class="alert alert-danger" role="alert">${message}</div>`;
}

function showSuccess(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.innerHTML = `<div class="alert alert-success" role="alert">${message}</div>`;
}

function updateNav() {
    const navLinks = document.getElementById('nav-links');
    const token = localStorage.getItem('access_token');

    if (token) {
        navLinks.innerHTML = `
            <li class="nav-item">
                <a class="nav-link" href="#" onclick="showSearch()">Поиск треков</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="#" onclick="showAdmin()">Админ</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="#" onclick="logout()">Выход</a>
            </li>
        `;
    } else {
        navLinks.innerHTML = `
            <li class="nav-item">
                <a class="nav-link" href="#" onclick="showRegister()">Регистрация</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="#" onclick="showLogin()">Вход</a>
            </li>
        `;
    }
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    showLogin();
    updateNav();
}


// При загрузке страницы отображаем форму входа или поиска, если пользователь уже вошел
window.onload = function() {
    updateNav();
    const token = localStorage.getItem('access_token');
    if (token) {
        showSearch();
    } else {
        showLogin();
    }
};

