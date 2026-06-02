from flask import Blueprint, render_template

shopping_bp = Blueprint('shopping', __name__, url_prefix='/shopping')


@shopping_bp.route('/')
def list_page():
    return render_template('shopping/list.html')
