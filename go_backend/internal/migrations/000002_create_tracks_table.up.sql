CREATE TABLE IF NOT EXISTS tracks (
    id SERIAL PRIMARY KEY,
    artist_id TEXT,
    artists TEXT,
    title TEXT,
    preview_url TEXT UNIQUE NOT NULL,
    signature VECTOR(110)
);
