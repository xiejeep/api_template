# -----------------------------------------------------------------------------
# AUTHENTICATION
# -----------------------------------------------------------------------------

WORKSPACE_AUTH_REQUIRE_LOGIN = not DEBUG
TENANT_LIMIT_LOGIN_PAGE = False

# Wechat configuration
WECHAT_APP_ID = os.getenv('WECHAT_APP_ID', '')
WECHAT_APP_SECRET = os.getenv('WECHAT_APP_SECRET', '')

# Wechat Mini Program configuration
WECHAT_MINI_APP_ID = os.getenv('WECHAT_MINI_APP_ID', '')
WECHAT_MINI_APP_SECRET = os.getenv('WECHAT_MINI_APP_SECRET', '')

# ----------------------------------------------------------------------------- 