import praw
import openai
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods import posts
import logging
import random
import os
from dotenv import load_dotenv
from config import Config
import time
import markdown2

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Reddit API client
reddit = praw.Reddit(
    client_id=Config.REDDIT_CLIENT_ID,
    client_secret=Config.REDDIT_CLIENT_SECRET,
    user_agent=Config.REDDIT_USER_AGENT
)

# Initialize OpenAI API client
openai.api_key = Config.OPENAI_API_KEY

# Initialize WordPress client
wp = Client(Config.WP_URL, Config.WP_USERNAME, Config.WP_PASSWORD)

def fetch_reddit_post():
    subreddit = reddit.subreddit("PersonalFinanceZA")
    posts = list(subreddit.new(limit=50))
    eligible_posts = [post for post in posts if post.num_comments >= 3 and post.created_utc > (time.time() - 86400)]
    
    if not eligible_posts:
        logger.warning("No eligible posts found")
        return None
    
    return random.choice(eligible_posts)

def prepare_data(post):
    if not post:
        return None
    
    title = post.title
    content = post.selftext
    top_comments = [comment.body for comment in post.comments.list()[:3]]
    
    return {
        "title": title,
        "content": content,
        "comments": top_comments
    }

def generate_article(data):
    if not data:
        return None
    
    prompt = f"""
    As a financial journalist, write an informative article based on the following Reddit post:
    Title: {data['title']}
    Content: {data['content']}
    Top comments:
    1. {data['comments'][0]}
    2. {data['comments'][1]}
    3. {data['comments'][2]}

    Provide insights, analysis, and additional context. The article should be engaging and informative. Use the Reddit post and comments as source material but write the article as a traditional article for a publication. Don't reference the Reddit post, user or comments directly. Improve readability by writing shorter sentences and simpler language to target an 8th grade reading level.
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a skilled financial journalist writing for a South African audience."},
            {"role": "user", "content": prompt}
        ]
    )

    article = response.choices[0].message['content']
    
    # Ensure the article starts with a title
    if not article.startswith('Title:'):
        article = f"Title: {data['title']}\n\n{article}"
    
    return article

def post_to_wordpress(article):
    if not article:
        return
    
    # Split the article into lines
    lines = article.split('\n')
    
    # Extract the title (first line) and remove "Title: " if present
    title = lines[0].replace("Title: ", "").strip()
    
    # Join the rest of the lines back into the content, skipping the title
    content = '\n'.join(lines[1:]).strip()
    
    # Convert markdown to HTML and ensure it's a regular string
    html_content = str(markdown2.markdown(content))
    
    post = WordPressPost()
    post.title = title
    post.content = html_content
    post.post_format = 'standard'  # This ensures it uses the default editor
    post.terms_names = {
        'category': ['Personal Finance'],
        'post_tag': ['South Africa', 'Finance', 'Advice']
    }
    post.post_status = 'publish'  # Set to 'publish' for immediate publishing
    
    post_id = wp.call(posts.NewPost(post))
    logger.info(f"Article posted to WordPress with ID: {post_id}")

def main():
    try:
        print("Fetching Reddit post...")
        post = fetch_reddit_post()
        print(f"Fetched post: {post.title}")

        print("Preparing data...")
        data = prepare_data(post)
        print("Data prepared.")

        print("Generating article...")
        article = generate_article(data)
        print(f"Article generated. First 100 characters: {article[:100]}...")

        print("Posting to WordPress...")
        post_to_wordpress(article)
        print("Article posted to WordPress.")

        logger.info("Article generated and posted successfully")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
