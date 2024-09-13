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
import psycopg2
from urllib.parse import urlparse

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

def get_db_connection():
    database_url = os.environ['DATABASE_URL']
    conn = psycopg2.connect(database_url, sslmode='require')
    return conn

def initialize_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS processed_posts (
            post_id TEXT PRIMARY KEY
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def fetch_reddit_post():
    print("Fetching Reddit post...")
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Load processed post IDs
    cur.execute("SELECT post_id FROM processed_posts")
    processed_posts = set(row[0] for row in cur.fetchall())
    print(f"Number of processed posts: {len(processed_posts)}")
    
    subreddit = reddit.subreddit("PersonalFinanceZA")
    for post in subreddit.hot(limit=50):  # Increase limit if needed
        if post.id not in processed_posts and not post.stickied and post.selftext:
            # Add post ID to processed posts
            cur.execute("INSERT INTO processed_posts (post_id) VALUES (%s)", (post.id,))
            conn.commit()
            
            cur.close()
            conn.close()
            
            print(f"Fetched post: {post.title}")
            print(f"Post ID: {post.id}")
            return post
    
    cur.close()
    conn.close()
    print("No suitable unprocessed posts found")
    return None

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
        model="gpt-4o",
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
        print("Starting content generation process...")
        initialize_db()  # Make sure to call this before fetching posts
        post = fetch_reddit_post()
        if post:
            data = prepare_data(post)
            article = generate_article(data)
            post_to_wordpress(article)
            print("Article generated and posted successfully")
        else:
            print("No suitable unprocessed posts found. Exiting.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        print("Content generation process completed. Exiting.")

if __name__ == "__main__":
    main()
