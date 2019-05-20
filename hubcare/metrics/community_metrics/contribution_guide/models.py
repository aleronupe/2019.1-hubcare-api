from django.db import models


class ContributionGuide(models.Model):

    owner = models.CharField(max_length=200)
    repo = models.CharField(max_length=200)
    contribution_guide = models.BooleanField(default=False)
    date_time = models.DateTimeField(default=None)

    class Meta:
        unique_together = (('owner', 'repo'),)
