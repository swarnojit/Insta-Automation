from instagrapi import Client
import pandas as pd
import time
import random
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get Instagram credentials
username = os.getenv("INSTAGRAM_USERNAME")
password = os.getenv("INSTAGRAM_PASSWORD")

# Get target Instagram username from environment variables
target_username = os.getenv("TARGET_USERNAME")

if not target_username:
    raise ValueError("TARGET_USERNAME is not set in the .env file.")

# Login to Instagram
cl = Client()
cl.login(username, password)

# Fetch the numeric user ID from the username
target_user_id = cl.user_id_from_username(target_username)

# Number of recent posts to fetch
find_value = 50

# List of relaxing comments for influencers (for a boy)
comments_list = [
   "You are absolutely breathtaking! 😍",
    "Your beauty radiates from within! 🌟",
    "Every photo is a masterpiece! 🎨",
    "You have the most enchanting smile! 💖",
    "Absolutely stunning, as always! 💕",
    "You redefine beauty! 😘",
    "Your confidence is truly inspiring! 💪",
    "You light up every room you enter! ✨",
    "Just when I thought you couldn't get more beautiful! 🌹",
    "This look is everything! Slaying it! 🔥",
    "You have the kind of beauty that takes my breath away! 💞",
    "Your style is always on point! 👗",
    "Looking like a dream! Keep shining! 🌈",
    "Your beauty is mesmerizing! Can't get enough! 🌺",
    "Every picture tells a beautiful story! 📸"
]

# Check if the user is followed, if not, follow and log it in follow.csv
try:
    follow_df = pd.read_csv('follow.csv')
except FileNotFoundError:
    follow_df = pd.DataFrame(columns=['user_id', 'username'])

if target_user_id not in follow_df['user_id'].values:
    try:
        print(f"Not following {target_username}, following now...")
        cl.user_follow(target_user_id)
        print(f"Followed {target_username} successfully!")

        # Log the followed account in follow.csv
        follow_df = pd.concat([follow_df, pd.DataFrame({'user_id': [target_user_id], 'username': [target_username]})])
        follow_df.to_csv('follow.csv', index=False, encoding='utf-8')
    except Exception as e:
        print(f"Error following {target_username}: {e}")
else:
    print(f"Already following {target_username}.")

while True:
    try:
        # Fetch recent media/posts from the user account
        user_posts = cl.user_medias(target_user_id, find_value)
    except Exception as e:
        print(f"Error fetching user posts: {e}")
        time.sleep(30)
        continue

    # Reading the CSV file that stores liked posts
    try:
        likes_df = pd.read_csv('likes.csv')
    except FileNotFoundError:
        # Create an empty DataFrame with columns if the file is missing
        likes_df = pd.DataFrame(columns=['post_id', 'post_code', 'post_url'])

    # Reading the CSV file that stores comments
    try:
        commenting_df = pd.read_csv('commenting.csv')
    except FileNotFoundError:
        # Create an empty DataFrame with columns if the file is missing
        commenting_df = pd.DataFrame(columns=['post_id', 'post_code', 'post_url', 'comment'])

    for post in user_posts:
        post_info = post.dict()
        post_id = post_info['id']
        post_code = post_info['code']
        post_url = f"https://instagram.com/reel/{post_code}"

        # Check if the post is already liked
        is_liked = post_id in likes_df['post_id'].values

        if not is_liked:
            print(f"New post found! Liking and commenting on post: {post_url}")

            # Randomly select a comment from the list
            comment = random.choice(comments_list)

            try:
                # Comment on the post
                cl.media_comment(post_id, comment)
                print(f"Commented on post {post_id}")

                # Log the comment in commenting.csv
                new_comment_row = pd.DataFrame({'post_id': [post_id], 'post_code': [post_code], 'post_url': [post_url], 'comment': [comment]})
                commenting_df = pd.concat([commenting_df, new_comment_row], ignore_index=True)
                commenting_df.to_csv('commenting.csv', index=False, encoding='utf-8')
            except Exception as e:
                print(f"Error commenting on post {post_id}: {e}")
                continue

            try:
                # Like the post
                cl.media_like(post_id)
                print(f"Liked post {post_id}")

                # Log the liked post in likes.csv
                new_like_row = pd.DataFrame({'post_id': [post_id], 'post_code': [post_code], 'post_url': [post_url]})
                likes_df = pd.concat([likes_df, new_like_row], ignore_index=True)
                likes_df.to_csv('likes.csv', index=False, encoding='utf-8')
            except Exception as e:
                print(f"Error liking post {post_id}: {e}")
                continue
        else:
            print(f"Post {post_id} is already liked.")

    # Wait for 5 seconds before checking for new posts
    print("Waiting for 5 seconds before checking for new posts...")
    time.sleep(5)