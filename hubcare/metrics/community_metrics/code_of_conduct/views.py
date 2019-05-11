from rest_framework.views import APIView
from rest_framework.response import Response
from code_of_conduct.models import CodeOfConduct
from code_of_conduct.serializers import CodeOfConductSerializer
from datetime import datetime, timezone
import requests
import os
from community_metrics.functions \
    import check_date, filter_object, serialized_object
from community_metrics.constants import URL_API, HTTP_OK


class CodeOfConductView(APIView):
    def get(self, request, owner, repo):
        '''
        return if a repository has a code of conduct or not
        '''
        code_of_conduct = filter_object(CodeOfConduct)

        username = os.environ['NAME']
        token = os.environ['TOKEN']

        if(not code_of_conduct):
            url = '/contents/.github/CODE_OF_CONDUCT.md'
            result = URL_API + owner + '/' + repo + url
            github_request = requests.get(result, auth=(username,
                                                        token))
            if(github_request.status_code == HTTP_OK):
                CodeOfConduct.objects.create(
                    owner=owner,
                    repo=repo,
                    code_of_conduct=True,
                    date_time=datetime.now(timezone.utc)
                )
            else:
                CodeOfConduct.objects.create(
                    owner=owner,
                    repo=repo, code_of_conduct=False,
                    date_time=datetime.now(timezone.utc)
                )

        elif(check_date(code_of_conduct)):
            url = '/contents/.github/CODE_OF_CONDUCT.md'
            result = URL_API + owner + '/' + repo + url
            github_request = requests.get(result, auth=(username,
                                                        token))
            if(github_request.status_code == HTTP_OK):
                CodeOfConduct.objects.filter(owner=owner, repo=repo).update(
                    owner=owner,
                    repo=repo,
                    code_of_conduct=True,
                    date_time=datetime.now(timezone.utc)
                )
            else:
                CodeOfConduct.objects.filter(owner=owner, repo=repo).update(
                    owner=owner,
                    repo=repo,
                    code_of_conduct=False,
                    date_time=datetime.now(timezone.utc)
                )

        code_of_conduct = CodeOfConduct.objects.all().filter(
            owner=owner,
            repo=repo
        )
        code_of_conduct_serialized = serialized_object(
            CodeOfConductSerializer,
            code_of_conduct
        )

        return Response(code_of_conduct_serialized.data[0])
