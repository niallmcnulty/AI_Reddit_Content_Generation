# Content Generation Workflow

This project automates the process of generating and publishing articles based on Reddit posts from r/PersonalFinanceZA using OpenAI's GPT model and WordPress.

## Features

- Fetches popular posts from r/PersonalFinanceZA subreddit
- Generates unique articles using OpenAI's GPT model
- Automatically posts articles as drafts to WordPress
- Tracks processed posts to avoid duplicates
- Uses Heroku for deployment and scheduling

## Prerequisites

- Python 3.12+
- Reddit API credentials
- OpenAI API key
- WordPress site with XML-RPC enabled
- Heroku account (for deployment)

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and fill in your credentials:
   ```
   cp .env.example .env
   ```

4. Edit the `.env` file with your actual credentials and API keys.

## Configuration

Adjust settings in the `.env` file:

- Reddit API credentials
- OpenAI API key
- WordPress credentials

## Local Usage

Run the script locally:
