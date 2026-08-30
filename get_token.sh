set -a
source .env
set +a

curl -sS -X POST https://api.volta-music.com/api/v1/oauth/token \
  -d "grant_type=client_credentials" \
  -d "client_id=${CLIENT_ID}" \
  -d "client_secret=${CLIENT_SECRET}" | jq '.' > config/token.json

