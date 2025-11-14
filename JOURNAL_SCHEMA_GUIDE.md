# Journal Database Schema Guide

## Overview

This database schema is designed to store and analyze years of journal entries with rich metadata, enabling temporal analysis, tagging, and pattern discovery.

## Core Design Principles

1. **Discrete Entries**: Each journal entry is stored separately with its own date and metadata
2. **Flexible Tagging**: Multi-category tagging system (moods, people, activities, topics, locations, projects)
3. **Temporal Analysis**: Optimized for date-based queries and cross-year comparisons
4. **Analytics-Ready**: Pre-computed views and stats tables for performance

## Schema Structure

### Main Tables

#### `files`
Tracks source files from Google Drive
- Stores filename, path, date range, import timestamp
- Checksums prevent duplicate imports

#### `entries`
The heart of the database - stores individual journal entries
- **entry_date**: When the entry was written
- **time_of_day**: Morning/afternoon/evening/night classification
- **content**: Full text of the entry
- **word_count** & **character_count**: For writing volume analysis
- **title**, **location**, **weather**: Optional metadata

#### `tags`
Flexible tagging with categories:
- **person**: People mentioned (friends, family, colleagues)
- **mood**: Emotional states (happy, sad, anxious, excited)
- **activity**: What you were doing (work, exercise, travel, coding)
- **topic**: Themes (health, goals, relationships, ideas)
- **location**: Places (cities, venues, countries)
- **project**: Specific projects or endeavors
- **other**: Catch-all category

#### `entry_tags`
Many-to-many relationship linking entries to tags
- Includes confidence score for auto-tagging scenarios

### Analytics Tables

#### `daily_stats`
Pre-computed daily aggregates for performance

#### `streaks`
Tracks consecutive writing periods

## Example Queries

### When Did Jake Write the Most?

```sql
-- Most productive month ever
SELECT year, month, entry_count, total_words
FROM monthly_stats
ORDER BY total_words DESC
LIMIT 1;

-- Most productive year
SELECT year, entry_count, total_words, avg_words
FROM yearly_stats
ORDER BY total_words DESC
LIMIT 1;

-- Busiest day of the week
SELECT
    CASE CAST(strftime('%w', entry_date) AS INTEGER)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END as day_of_week,
    COUNT(*) as entries,
    SUM(word_count) as total_words
FROM entries
GROUP BY strftime('%w', entry_date)
ORDER BY total_words DESC;

-- Top 10 most prolific days
SELECT
    entry_date,
    COUNT(*) as entries_that_day,
    SUM(word_count) as words_that_day
FROM entries
GROUP BY entry_date
ORDER BY words_that_day DESC
LIMIT 10;
```

### What Was Jake Up To On This Date Throughout the Years?

```sql
-- Entries on December 25th across all years
SELECT
    strftime('%Y', entry_date) as year,
    title,
    word_count,
    content,
    (SELECT GROUP_CONCAT(t.name, ', ')
     FROM entry_tags et
     JOIN tags t ON et.tag_id = t.id
     WHERE et.entry_id = e.id) as tags
FROM entries e
WHERE strftime('%m-%d', entry_date) = '12-25'
ORDER BY year DESC;

-- Using the view (same query, cleaner)
SELECT *
FROM same_day_history
WHERE month_day = '12-25';
```

### Mood Patterns

```sql
-- Most common moods
SELECT
    t.name as mood,
    COUNT(*) as times_tagged,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM entries), 2) as percentage
FROM entry_tags et
JOIN tags t ON et.tag_id = t.id
WHERE t.category = 'mood'
GROUP BY t.name
ORDER BY times_tagged DESC;

-- Mood by time of day
SELECT
    e.time_of_day,
    t.name as mood,
    COUNT(*) as occurrences
FROM entries e
JOIN entry_tags et ON e.id = et.entry_id
JOIN tags t ON et.tag_id = t.id
WHERE t.category = 'mood'
GROUP BY e.time_of_day, t.name
ORDER BY e.time_of_day, occurrences DESC;

-- How moods changed over time
SELECT
    strftime('%Y', e.entry_date) as year,
    t.name as mood,
    COUNT(*) as count
FROM entries e
JOIN entry_tags et ON e.id = et.entry_id
JOIN tags t ON et.tag_id = t.id
WHERE t.category = 'mood'
GROUP BY year, t.name
ORDER BY year, count DESC;
```

### People Mentioned

```sql
-- Most mentioned people
SELECT
    t.name as person,
    COUNT(*) as mentions,
    MIN(e.entry_date) as first_mention,
    MAX(e.entry_date) as last_mention,
    ROUND(julianday(MAX(e.entry_date)) - julianday(MIN(e.entry_date))) as days_span
FROM entry_tags et
JOIN tags t ON et.tag_id = t.id
JOIN entries e ON et.entry_id = e.id
WHERE t.category = 'person'
GROUP BY t.name
ORDER BY mentions DESC;

-- Co-occurrence: Which people are mentioned together?
SELECT
    t1.name as person1,
    t2.name as person2,
    COUNT(*) as times_together
FROM entry_tags et1
JOIN entry_tags et2 ON et1.entry_id = et2.entry_id AND et1.tag_id < et2.tag_id
JOIN tags t1 ON et1.tag_id = t1.id
JOIN tags t2 ON et2.tag_id = t2.id
WHERE t1.category = 'person' AND t2.category = 'person'
GROUP BY t1.name, t2.name
ORDER BY times_together DESC
LIMIT 20;
```

### Activity Patterns

```sql
-- Most common activities by year
SELECT
    strftime('%Y', e.entry_date) as year,
    t.name as activity,
    COUNT(*) as count
FROM entries e
JOIN entry_tags et ON e.id = et.entry_id
JOIN tags t ON et.tag_id = t.id
WHERE t.category = 'activity'
GROUP BY year, t.name
ORDER BY year DESC, count DESC;

-- Activity streaks (consecutive days doing something)
WITH activity_days AS (
    SELECT DISTINCT
        e.entry_date,
        t.name as activity
    FROM entries e
    JOIN entry_tags et ON e.id = et.entry_id
    JOIN tags t ON et.tag_id = t.id
    WHERE t.category = 'activity'
)
SELECT
    activity,
    entry_date as start_date,
    COUNT(*) OVER (
        PARTITION BY activity,
        DATE(entry_date, '-' || ROW_NUMBER() OVER (PARTITION BY activity ORDER BY entry_date) || ' days')
    ) as streak_length
FROM activity_days
ORDER BY streak_length DESC, activity, start_date;
```

### Writing Patterns

```sql
-- Writing frequency over time
SELECT
    strftime('%Y-%m', entry_date) as month,
    COUNT(*) as entries,
    SUM(word_count) as words,
    AVG(word_count) as avg_words_per_entry
FROM entries
GROUP BY month
ORDER BY month;

-- Time of day preference
SELECT
    time_of_day,
    COUNT(*) as entries,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM entries), 2) as percentage,
    AVG(word_count) as avg_words
FROM entries
WHERE time_of_day != 'unknown'
GROUP BY time_of_day
ORDER BY entries DESC;

-- Longest entries
SELECT
    entry_date,
    title,
    word_count,
    (SELECT GROUP_CONCAT(t.name, ', ')
     FROM entry_tags et
     JOIN tags t ON et.tag_id = t.id
     WHERE et.entry_id = e.id) as tags,
    substr(content, 1, 100) || '...' as preview
FROM entries e
ORDER BY word_count DESC
LIMIT 10;

-- Entry length distribution
SELECT
    CASE
        WHEN word_count < 50 THEN '< 50 words'
        WHEN word_count < 100 THEN '50-99 words'
        WHEN word_count < 250 THEN '100-249 words'
        WHEN word_count < 500 THEN '250-499 words'
        WHEN word_count < 1000 THEN '500-999 words'
        ELSE '1000+ words'
    END as length_category,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM entries), 2) as percentage
FROM entries
GROUP BY length_category;
```

### Search and Discovery

```sql
-- Full text search for keywords
SELECT
    entry_date,
    title,
    word_count,
    substr(content, INSTR(LOWER(content), LOWER('keyword')) - 50, 200) as context
FROM entries
WHERE LOWER(content) LIKE '%keyword%'
ORDER BY entry_date DESC;

-- Find entries with multiple tags
SELECT
    e.entry_date,
    e.title,
    GROUP_CONCAT(t.name, ', ') as tags
FROM entries e
JOIN entry_tags et ON e.id = et.entry_id
JOIN tags t ON et.tag_id = t.id
WHERE t.name IN ('travel', 'excited', 'friends')
GROUP BY e.id
HAVING COUNT(DISTINCT t.name) >= 2
ORDER BY e.entry_date DESC;

-- Entries from a specific period
SELECT
    entry_date,
    title,
    word_count,
    (SELECT GROUP_CONCAT(name, ', ')
     FROM tags
     WHERE id IN (SELECT tag_id FROM entry_tags WHERE entry_id = e.id)) as tags
FROM entries e
WHERE entry_date BETWEEN '2023-06-01' AND '2023-08-31'
ORDER BY entry_date;
```

### Tag Analysis

```sql
-- Tag evolution (when tags were most used)
SELECT
    t.name,
    t.category,
    strftime('%Y', e.entry_date) as year,
    COUNT(*) as usage_count
FROM tags t
JOIN entry_tags et ON t.id = et.tag_id
JOIN entries e ON et.entry_id = e.id
GROUP BY t.name, t.category, year
ORDER BY t.name, year;

-- Unused tags
SELECT name, category, created_at
FROM tags
WHERE id NOT IN (SELECT DISTINCT tag_id FROM entry_tags);

-- Tag combinations (what tags appear together most)
SELECT
    t1.name as tag1,
    t2.name as tag2,
    COUNT(*) as co_occurrences
FROM entry_tags et1
JOIN entry_tags et2 ON et1.entry_id = et2.entry_id AND et1.tag_id < et2.tag_id
JOIN tags t1 ON et1.tag_id = t1.id
JOIN tags t2 ON et2.tag_id = t2.id
GROUP BY t1.name, t2.name
ORDER BY co_occurrences DESC
LIMIT 25;
```

## Visualization Ideas

### Daily Heatmap
Use `daily_stats` to create a GitHub-style contribution graph showing writing frequency

### Timeline View
Query entries by date and display on a scrollable timeline with tag colors

### Mood Ring
Circular visualization of mood distribution over time

### Word Cloud
Generate from most common tags or keywords extracted from content

### This Day in History
Show all entries from the current day (MM-DD) across all years in a vertical timeline

### Network Graph
Visualize tag co-occurrences or people mentioned together

### Writing Streaks
Calendar view highlighting consecutive writing days

## Data Import Strategy

1. **Parse files** chronologically
2. **Extract entries** by date markers or natural breaks
3. **Analyze content** for:
   - Word count
   - Time indicators (morning, 3pm, evening, etc.)
   - Keywords for auto-tagging
4. **Insert into database** with transaction batching
5. **Manual tag review** for accuracy
6. **Compute daily_stats** after import

## Maintenance Queries

```sql
-- Recompute daily stats
INSERT OR REPLACE INTO daily_stats (stat_date, entry_count, total_words, total_characters, avg_words_per_entry, unique_tags)
SELECT
    entry_date,
    COUNT(*),
    SUM(word_count),
    SUM(character_count),
    AVG(word_count),
    (SELECT COUNT(DISTINCT tag_id)
     FROM entry_tags et
     WHERE et.entry_id IN (SELECT id FROM entries e2 WHERE e2.entry_date = e.entry_date))
FROM entries e
GROUP BY entry_date;

-- Find and merge duplicate entries
SELECT entry_date, content, COUNT(*) as duplicates
FROM entries
GROUP BY entry_date, content
HAVING duplicates > 1;

-- Cleanup orphaned tags
DELETE FROM tags
WHERE id NOT IN (SELECT DISTINCT tag_id FROM entry_tags);
```

## Extensions & Future Ideas

- **Sentiment analysis**: Add sentiment_score column to entries
- **Media attachments**: New table for photos, sketches referenced in entries
- **Goals tracking**: Link entries to personal goals with progress indicators
- **Relationships graph**: Explicit relationship tracking between people
- **Location geocoding**: Lat/long for location-based queries
- **AI summaries**: Store AI-generated summaries for long entries
- **Export formats**: JSON, Markdown, PDF generation from queries

## Technology Recommendations

- **Database**: SQLite (portable), PostgreSQL (for larger scale)
- **Backend**: Python with SQLAlchemy or plain SQL
- **Analysis**: pandas, matplotlib, seaborn for data science
- **Visualization**: D3.js, Plotly, or Observable for web dashboards
- **NLP**: spaCy or NLTK for auto-tagging and entity extraction
- **Frontend**: React/Vue with a calendar/timeline component library

---

Have fun exploring your life through data! 📊✨
