#!/bin/bash
# 监听 herdr agent；完成/卡住时把最后输出 POST 给 Grok Bot webhook routine
# 触发：done、blocked，以及 working→idle（聚焦 pane 时常跳过 done）
AGENT=${1:-gb1}
ENV_FILE="${GROKBOT_WEBHOOK_ENV:-$HOME/.config/herdr/grokbot-webhook.env}"
if [ ! -f "$ENV_FILE" ]; then
  echo "missing webhook env: $ENV_FILE" >&2
  exit 1
fi
# shellcheck disable=SC1090
. "$ENV_FILE"
if [ -z "${GROKBOT_WEBHOOK:-}" ]; then
  echo "GROKBOT_WEBHOOK empty in $ENV_FILE" >&2
  exit 1
fi
AUTH="${GROKBOT_AUTH:-}"
AUTH="${AUTH#Authorization: }"
AUTH="${AUTH#authorization: }"
case "$AUTH" in
  [Bb]earer\ *) ;;
  *) AUTH="Bearer $AUTH" ;;
esac
LAST=""
SAW_WORKING=0
post_status() {
  local S="$1"
  TEXT=$(herdr agent read "$AGENT" --source recent-unwrapped --lines 60)
  jq -n --arg a "$AGENT" --arg s "$S" --arg t "$TEXT" '{agent:$a,status:$s,text:$t}' \
    | curl -sS -X POST "$GROKBOT_WEBHOOK" -H "Authorization: $AUTH" \
        -H 'content-type: application/json' --data @- && echo "$(date) sent $AGENT $S"
}
while true; do
  S=$(herdr agent get "$AGENT" 2>/dev/null | jq -r '.result.agent.agent_status // empty')
  [ -z "$S" ] && { sleep 10; continue; }
  if [ "$S" = working ]; then
    SAW_WORKING=1
  fi
  if { [ "$S" = done ] || [ "$S" = blocked ]; } && [ "$S" != "$LAST" ]; then
    post_status "$S"
    SAW_WORKING=0
  elif [ "$S" = idle ] && [ "$SAW_WORKING" = 1 ] && [ "$LAST" = working ]; then
    # focused pane: completion often lands as idle without done
    post_status idle
    SAW_WORKING=0
  fi
  LAST=$S
  sleep 2
done
