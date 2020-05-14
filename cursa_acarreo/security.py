from functools import wraps
from flask_login import current_user
from flask import abort


def mustbe_admin(view_function):
    @wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        if current_user.is_admin:
            return view_function(*args, **kwargs)
        else:
            # return render_template('403.html')
            abort(403)
    return decorated_function
