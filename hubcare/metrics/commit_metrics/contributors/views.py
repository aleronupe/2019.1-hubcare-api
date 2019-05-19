from rest_framework.views import APIView
from rest_framework.response import Response
from contributors.models import DifferentsAuthors
from contributors.serializers \
    import DifferentsAuthorsSerializers
from contributors.constants import *
from datetime import datetime, timezone, timedelta
import requests
import os


class DifferentsAuthorsView(APIView):
    '''
        Get the number of different authors from a repo using GitHub Api of the
        last 30 days and return the total sum
        Input: owner, repo
        Output: A list with the different authors o the last 30 days
        and save data
    '''
    def get(self, request, owner, repo):
        '''
            Check the existence of the repo, if so get the number different
            authors of the last 30 days and save the data.
            Input: owner, repo
            Output: A list with the different authors o the last 30 days
            and save data
        '''
        differentsauthors = DifferentsAuthors.objects.all().filter(
            owner=owner,
            repo=repo
        )
        differentsauthors_serialized = DifferentsAuthorsSerializers(
            differentsauthors,
            many=True)
        username = os.environ['NAME']
        token = os.environ['TOKEN']
        github_request = requests.get(
            'https://api.github.com/repos/' + owner + '/' + repo + '/commits',
            auth=(username, token))
        github_data = github_request.json()
        present = datetime.today()
        days = timedelta(days=month_days)
        commitsLastThirtyDays = []
        authorsCommits = []
        out = []
        listCommits = []
        listJson = []

        if (github_request.status_code >= 200 and
                github_request.status_code <= 299):

            for commit in github_data:
                commit['commit']['committer']['date'].split('T')[0]
                past = datetime.strptime(
                    commit['commit']['committer']['date'],
                    "%Y-%m-%dT%H:%M:%SZ")
                commitsDay = present - days
                if((past > commitsDay)):
                    commitsLastThirtyDays.append(
                        commit['commit']['committer']['date'].split('T')[0])
                    authorsCommits.append(commit['commit']['author']['email'])
            authorsDistintCommits = set(authorsCommits)
            for author in authorsDistintCommits:
                listJson.append({'author': author,
                                'numberCommits': authorsCommits.count(author)})
        return Response(listJson)

    def post(self, request, owner, repo):

        print('time 1: ', datetime.now())

        username = os.environ['NAME']
        token = os.environ['TOKEN']

        time_now = datetime.now()
        period = timedelta(weeks=TOTAL_WEEKS)
        since = str(time_now-period).replace(' ', '-')

        url_since = '/commits?since='
        url_page = '&per_page=100&page='
        page = 1
        all_commits = []
        while True:
            commits = requests.get(
                MAIN_URL + owner + '/' + repo +
                url_since + since +
                url_page + str(page),
                auth=(username, token)
            ).json()

            if commits:
                all_commits += commits
                page += 1
            else:
                break

        print('time 2: ', datetime.now())

        return Response(all_commits)
