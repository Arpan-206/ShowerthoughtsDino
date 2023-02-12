import os
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from dotenv import load_dotenv
import praw
import asyncio
import logging

from rich import print

# Create a log file here
logging.basicConfig(filename='bot.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

load_dotenv()

# Initializes your app with your bot token and socket mode handler
app = AsyncApp(token=os.environ.get("SLACK_BOT_TOKEN"))

reddit = praw.Reddit(
    client_id=os.environ.get("REDDIT_CLIENT_ID"),
    client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
    user_agent=os.environ.get("REDDIT_USER_AGENT"),
)

subreddit = reddit.subreddit("ShowerThoughts")


@app.command("/random-showerthought")
async def repeat_text(ack, respond, command):
    # Acknowledge command request
    ack()

    submission = subreddit.random()
    my_message = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"\"{submission.title}\""
                }
            }

        ]
    }
    await respond(f"{command['text']}")


async def daily_top_10():
    """This function will post the top 10 shower thoughts to the channel every 24 hours.
    """

    my_message = {
        "blocks": [

            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "The Shower Thoughts for today!",
                    "emoji": True
                }
            },
            {
                "type": "divider"
            },
        ]
    }
    hot = subreddit.hot(limit=10)
    for submission in hot:
        # add a new block to the message
        if submission.over_18:
            my_message["blocks"].append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"> {submission.title} (NSFW)"
                    }}
            )
        my_message["blocks"].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"> {submission.title}"
            }
        })

    logging.info("Posting the top 10 shower thoughts to Slack")

    await app.client.chat_postMessage(
        channel="#shower-thoughts",
        blocks=my_message["blocks"]
    )

    logging.info("Sleeping for 24 hours")
    await asyncio.sleep(86400)


async def main():
    asyncio.ensure_future(daily_top_10())
    handler = AsyncSocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    await handler.start_async()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
