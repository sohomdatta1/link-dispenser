import os

USERAGENT = 'Wikimedia-Toolforge-Link-Dispenser/1.0 (https://w.wiki/MzLY; soda@toolforge.org)'
TOKEN_TO_ATTRIBUTE_TO_TOOL_OWNER = os.getenv("TOKEN_TO_ATTRIBUTE_TO_TOOL_OWNER", "")
if 'NOTDEV' not in os.environ or 'DOCKER' in os.environ:
    HEADERS = { 'User-Agent': USERAGENT, 'Authorization': f'Bearer {TOKEN_TO_ATTRIBUTE_TO_TOOL_OWNER}' }
else:
    HEADERS = { 'User-Agent': USERAGENT }