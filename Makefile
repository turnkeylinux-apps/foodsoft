WEBMIN_FW_TCP_INCOMING = 22 80 443 12320 12321

COMMON_CONF = yarn
COMMON_OVERLAYS = yarn

include $(FAB_PATH)/common/mk/turnkey/rails.mk
include $(FAB_PATH)/common/mk/turnkey.mk
