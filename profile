{
    "id": "YOUR_ID",
    "secret": "YOUR_SECRET",
    "auth_url": "https://iam.mcafee-cloud.com/iam/v1.1/token",
    "api_url": "https://api.manage.trellix.com/epo/v2/",
    "api_short_url": "https://api.manage.trellix.com",
    "auth_headers": {
        "Content-Type": "application/x-www-form-urlencoded"
    },
    "api_headers": {
        "Content-Type": "application/vnd.api+json",
        "x-api-key": "YOUR_X-API-KEY",
        "Authorization": "Bearer "
    },
    "auth_payload": {
        "grant_type": "client_credentials",
        "scope": "epo.device.r epo.device.w epo.tags.r epo.tags.w epo.evt.r",
        "audience": "mcafee"
    },
    "device_page_limit": 20,
    "events_page_limit": 1000,
    "events_cursor": "",
    "log_level": "WARN",
    "log_path": ""
}