# from .get_user_name import get_user_name
# from .query_history_feeds import query_history_feeds
# from .send_feeds import send_feeds
import os
import pkgutil

pkgpath = os.path.dirname(__file__)
pkgname = os.path.basename(pkgpath)

# 动态引入，效果类似以下（不会引入__init__.py）
# from .get_user_name import get_user_name
# from .query_history_feeds import query_history_feeds
# from .send_feeds import send_feeds
for _, file, _ in pkgutil.iter_modules([pkgpath]):
    if file[0]!='_':
        exec("from .%s import %s" % (file, file))

