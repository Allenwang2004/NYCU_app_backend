from flask_admin.contrib.sqla import ModelView
from wtforms.fields import BooleanField
from flask import session, redirect, url_for

class ProtectedModelView(ModelView):
    column_list = ['email', 'name', 'is_verified', 'is_filled']
    column_searchable_list = ['email', 'name']
    form_excluded_columns = ['password']
    form_excluded_columns = ['is_verified', 'is_filled']
    column_default_sort = ('id', True)
    can_create = False  
    can_delete = True  
    can_edit = False    
    def is_accessible(self):
        return session.get("admin_logged_in", False)

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("admin_auth.admin_login"))

class MoodLogView(ModelView):
    column_list = ('user_name','date', 'mood', 'diary')  # 顯示 user_name 而不是 user_id
    column_labels = {
        'user_name': '使用者名稱',
        'date': '日期',
        'mood': '心情',
        'diary': '日記'
    }

    def _user_name_formatter(view, context, model, name):
        return model.user.name if model.user else '無使用者'

    column_formatters = {
        'user_name': _user_name_formatter
    }

    # 為了能讓 column_formatters 找到這個虛擬欄位
    def scaffold_list_columns(self):
        columns = super().scaffold_list_columns()
        if 'user_name' not in columns:
            columns.append('user_name')
        return columns