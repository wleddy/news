from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint, Response
from users.admin import login_required, table_access_required
from datetime import datetime, timedelta
import calendar
import mistune # for Markdown rendering
import os

mod = Blueprint('www',__name__, template_folder='../templates', url_prefix='/news')


def setExits():
    g.homeURL = url_for('.display')
    g.title = 'News'

@mod.route('/')
def display():
    setExits()

    rendered_html = render_markdown_for(mod,'index.md')
    
    
    return render_template('news.html',
        rendered_html=rendered_html, 
        )    


def render_markdown_for(mod,file_name):
    """Try to find the file to render and then do so"""
    rendered_html = ''
    # use similar search approach as flask templeting, root first, then local
    # try to find the root templates directory
    markdown_path = os.path.dirname(os.path.abspath(__name__)) + '/templates/{}'.format(file_name)
    if not os.path.isfile(markdown_path):
        # look in the templates directory of the calling blueprint
        markdown_path = os.path.dirname(os.path.abspath(__file__)) + '/{}/{}'.format(mod.template_folder,file_name)
    if os.path.isfile(markdown_path):
        f = open(markdown_path)
        rendered_html = f.read()
        f.close()
        rendered_html = mistune.markdown(rendered_html)
    
    return rendered_html
    
    
