CREATE TABLE batches (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_lang TEXT,
  target_lang TEXT
);

CREATE TABLE batch_keys (
  key TEXT PRIMARY KEY CHECK (length(key) = 36),
  batch_id INTEGER REFERENCES batch(id)
);

CREATE TABLE sentences (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  batch_id INTEGER REFERENCES batch(id),
  source TEXT
);

CREATE TABLE translators (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT
);

CREATE TABLE translations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_id INTEGER REFERENCES sentence(id),
  translator_id INTEGER REFERENCES translator(id),
  translation TEXT
);

CREATE TABLE rankings (
  translation_id INTEGER REFERENCES translations(id),
  batch_key INTEGER REFERENCES batch_keys(key),
  rank INTEGER NOT NULL CHECK (rank > 0)
);
