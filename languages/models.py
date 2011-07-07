from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import dictsort
from django.db.models import permalink
from django.contrib.auth.models import User

class LanguageManager(models.Manager):
    
    def get_unused(self, project):
        from django.db import connection
        cursor = connection.cursor()

        cursor.execute("SELECT l.id, l.name, l.code "\
                       "FROM language l "\
                       "LEFT JOIN teams t "\
                       "on t.language_id = l.id AND t.project_id=%s "\
                       "WHERE t.id IS NULL "\
                       "ORDER BY l.name",
                       [project.id])
        langs = []
        for row in cursor.fetchall():
            l = self.model(id=row[0],name=row[1], code=row[2])
            langs.append(l)
        return langs 
    
class Language(models.Model):
    """
    A spoken language or dialect, with a distinct locale.
    >>> l = Language.objects.create(code="es",name="Spanish")
    >>> l = Language.objects.get(code="es")
    >>> l
    <Language: Spanish>
    >>> l.delete()
    """
    name = models.CharField(unique=True, max_length=50,
        help_text="The name of the language including dialect, script, etc.")
    code = models.CharField(unique=True, max_length=50,
        help_text=("The primary language code, used in file naming, etc."
                   "(eg. pt_BR for Brazilian Portuguese.)"))

    objects = LanguageManager()
    
    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.code)

    def __repr__(self):
        return u'<Language: %s>' % self.name
    
    class Meta:
        db_table  = 'language'
        ordering  = ('name',)

    @permalink
    def get_absolute_url(self):
        return ('language_detail', None, { 'slug': self.code })
