# GameForge

GameForge is a cyber-styled terminal application for tracking video games, player libraries, sentiment, value-for-money, and cross-game lore relationships.

It runs as a Python console app and stores data in MongoDB.

## Core Highlights

- Full terminal workflow with a HUD-like interface
- Complete CRUD support for users, games, and library entries
- Genre and playstyle support for both users and games
- Lore tag graph-style linking for recommendation-style suggestions
- Sentiment tracking with emotional state and score
- Dust metric that identifies stale games not touched for 6+ months
- Financial tracking using price paid and cost per hour
- Seed script with realistic sample users, games, and tracked entries

## Tech Stack

- Python 3.10+
- MongoDB
- pymongo
- mongomock fallback support when MongoDB is unavailable

## Project Structure

- main.py: App entry point
- seed.py: Database seeding script
- config/database.py: MongoDB client and connection configuration
- models/user_model.py: User creation and update models
- models/game_model.py: Game and library entry models
- services/library_service.py: CRUD operations and analytics logic
- services/cli.py: Interactive terminal menu flow
- utils/terminal_ui.py: HUD rendering helpers

## Functional Coverage

### User Management

- Create user
- List users
- Update user
- Delete user
- Resolve users by either ObjectId or username

### Game Management

- Create game
- List games
- Update game
- Delete game
- Store genres, playstyles, lore tags, platform, release year, and price paid

### Library Tracking

- Track game for a user
- Update tracked entry
- Delete tracked entry
- View one user library
- View all library entries

### Advanced Metrics

- Hours played tracking
- Completion tracking
- Achievement tracking
- Sentiment state tracking
- Sentiment score tracking
- Cost per hour calculation
- Financial verdict labels such as HIGH VALUE and EXPENSIVE
- Dust state calculation based on inactivity windows

### Lore Linker

- Store custom lore tags per game
- Compare shared lore tags, genres, and playstyles
- Suggest next games based on trait overlap

### Dashboard and Search

- User-level stats summary
- Game inspection HUD
- Game search by title, developer, genre, playstyle, and lore tags

## Menu Operations

The app currently exposes these interactive options:

1. Add user
2. List users
3. Update user
4. Delete user
5. Add game
6. List games
7. Update game
8. Delete game
9. Track a game
10. Update tracked game
11. Delete tracked game
12. View user library
13. Inspect game HUD
14. Lore-link suggestions
15. Search games
16. View user stats
17. List all library entries
18. Exit

## Data Model Summary

### users collection

- username
- email
- favorite_platform
- favorite_genres
- playstyles
- bio
- created_at
- updated_at

### games collection

- title
- genre
- playstyles
- lore_tags
- developer
- release_year
- price_paid
- platform
- description
- added_at
- created_at
- updated_at

### library collection

- user_id
- game_id
- hours_played
- status
- sentiment_state
- sentiment_score
- rating
- comment
- achievements_unlocked
- completion_percentage
- last_played_at
- created_at
- updated_at

Derived values are computed at runtime in the service layer:

- cost_per_hour
- financial_value
- dust_days
- dust_state
- dust_score
- dust_note

## Installation

1. Ensure Python 3.10 or newer is installed.
2. Ensure MongoDB is installed and running locally, or provide a remote URI.
3. Install Python dependencies.

```bash
pip install -r requirements.txt
```

## Configuration

You can configure database access with environment variables:

- MONGODB_URI: MongoDB connection string
- MONGODB_DB: Database name (default: gameforge)
- MONGODB_ALLOW_MOCK: Set to 0 to disable mongomock fallback

Default connection values:

- URI: mongodb://localhost:27017
- Database: gameforge

## Seed Data

The seed script clears and repopulates all three collections with rich demo data.

Run:

```bash
python seed.py
```

Current seed includes:

- 12 users
- 11 games
- 11 tracked library entries

## Run the Application

Start the CLI:

```bash
python main.py
```

If your shell is not currently in the GameForge folder, run with an absolute path or change directory first.

## Notes

- The interface is intentionally themed for a cyber terminal feel.
- The app accepts usernames and game titles in many lookup paths, not only ObjectIds.
- Datetime logic is timezone-normalized for dust calculations.
