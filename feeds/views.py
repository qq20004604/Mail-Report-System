from .view import *
import sys
from user_rec_scan import AutoMailPush
from config.switch import MAIL_SUMMARY_PUSH_SWITCH

# 只有正常运行的时候才执行这个
# todo 目前似乎存在 bug，有空我修一下
if 'runserver' in sys.argv and MAIL_SUMMARY_PUSH_SWITCH:
    amp = AutoMailPush()
    amp.start()
