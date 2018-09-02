from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint, Response
from users.admin import login_required, table_access_required
from users.utils import cleanRecordID, printException, render_markdown_for, render_markdown_text
from news.models import Article
from datetime import datetime, timedelta

mod = Blueprint('news',__name__, template_folder='../templates', url_prefix='/news')


def setExits():
    g.homeURL = url_for('.display')
    g.listURL = g.homeURL
    g.editURL = url_for('.edit')
    g.deleteURL = url_for('.delete')
    g.viewURL = url_for('.view',article_handle = -1)
    g.title = 'News'

@mod.route('/', methods=["GET",])
def display():
    setExits()
    #import pdb; pdb.set_trace()
    rendered_html = render_markdown_for(__file__,mod,'news/news.md')
    
    recs = Article(g.db).select()
    
    return render_template('news/news.html',
        rendered_html=rendered_html, recs = recs,
        )    

@mod.route('/view', methods=["GET",])
@mod.route('/view/', methods=["GET",])
@mod.route('/view/<article_handle>', methods=["GET",])
@mod.route('/view/<article_handle>/', methods=["GET",])
def view(article_handle=-1):
    setExits()
    
    rec = Article(g.db).get(article_handle)
    if not rec:
        flash("That article could not be found.")
        return redirect(g.homeURL)
        
    g.title = rec.title
    if len(rec.title) > 20:
        g.title = rec.title[:20] + "..."
    
    rendered_html = render_markdown_text(rec.words)
        
    return render_template('news/article.html',
        rendered_html=rendered_html, rec=rec,
        )       
    
@mod.route('/edit', methods=["GET","POST"])
@mod.route('/edit/', methods=["GET","POST"])
@mod.route('/edit/<article_handle>', methods=["GET","POST"])
@mod.route('/edit/<article_handle>/', methods=["GET","POST"])
@table_access_required(Article)
def edit(article_handle='0'):
    setExits()
    g.title = "Article"
    articles = Article(g.db)
    
    #import pdb; pdb.set_trace()
    rec_id = cleanRecordID(article_handle)
    rec = articles.get(article_handle)
    if not rec and not rec_id == 0:
        flash('Could not find that artcle')
        return redirect(g.homeURL)
    
    if rec_id == 0:
        rec = articles.new()
    
    ##Is the handle an existing slug?
    #if len(article_handle) > 0:
    #    # The slug is arbitrary text, so be careful!!!
    #    sql = 'select * from article where slug = ?'
    #    rec = articles.select_one_raw(sql,(article_handle,))
    #if not rec:
    #    rec_id = cleanRecordID(article_handle)
    #    if rec_id < 0:
    #        #is the handle < o? ... bad request, go home
    #        flash('That is not a valid article slug')
    #        return redirect(g.homeURL)
    #        
    #    if rec_id > 0:
    #        rec = articles.get(rec_id)
    #        if not rec:
    #            flash('That is not a valid article id')
    #            return redirect(g.homeURL)
    #    else:
    #        #is the handle zero?  ... make a new record
    #        rec = articles.new()
    
    
    #Is there a form?
    if request.form:
        #import pdb; pdb.set_trace()
        
        articles.update(rec,request.form)
        if valid_form(rec):
            try:
                articles.save(rec)
                g.db.commit()
                return redirect(g.homeURL)
            except Exception as e:
                g.db.rollback()
                flash(printException("Error when attepting to save article.",e))
                
    
    return render_template('news/article_edit.html',rec=rec)

@mod.route('/delete/', methods=['GET','POST'])
@mod.route('/delete/<int:rec_id>/', methods=['GET','POST'])
@table_access_required(Article)
def delete(rec_id=None):
    setExits()
    g.title = "Article"
    
    if rec_id == None:
        rec_id = request.form.get('id',request.args.get('id',-1))
    
    rec_id = cleanRecordID(rec_id)
    if rec_id <=0:
        flash("That is not a valid record ID")
        return redirect(g.listURL)
        
    rec = Article(g.db).get(rec_id)
    if not rec:
        flash("Record not found")
    else:
        Article(g.db).delete(rec.id)
        g.db.commit()
        
    return redirect(g.listURL)


def valid_form(rec):
    valid_form = True
    slug = request.form.get('slug','').strip()
    title = request.form.get('title','').strip()
    
    if not slug and title:
        slug = title.lower()
        for s in ' /<>"\'#.()':
            slug = slug.replace(s,'-')
        rec.slug = slug
    
    if not title:
        flash("The title may not be empty")
        valid_form = False
        
    if not slug:
        flash("The slug line may not be empty")
        valid_form = False
        
    if slug:
        sql = 'select * from article where slug = ? and id <> ?'
        find_slug = Article(g.db).select_raw(sql,(slug,rec.id))
        if find_slug and len(find_slug) > 0:
            flash("The slug line must be unique")
        
    
    return valid_form
    
    
