# TikTok data

## Setup

Run on `Python 3.11.6`. The `requirements.txt` file might have more packages than are
actually being used.

You'll need to have a Chrome profile that's already logged into TikTok. You can either...

1. Set up a Chrome profile locally - TikTok might prevent you from doing so as you've logged in too many times.
   And the blocking seems to be IP-based and it takes a while.
2. Copy your existing Chrome user data directory (go to `chrome://version`) here, then remove the profiles you
   don't need and change the folder name of the one you wish to use to `Default`

## Deploying it

There are 2 challenges.

### Scheduled tasks in Dockerised application

There are a couple of ways of doing it:

1. Web server - involves more setup
2. Cron jobs - simpler, but Docker containers aren't made for this; you won't notice if the cron job fails

### Chrome profile

The application needs to have the Chrome profile directory. You can't add it to git though because
it contains sensitive information from the browser. One way to overcome this is to upload the
directory to an SFTP server like [SFTPGo](https://github.com/drakkan/sftpgo), then have the application
download the contents.
