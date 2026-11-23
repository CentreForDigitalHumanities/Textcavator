from django.db import models

class NewsItem(models.Model):
    '''
    News item to publish on the user interface. Can be used to announce new features,
    corpora, etc.
    '''

    class Meta:
        ordering = ['-date']


    date = models.DateField(
        auto_now_add=True,
    )
    title = models.CharField(
    )
    content = models.TextField(
        help_text='Message content. Supports markdown formatting.',
    )

    def __str__(self):
        return self.title
