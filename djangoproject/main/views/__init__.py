# from .old_w12 import category_list, category_detail, category_product
# from .fbv import category_list, category_detail
# from .cbv import CategoryList, CategoryDetail
from .auth import UserList, login, logout, CreateUserView, current_user, set_password
from .generic_cbv import  Groups, GroupDetail, SubscribedGroups, CreatedGroups, UserDetail
from .cbv import GroupPostView,post_comments,comment_detail

from .fbv import post_detail, comment_replies, post_like, comment_like, subscribe
