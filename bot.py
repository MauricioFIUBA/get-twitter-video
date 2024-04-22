'''Telegram bot get Twitter video'''
import sys
import os
import logging
from datetime import timedelta
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, Application, ContextTypes, CommandHandler, MessageHandler, filters

from twitter import get_twitter_video
from exceptions import NoVideoFoundError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

load_dotenv()

ALLOWED_URLS = ['twitter.com', 'x.com']


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Start command handler'''
    effective_chat = update.effective_chat
    if effective_chat is None:
        return

    await context.bot.send_message(chat_id=effective_chat.id,
                                   text='Hello! I am a bot that can download videos from Twitter.\
                                    Send me a link to the tweet and I will send you the video.')

async def get_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Get video command handler'''
    effective_chat = update.effective_chat
    if effective_chat is None:
        return

    tweet_url = update.message.text if update.message else None
    if tweet_url is None or not tweet_url.split('/')[2] in ALLOWED_URLS:
        logging.info('Invalid Domain: %s', tweet_url.split("/")[2] if tweet_url else None)
        await context.bot.send_message(chat_id=effective_chat.id,
                                       text='Please send me a link to the tweet.')
        return

    await context.bot.send_message(chat_id=effective_chat.id,
                                   text='Wait a moment, I am downloading the video...')
    logging.info('Get video from %s', tweet_url)
    
    try:
        video_bytes = get_twitter_video(tweet_url)
    except ConnectionError as e:
        logging.error('Error downloading video: %s', e)
        await context.bot.send_message(chat_id=effective_chat.id,
                                       text='Error downloading video. Please try again later.')
        return

    except NoVideoFoundError as e:
        logging.error('No video found: %s', e)
        await context.bot.send_message(chat_id=effective_chat.id,
                                       text='No video found in the tweet. Please send another tweet.')
        return

    await context.bot.send_message(chat_id=effective_chat.id,
                                   text='Sending video...')
    await context.bot.send_video(chat_id=effective_chat.id,
                                 video=video_bytes, supports_streaming=True)

if __name__ == '__main__':
    token = os.getenv('TOKEN')
    if token is None:
        logging.error('Please set the environment variable TOKEN with the bot token.')
        sys.exit(1)

    application: Application = (ApplicationBuilder()
                                .token(token)
                                .read_timeout(timedelta(minutes=5).seconds)
                                .build())

    start_handler = CommandHandler('start', start)

    application.add_handler(start_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_video))

    application.run_polling()
