from rest_framework.views import APIView
from rest_framework.response import Response
from good_first_issue.models import GoodFirstIssue
from good_first_issue.serializers import GoodFirstIssueSerializer
from datetime import datetime, timezone
from issue_metrics import constants
import requests
import json
import os


class GoodFirstIssueView(APIView):
    def get(self, request, owner, repo):
        '''
        returns good first issue rate
        '''

        good_first_issues = GoodFirstIssue.objects.all().filter(
            owner=owner,
            repo=repo
        )
        url = constants.main_url + owner + '/' + repo
        if(not good_first_issues):
            total_issues, good_first_issue = self.get_total_goodfirstissue(url)
            GoodFirstIssue.objects.create(
                owner=owner,
                repo=repo,
                total_issues=total_issues,
                good_first_issue=good_first_issue,
                date_time=datetime.now(
                    timezone.utc
                )
            )
        elif check_datetime(good_first_issues[0]):
            good_first_issues = GoodFirstIssue.objects.get(
                owner=owner,
                repo=repo
            )
            total_issues, good_first_issue = self.get_total_goodfirstissue(url)
            GoodFirstIssue.objects.filter(owner=owner, repo=repo).update(
                total_issues=total_issues,
                good_first_issue=good_first_issue,
                date_time=datetime.now(
                    timezone.utc
                )
            )
        return Response(self.get_metric(owner, repo))

    def get_total_goodfirstissue(self, url):
        '''
        returns the number of all issues and the issues with
        good first issue label
        '''
        username = os.environ['NAME']
        token = os.environ['TOKEN']

        total_issues = 0
        good_first_issue = 0
        info_repo = requests.get(url, auth=(username,
                                            token)).json()
        total_issues = info_repo["open_issues_count"]
        page = '&page=1'
        label_url = url + constants.label_good_first_issue_spaces
        result = requests.get(label_url + page,
                              auth=(username,
                                    token)).json()

        '''
        checks possibilities for different aliases of good first issue
        '''
        if result:
            good_first_issue = self.count_all_good_first_issue(
                label_url,
                result
            )
        else:
            label_url = url + constants.label_goodfirstissue
            result = requests.get(label_url + page,
                                  auth=(username,
                                        token)).json()
            if result:
                good_first_issue = self.count_all_good_first_issue(
                    label_url,
                    result
                )
            else:
                label_url = url + constants.label_good_first_issue
                result = requests.get(label_url + page,
                                      auth=(username,
                                            token)).json()
                if result:
                    good_first_issue = self.count_all_good_first_issue(
                        label_url,
                        result
                    )
        return total_issues, good_first_issue

    def count_all_good_first_issue(self, url, result):
        '''
        returns the number of good first issue in all pages
        '''
        username = os.environ['NAME']
        token = os.environ['TOKEN']
        count = 1
        page = '&page='
        good_first_issue = 0
        while result:
            count += 1
            good_first_issue += len(result)
            result = requests.get(url + page + str(count),
                                  auth=(username, token)).json()

        return good_first_issue

    def get_metric(self, owner, repo):
        '''
        returns the metric of the repository
        '''
        good_first_issues = GoodFirstIssue.objects.all().filter(
            owner=owner,
            repo=repo
        )[0]
        if good_first_issues.total_issues != 0:
            total_sample = good_first_issues.total_issues
            rate = good_first_issues.good_first_issue / total_sample
        else:
            rate = 0.0
        rate = '{"rate":\"' + str(rate) + '"}'
        rate_json = json.loads(rate)
        return rate_json


def check_datetime(good_first_issue):
    '''
    verifies if the time difference between the last update and now is
    greater than 24 hours
    '''
    datetime_now = datetime.now(timezone.utc)
    if((datetime_now - good_first_issue.date_time).days >= 1):
        return True
    return False
