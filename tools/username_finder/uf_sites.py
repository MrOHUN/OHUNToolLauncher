SITES = [
    {
        "name": "GitHub",
        "url": "https://github.com/{}",
        "errorType": "status_code",
    },
    {
        "name": "GitLab",
        "url": "https://gitlab.com/{}",
        "errorType": "status_code",
    },
    {
        "name": "Instagram",
        "url": "https://www.instagram.com/{}",
        "errorType": "message",
        "errorMsg": "Sorry, this page isn't available",
        # Oddiy sahifa, login kerak emas
    },
    {
        "name": "TikTok",
        "url": "https://www.tiktok.com/@{}",
        "errorType": "message",
        "errorMsg": "\"statusCode\":10202",
    },
    {
        "name": "Reddit",
        "url": "https://www.reddit.com/user/{}/about.json",
        "errorType": "json_key",
        "errorKey": "error",
    },
    {
        "name": "Pinterest",
        "url": "https://www.pinterest.com/{}",
        "errorType": "message",
        "errorMsg": "Sorry! We couldn't find that page",
    },
    {
        "name": "Telegram",
        "url": "https://t.me/{}",
        "errorType": "message",
        "errorMsg": "tgme_page_description",
        "checkMode": "present",
    },
    {
        "name": "YouTube",
        "url": "https://www.youtube.com/@{}",
        "errorType": "message",
        "errorMsg": "VisitorData",
        "checkMode": "present",
    },
    {
        "name": "SoundCloud",
        "url": "https://soundcloud.com/{}",
        "errorType": "status_code",
    },
    {
        "name": "Twitch",
        "url": "https://www.twitch.tv/{}",
        "errorType": "message",
        "errorMsg": "isLiveBroadcast",
        "checkMode": "present",
    },
    {
        "name": "Steam",
        "url": "https://steamcommunity.com/id/{}",
        "errorType": "message",
        "errorMsg": "The specified profile could not be found.",
    },
    {
        "name": "Medium",
        "url": "https://medium.com/@{}",
        "errorType": "status_code",
    },
    {
        "name": "Dev.to",
        "url": "https://dev.to/{}",
        "errorType": "status_code",
    },
    {
        "name": "Replit",
        "url": "https://replit.com/@{}",
        "errorType": "status_code",
    },
    {
        "name": "Keybase",
        "url": "https://keybase.io/{}",
        "errorType": "status_code",
    },
    {
        "name": "Pastebin",
        "url": "https://pastebin.com/u/{}",
        "errorType": "message",
        "errorMsg": "Not Found",
    },
    {
        "name": "Linktree",
        "url": "https://linktr.ee/{}",
        "errorType": "message",
        "errorMsg": "\"statusCode\":404",
    },
    {
        "name": "Imgur",
        "url": "https://api.imgur.com/3/account/{}",
        "errorType": "json_key",
        "errorKey": "error",
        "headers_extra": {"Authorization": "Client-ID 546c25a59c58ad7"},
    },
    {
        "name": "Flickr",
        "url": "https://www.flickr.com/people/{}",
        "errorType": "status_code",
    },
    {
        "name": "Vimeo",
        "url": "https://vimeo.com/{}",
        "errorType": "status_code",
    },
]
