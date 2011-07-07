from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from common.decorators import permission_required_with_403
from common.view.decorators import render
from news.forms import ArticleForm
from news.models import Article

@permission_required_with_403('news.add')
@render('news/editor.html')
def news_add(request):
    
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            n = form.save(request.user)
            return HttpResponseRedirect(n.get_absolute_url())
    else:
        form = ArticleForm(initial={'author': request.user.pk})
        
    return {'form': form}

@render('news/view.html')
def news_view(request, slug):
    return {'article': get_object_or_404(Article,slug=slug)}
