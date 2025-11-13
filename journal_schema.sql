-- Journal Database Schema
-- Designed for parsing and analyzing personal journal entries over years
-- Optimized for temporal queries, tagging, and data analysis

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Source files from Google Drive
CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    original_path TEXT,
    file_size_bytes INTEGER,
    date_range_start DATE,
    date_range_end DATE,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    checksum TEXT, -- for detecting duplicates
    UNIQUE(checksum)
);

-- Main journal entries table
CREATE TABLE entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    entry_date DATE NOT NULL,
    time_of_day TEXT CHECK(time_of_day IN ('morning', 'afternoon', 'evening', 'night', 'unknown')),
    content TEXT NOT NULL,
    word_count INTEGER NOT NULL,
    character_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Optional metadata
    title TEXT, -- if entry has a title
    location TEXT, -- free-form location string
    weather TEXT, -- if mentioned

    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
);

-- Indexes for common queries
CREATE INDEX idx_entries_date ON entries(entry_date);
CREATE INDEX idx_entries_file ON entries(file_id);
CREATE INDEX idx_entries_word_count ON entries(word_count);
CREATE INDEX idx_entries_time_of_day ON entries(time_of_day);

-- ============================================================================
-- TAGGING SYSTEM
-- ============================================================================

-- Flexible tagging system with categories
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT CHECK(category IN ('person', 'mood', 'activity', 'topic', 'location', 'project', 'other')),
    description TEXT,
    color TEXT, -- hex color for visualization
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(name, category)
);

CREATE INDEX idx_tags_category ON tags(category);
CREATE INDEX idx_tags_name ON tags(name);

-- Many-to-many relationship between entries and tags
CREATE TABLE entry_tags (
    entry_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    confidence REAL DEFAULT 1.0 CHECK(confidence >= 0 AND confidence <= 1), -- for auto-tagging
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (entry_id, tag_id),
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE INDEX idx_entry_tags_entry ON entry_tags(entry_id);
CREATE INDEX idx_entry_tags_tag ON entry_tags(tag_id);

-- ============================================================================
-- ANALYTICS TABLES
-- ============================================================================

-- Pre-computed daily statistics for performance
CREATE TABLE daily_stats (
    stat_date DATE PRIMARY KEY,
    entry_count INTEGER DEFAULT 0,
    total_words INTEGER DEFAULT 0,
    total_characters INTEGER DEFAULT 0,
    avg_words_per_entry REAL,
    unique_tags INTEGER DEFAULT 0,
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Track writing streaks
CREATE TABLE streaks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    days_count INTEGER NOT NULL,
    entries_count INTEGER NOT NULL,
    total_words INTEGER NOT NULL
);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Entries with all their tags
CREATE VIEW entry_tags_view AS
SELECT
    e.id as entry_id,
    e.entry_date,
    e.title,
    e.word_count,
    e.time_of_day,
    t.name as tag_name,
    t.category as tag_category,
    et.confidence
FROM entries e
LEFT JOIN entry_tags et ON e.id = et.entry_id
LEFT JOIN tags t ON et.tag_id = t.id;

-- View: Monthly writing statistics
CREATE VIEW monthly_stats AS
SELECT
    strftime('%Y', entry_date) as year,
    strftime('%m', entry_date) as month,
    COUNT(*) as entry_count,
    SUM(word_count) as total_words,
    AVG(word_count) as avg_words,
    MIN(word_count) as min_words,
    MAX(word_count) as max_words
FROM entries
GROUP BY year, month
ORDER BY year DESC, month DESC;

-- View: Yearly writing statistics
CREATE VIEW yearly_stats AS
SELECT
    strftime('%Y', entry_date) as year,
    COUNT(*) as entry_count,
    SUM(word_count) as total_words,
    AVG(word_count) as avg_words,
    COUNT(DISTINCT strftime('%Y-%m-%d', entry_date)) as days_with_entries
FROM entries
GROUP BY year
ORDER BY year DESC;

-- View: Tag usage frequency
CREATE VIEW tag_frequency AS
SELECT
    t.name,
    t.category,
    COUNT(et.entry_id) as usage_count,
    MIN(e.entry_date) as first_used,
    MAX(e.entry_date) as last_used
FROM tags t
LEFT JOIN entry_tags et ON t.id = et.tag_id
LEFT JOIN entries e ON et.entry_id = e.id
GROUP BY t.id, t.name, t.category
ORDER BY usage_count DESC;

-- View: "This day in history" - entries on same day across years
CREATE VIEW same_day_history AS
SELECT
    strftime('%m-%d', entry_date) as month_day,
    strftime('%Y', entry_date) as year,
    id as entry_id,
    title,
    word_count,
    substr(content, 1, 200) as preview
FROM entries
ORDER BY month_day, year;

-- ============================================================================
-- SAMPLE DATA / SEED
-- ============================================================================

-- Pre-populate common tag categories
INSERT INTO tags (name, category, description, color) VALUES
('happy', 'mood', 'Positive, joyful mood', '#FFD700'),
('sad', 'mood', 'Melancholic, down mood', '#4169E1'),
('anxious', 'mood', 'Worried, nervous', '#FF6347'),
('reflective', 'mood', 'Contemplative, introspective', '#9370DB'),
('excited', 'mood', 'Energetic, enthusiastic', '#FF69B4'),
('work', 'activity', 'Professional work and career', '#708090'),
('exercise', 'activity', 'Physical activity and fitness', '#32CD32'),
('travel', 'activity', 'Travel and exploration', '#FF8C00'),
('reading', 'activity', 'Reading books, articles', '#8B4513'),
('coding', 'activity', 'Programming and development', '#00CED1'),
('family', 'topic', 'Family matters and relationships', '#FF1493'),
('health', 'topic', 'Health and wellness', '#7FFF00'),
('goals', 'topic', 'Personal goals and aspirations', '#FFD700'),
('memories', 'topic', 'Remembering past events', '#DDA0DD'),
('ideas', 'topic', 'New ideas and insights', '#00FA9A');
