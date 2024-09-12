# Content Generation Workflow

This project automates the process of generating and publishing articles based on Reddit posts from r/PersonalFinanceZA using OpenAI's GPT model and WordPress.

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in your credentials
4. Run the script: `python content_generator.py`

## Configuration

Adjust settings in `.env` file:

- Reddit API credentials
- OpenAI API key
- WordPress credentials

## Usage

The script runs daily to:
1. Fetch a popular post from r/PersonalFinanceZA
2. Generate an article using GPT-3
3. Post the article as a draft on WordPress

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
