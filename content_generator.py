import praw
import openai
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods import posts
import logging
import random
import os
from dotenv import load_dotenv
from config import Config

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

    Provide insights, analysis, and additional context. The article should be engaging and informative.
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a skilled financial journalist writing for a South African audience."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message['content']

def post_to_wordpress(article):
    if not article:
        return
    
    post = WordPressPost()
    post.title = "Financial Insights: " + article.split('\n')[0]  # Use first line as title
    post.content = article
    post.terms_names = {
        'category': ['Personal Finance'],
        'post_tag': ['South Africa', 'Finance', 'Advice']
    }
    post.post_status = 'draft'  # Set to 'publish' for immediate publishing
    
    post_id = wp.call(posts.NewPost(post))
    logger.info(f"Article posted to WordPress with ID: {post_id}")

def main():
    try:
        post = fetch_reddit_post()
        data = prepare_data(post)
        article = generate_article(data)
        post_to_wordpress(article)
        logger.info("Article generated and posted successfully")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
