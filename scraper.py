
# ============================================
# Install: pip install selenium webdriver-manager pandas
# ============================================

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import pandas as pd
from datetime import datetime, timedelta

class TwitterSeleniumScraper:
    def __init__(self, headless=False):
        """Initialize Selenium driver"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.all_tweets = []
    
    def login(self, username, password):
        """
        Login to Twitter (REQUIRED for scraping)
        You need your own Twitter account credentials
        """
        print("Logging in to Twitter...")
        self.driver.get("https://twitter.com/login")
        time.sleep(3)
        
        try:
            # Enter username/email
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]'))
            )
            username_input.send_keys(username)
            username_input.send_keys(Keys.RETURN)
            time.sleep(2)
            
            # Enter password
            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
            )
            password_input.send_keys(password)
            password_input.send_keys(Keys.RETURN)
            time.sleep(5)
            
            print("✓ Login successful!")
            return True
        except Exception as e:
            print(f"✗ Login failed: {e}")
            return False
    
    def scrape_tweets(self, query, max_tweets=100, scroll_pause=3):
        """Scrape tweets using search"""
        print(f"\nScraping tweets for: {query}")
        print(f"Target: {max_tweets} tweets\n")
        
        # Navigate to search
        search_url = f"https://twitter.com/search?q={query}&src=typed_query&f=live"
        self.driver.get(search_url)
        time.sleep(5)
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        tweets_found = set()
        no_new_tweets_count = 0
        
        while len(self.all_tweets) < max_tweets:
            # Find all tweet articles
            tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
            
            for tweet_elem in tweet_elements:
                if len(self.all_tweets) >= max_tweets:
                    break
                
                try:
                    # Get unique tweet ID to avoid duplicates
                    tweet_links = tweet_elem.find_elements(By.CSS_SELECTOR, 'a[href*="/status/"]')
                    if not tweet_links:
                        continue
                    
                    tweet_url = tweet_links[0].get_attribute('href')
                    tweet_id = tweet_url.split('/status/')[-1].split('?')[0] if '/status/' in tweet_url else None
                    
                    if not tweet_id or tweet_id in tweets_found:
                        continue
                    
                    tweets_found.add(tweet_id)
                    
                    # Extract username
                    try:
                        user_elem = tweet_elem.find_element(By.CSS_SELECTOR, 'div[data-testid="User-Name"]')
                        username_link = user_elem.find_element(By.CSS_SELECTOR, 'a')
                        username = username_link.get_attribute('href').split('/')[-1]
                        user_name = user_elem.text.split('\n')[0] if '\n' in user_elem.text else username
                    except:
                        username = "Unknown"
                        user_name = "Unknown"
                    
                    # Extract tweet text
                    try:
                        text_elem = tweet_elem.find_element(By.CSS_SELECTOR, 'div[data-testid="tweetText"]')
                        tweet_text = text_elem.text
                    except:
                        tweet_text = ""
                    
                    # Extract timestamp
                    try:
                        time_elem = tweet_elem.find_element(By.CSS_SELECTOR, 'time')
                        timestamp = time_elem.get_attribute('datetime')
                    except:
                        timestamp = datetime.now().isoformat()
                    
                    # Extract engagement metrics
                    try:
                        reply_elem = tweet_elem.find_element(By.CSS_SELECTOR, 'button[data-testid="reply"]')
                        replies = reply_elem.get_attribute('aria-label')
                        replies = ''.join(filter(str.isdigit, replies)) if replies else '0'
                    except:
                        replies = '0'
                    
                    try:
                        retweet_elem = tweet_elem.find_element(By.CSS_SELECTOR, 'button[data-testid="retweet"]')
                        retweets = retweet_elem.get_attribute('aria-label')
                        retweets = ''.join(filter(str.isdigit, retweets)) if retweets else '0'
                    except:
                        retweets = '0'
                    
                    try:
                        like_elem = tweet_elem.find_element(By.CSS_SELECTOR, 'button[data-testid="like"]')
                        likes = like_elem.get_attribute('aria-label')
                        likes = ''.join(filter(str.isdigit, likes)) if likes else '0'
                    except:
                        likes = '0'
                    
                    tweet_data = {
                        'user_id': username,
                        'user_name': user_name,
                        'timestamp': timestamp,
                        'tweet_text': tweet_text,
                        'likes': likes,
                        'retweets': retweets,
                        'replies': replies,
                        'tweet_url': tweet_url,
                        'tweet_id': tweet_id
                    }
                    
                    self.all_tweets.append(tweet_data)
                    print(f"✓ Collected: {len(self.all_tweets)}/{max_tweets} tweets")
                    
                except Exception as e:
                    continue
            
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)
            
            # Check if reached bottom
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                no_new_tweets_count += 1
                if no_new_tweets_count >= 3:
                    print("\n⚠ Reached end of available tweets")
                    break
            else:
                no_new_tweets_count = 0
            
            last_height = new_height
        
        print(f"\n✓ Total tweets collected: {len(self.all_tweets)}")
    
    def categorize_by_time(self):
        """Categorize tweets by time"""
        now = datetime.now()
        few_hours, few_days, few_weeks, older = [], [], [], []
        
        for tweet in self.all_tweets:
            try:
                tweet_time = datetime.fromisoformat(tweet['timestamp'].replace('Z', '+00:00'))
                # Make both timezone aware or naive
                if tweet_time.tzinfo:
                    from datetime import timezone
                    now = datetime.now(timezone.utc)
                time_diff = now - tweet_time
                
                if time_diff < timedelta(hours=24):
                    few_hours.append(tweet)
                elif time_diff < timedelta(days=7):
                    few_days.append(tweet)
                elif time_diff < timedelta(weeks=4):
                    few_weeks.append(tweet)
                else:
                    older.append(tweet)
            except:
                older.append(tweet)
        
        return few_hours, few_days, few_weeks, older
    
    def save_to_csv(self, filename='tata_motors_tweets.csv'):
        """Save to CSV"""
        if not self.all_tweets:
            print("No tweets to save!")
            return
        
        df = pd.DataFrame(self.all_tweets)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"\n✓ Saved to: {filename}")
        print(f"  Total records: {len(self.all_tweets)}")
    
    def save_categorized(self):
        """Save categorized tweets"""
        few_hours, few_days, few_weeks, older = self.categorize_by_time()
        
        files = [
            ('Few_Hours_Ago.txt', few_hours),
            ('Few_Days_Ago.txt', few_days),
            ('Few_Weeks_Ago.txt', few_weeks),
            ('Older_Tweets.txt', older)
        ]
        
        for filename, tweets in files:
            if tweets:
                with open(filename, 'w', encoding='utf-8') as f:
                    for tweet in tweets:
                        f.write(f"User: @{tweet['user_id']} ({tweet['user_name']})\n")
                        f.write(f"Time: {tweet['timestamp']}\n")
                        f.write(f"Tweet: {tweet['tweet_text']}\n")
                        f.write(f"Engagement: ❤️ {tweet['likes']} | 🔁 {tweet['retweets']} | 💬 {tweet['replies']}\n")
                        f.write(f"URL: {tweet['tweet_url']}\n")
                        f.write("-" * 80 + "\n\n")
                print(f"✓ Saved {len(tweets)} tweets to {filename}")
    
    def close(self):
        """Close browser"""
        self.driver.quit()


# ============================================
# MAIN EXECUTION
# ============================================
def main():
    print("=" * 80)
    print("TWITTER SCRAPER - TATA MOTORS REVIEWS")
    print("Using Selenium (Browser Automation)")
    print("=" * 80)
    
    # ⚠️ IMPORTANT: You need to provide your Twitter login credentials
    TWITTER_USERNAME = input("\nEnter your Twitter username/email: ").strip()
    TWITTER_PASSWORD = input("Enter your Twitter password: ").strip()
    
    if not TWITTER_USERNAME or not TWITTER_PASSWORD:
        print("\n❌ Error: Username and password are required!")
        print("\nWhy login is needed:")
        print("  - Twitter now requires authentication to view tweets")
        print("  - Use your own Twitter account (it's safe)")
        print("  - Your credentials are only used locally on your machine")
        return
    
    # Initialize scraper
    scraper = TwitterSeleniumScraper(headless=False)  # Set True to hide browser
    
    try:
        # Login to Twitter
        if not scraper.login(TWITTER_USERNAME, TWITTER_PASSWORD):
            print("\n❌ Login failed! Please check your credentials.")
            return
        
        # Search query
        query = "Tata Motors"
        
        # Scrape tweets
        scraper.scrape_tweets(query=query, max_tweets=100, scroll_pause=3)
        
        # Save results
        scraper.save_to_csv('tata_motors_tweets.csv')
        scraper.save_categorized()
        
        # Display sample
        if scraper.all_tweets:
            df = pd.DataFrame(scraper.all_tweets)
            print("\n" + "=" * 80)
            print("SAMPLE TWEETS:")
            print("=" * 80)
            print(df[['user_id', 'timestamp', 'tweet_text']].head(3).to_string())
        
        print("\n" + "=" * 80)
        print("✓ SCRAPING COMPLETED!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    finally:
        scraper.close()


if __name__ == "__main__":
    main()