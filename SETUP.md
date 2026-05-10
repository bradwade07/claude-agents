# Bradbot Setup Checklist

Fill `secrets/.env` with these tokens before first run.

## 1. Anthropic API Key

- Visit https://console.anthropic.com
- API Keys → Create Key
- Add billing/credits (separate from Pro subscription if you have one)
- Paste into `secrets/.env`:
  ```
  ANTHROPIC_API_KEY=sk-ant-...
  ```

## 2. Discord Bot

### Create bot
1. https://discord.com/developers/applications → New Application
2. Name: "Bradbot"
3. Left sidebar → **Bot**
4. **Reset Token** → copy token → paste into `secrets/.env`:
   ```
   BRADBOT_DISCORD_TOKEN=...
   ```
5. **Privileged Gateway Intents** → enable **MESSAGE CONTENT INTENT** (required)

### Invite bot to your server
1. Left sidebar → **OAuth2** → **URL Generator**
2. Scopes: `bot`
3. Bot Permissions: `Send Messages`, `Read Message History`, `View Channels`
4. Copy URL → open in browser → select your server → authorize

### Get channel ID
1. Discord → Settings → Advanced → enable **Developer Mode**
2. Right-click target channel → **Copy Channel ID**
3. Paste into `secrets/.env`:
   ```
   BRADBOT_CHANNEL_ID=123456789012345678
   ```

## 3. ClickUp

1. ClickUp → avatar (bottom-left) → Settings
2. **Apps** → **API Token** → Generate
3. Paste into `secrets/.env`:
   ```
   CLICKUP_API_KEY=pk_...
   ```
- Inbox list ID `901415799153` is already hardcoded in `bradbot/tools/clickup.py`

## 4. Google Cloud Console (Calendar)

1. https://console.cloud.google.com → create project (or pick existing)
2. **APIs & Services** → **Library** → enable **Google Calendar API**
3. **Credentials** → **Create Credentials** → **OAuth client ID**
4. Application type: **Desktop app** → name it "Bradbot"
5. Download JSON → save as `secrets/google/credentials.json`
6. On first bot run, browser opens for OAuth approval
7. Token auto-cached at `secrets/google/token.json`

## 5. Run

```bash
.venv/Scripts/python.exe -m bradbot
```

Bot logs in, posts ready message, starts scheduler. Send any message in configured Discord channel → Bradbot replies.

## Verification

In your Discord channel, try:
- `remember grocery: milk, eggs` → memory tool fires
- `what's on my grocery list?` → recall works
- `add task: test bradbot` → ClickUp task created
- `what's on my calendar today?` → Calendar events returned
