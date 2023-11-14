from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from database.serializers import *
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from rest_framework.authentication import TokenAuthentication
from django.http import JsonResponse
from rest_framework import generics, status
from django.contrib.postgres.search import SearchVector
from database.models import *

# from nltk.corpus import wordnet as wn
# import nltk
#
# nltk.download('wordnet')

# Create your views here.

# Class based view to register user
class SignUpAPIView(generics.CreateAPIView):
    permission_classes = (AllowAny,) 
    serializer_class = RegisterSerializer

# Class based view to get User details using Token Authentication
class UserDetailAPI(APIView):
  authentication_classes = (TokenAuthentication,)
  permission_classes = (IsAuthenticated,)

  def get(self, request, *args, **kwargs):
    user = User.objects.get(id=request.user.id)
    serializer = UserSerializer(user)

    return Response(serializer.data)

class ChangePasswordView(generics.UpdateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user

class ChangeProfileSettingsView(generics.UpdateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = BasicUser.objects.all()
    serializer_class = ChangeProfileSettingsSerializer

    def get_object(self):
        return self.request.user.basicuser
      
class NodeAPIView(APIView):
  
    def get(self, request):
        id = int(request.GET.get("node_id"))
        node = Node.objects.filter(node_id=id)
        if node.count() == 0:
            return JsonResponse(
                {"message": "There is no node with this id."}, status=404
            )
        elif node.first().removed_by_admin:
            return JsonResponse(
                {"message": "The node is removed by admin."}, status=404
            )
        node = node.first()
        serializer = NodeSerializer(node)
        return Response(serializer.data)

def search(request):
    search = request.GET.get("query")
    search_type = request.GET.get("type")
    if search == None or search == "":
        return JsonResponse({'status': 'Title to search must be given.'}, status=400)
    if search_type == None or search_type == "":
        return JsonResponse({'status': 'Type to search must be given.'}, status=400)
    if search_type != 'node' and search_type != 'author' and search_type != 'all' and search_type != 'by':
        return JsonResponse({'status': 'invalid search type.'}, status=400)
    search_elements = search.split()
    # similars = [] # TODO ADVANCED SEARCH
    # also_sees = []
    #
    # for element in search_elements:
    #     if  len(wn.synsets(element)) != 0:
    #         for el in wn.synsets(element)[0].also_sees():
    #             el = el.name()
    #             el = el[:el.find('.')]
    #             also_sees.append(el)
    #         for el in wn.synsets(element)[0].similar_tos():
    #             el = el.name()
    #             el = el[:el.find('.')]
    #             similars.append(el)
    # start search with exact search
    nodes = []

    if search_type == 'by' or search_type == 'all':
        # print(search_elements)
        for el in search_elements:
            res_name = User.objects.filter(first_name__icontains=el)
            res_surname = User.objects.filter(last_name__icontains=el)
            for e in res_name:
                if Contributor.objects.filter(user_id=e.id).count() != 0:
                    cont_nodes = Contributor.objects.get(user_id=e.id).NodeContributors.all()
                    for node in cont_nodes:
                        nodes.append(node.node_id)

            for e in res_surname:
                if Contributor.objects.filter(user_id=e.id).count() != 0:
                    cont_nodes = Contributor.objects.get(user_id=e.id).NodeContributors.all()
                    for node in cont_nodes:
                        nodes.append(node.node_id)


    contributors = []
    if search_type == 'node' or search_type == 'all':
        for el in search_elements:
            res = Node.objects.annotate(search=SearchVector("node_title")).filter(node_title__icontains=el)
            for e in res:
                nodes.append(e.node_id)
    if search_type == 'author' or search_type == 'all':    # TODO This method is too inefficient
        for el in search_elements:
            res_name = User.objects.filter(first_name__icontains=el)
            res_surname = User.objects.filter(last_name__icontains=el)
            for e in res_name:
                if Contributor.objects.filter(user_id=e.id).count() != 0:
                    contributors.append(e.username)
            for e in res_surname:
                if Contributor.objects.filter(user_id=e.id).count() != 0:
                    contributors.append(e.username)
    contributors = list(set(contributors))
    nodes = list(set(nodes))
    res_authors = []
    for cont in contributors:
        user = User.objects.get(username=cont)
        cont = Contributor.objects.get(user=user)
        res_authors.append({'name': user.first_name,
                        'surname': user.last_name, 'username': cont.user.username , 'id': cont.id})
    node_infos = []
    for node_id in nodes:
        node = Node.objects.get(node_id=node_id)
        authors = []
        for cont in node.contributors.all():
            user = User.objects.get(id=cont.user_id)
            authors.append({'name': user.first_name,
                            'surname': user.last_name, 'username': user.username, 'id': cont.id})
        node_infos.append({'id': node_id, 'title': node.node_title, 'date': node.publish_date, 'authors': authors})
    return JsonResponse({'nodes' : node_infos , 'authors' :res_authors },status=200)



def get_profile(request):
    mail = request.GET.get("mail")
    check = User.objects.filter(username=mail)
    if check.count() == 0:
        return JsonResponse({'message': "User with this mail adress does not exist."}, status=400)
    user = User.objects.get(username=mail)
    basic_user = BasicUser.objects.get(user_id=user.id)
    cont =  Contributor.objects.filter(user_id=user.id)
    nodes = []
    asked_questions = []
    answered_questions = []
    if cont.count() != 0:
        user_nodes = Node.objects.filter(contributors=cont[0].id)
        for node in user_nodes:
            nodes.append(node.node_id)
        user_answered_qs = Question.objects.filter(answerer=cont[0].id)
        for ans in user_answered_qs:
            asker_user = User.objects.get(id=ans.asker.user_id)
            answerer_user = User.objects.get(id=ans.answerer.user_id)
            answered_questions.append({'id':ans.id, 'ask_date':ans.created_at, 'node_id':ans.node.node_id, 'node_title':ans.node.node_title, 'node_date':ans.node.publish_date,
                                       'asker_id':ans.asker.id,'asker_name':asker_user.first_name,'asker_surname':asker_user.last_name,
                                       'asker_mail':asker_user.username,'answerer_name':answerer_user.first_name,'answerer_surname':answerer_user.last_name,
                                       'answerer_mail':answerer_user.username,
                                           'answerer_id':ans.answerer.id, 'question_content':ans.question_content,
                                       'answer_content':ans.answer_content,'answer_date':ans.answered_at,'is_answered':1})

    user_asked_qs = Question.objects.filter(asker=cont[0].id)
    for q in user_asked_qs:
        asker_user = User.objects.get(id=q.asker.user_id)
        if q.answerer == None:
            asked_questions.append(
                {'id': q.id, 'ask_date': q.created_at, 'node_id': q.node.node_id, 'node_title': q.node.node_title,
                 'node_date': q.node.publish_date,
                 'asker_id': q.asker.id, 'asker_name': asker_user.first_name, 'asker_surname': asker_user.last_name,
                 'asker_mail': asker_user.username,  'question_content': q.question_content, 'is_answered': 0})
            continue
        answerer_user = User.objects.get(id=q.answerer.user_id)
        asked_questions.append(
            {'id': q.id, 'ask_date': q.created_at, 'node_id': q.node.node_id, 'node_title': q.node.node_title,
             'node_date': q.node.publish_date,
             'asker_id': q.asker.id, 'asker_name': asker_user.first_name, 'asker_surname': asker_user.last_name,
             'asker_mail': asker_user.username, 'answerer_name': answerer_user.first_name,
             'answerer_surname': answerer_user.last_name,
             'answerer_mail': answerer_user.username,
             'answerer_id': q.answerer.id, 'question_content': q.question_content,
             'answer_content': q.answer_content, 'answer_date': q.answered_at, 'is_answered':1})

    node_infos = []
    for node_id in nodes:
        node = Node.objects.get(node_id=node_id)
        authors = []
        for cont in node.contributors.all():
            user = User.objects.get(id=cont.user_id)
            authors.append({'name': user.first_name, 'surname': user.last_name, 'username': user.username})
        node_infos.append({'id':node_id,'title':node.node_title,'date':node.publish_date,'authors':authors})

    return JsonResponse({'name':user.first_name,
                         'surname':user.last_name,
                         'bio':basic_user.bio,
                         'nodes': node_infos,
                         'asked_questions':asked_questions,
                         'answered_questions':answered_questions},status=200)

def get_proof_from_id(request):
    id = int(request.GET.get("proof_id"))
    proof = Proof.objects.filter(proof_id=id)
    if proof.count() == 0:
        return JsonResponse({'message':'There is no proof with this id.'},status=404)
    data = {'proof_id': proof[0].proof_id,
            'proof_title': proof[0].proof_title,
            'proof_content': proof[0].proof_content,
            'is_valid': proof[0].is_valid,
            'is_disproof': proof[0].is_disproof,
            'publish_date': proof[0].publish_date,
            }
    return JsonResponse(data, status=200)

def get_theorem_from_id(request):
    id = int(request.GET.get("theorem_id"))
    theorem = Theorem.objects.filter(theorem_id=id)
    if theorem.count() == 0:
        return JsonResponse({'message':'There is no theorem with this id.'},status=404)

    data = {'theorem_id': theorem[0].theorem_id,
            'theorem_title': theorem[0].theorem_title,
            'theorem_content': theorem[0].theorem_content,
            'publish_date': theorem[0].publish_date,
            }
    return JsonResponse(data, status=200)


def get_contributor_from_id(request):
    id = int(request.GET.get("id"))
    cont = Contributor.objects.filter(id=id)
    if cont.count() == 0:
        return JsonResponse({'message':'There is no contributor with this id.'},status=404)
    user = User.objects.get(id=cont[0].user_id)
    data = {'id': cont[0].id,
            'username': user.username,
            'name': user.first_name,
            'surname': user.last_name,
            }
    return JsonResponse(data, status=200)