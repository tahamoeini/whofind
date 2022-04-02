from email import message
from urllib import response
from django.shortcuts import render
import json
import requests
import uuid
import urllib.parse
from whofind.settings import *
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import *
from rest_framework.permissions import *
from rest_framework.response import Response
from .models import *

if (CREDENTIALS['yandex']):
    yandex = CREDENTIALS['yandex']
    yandexUsername = yandex['username']
    yandexKey = yandex['key']
if(CREDENTIALS['google']):
    google = CREDENTIALS['google']
    googleAPIKey = google['api_key']
    googleClientId = google['client_id']
if(CREDENTIALS['rapidapi']):
    rapidapi = CREDENTIALS['rapidapi']
    rapidKey = rapidapi['key']


@api_view(['GET'])
@permission_classes([AllowAny])
def crawl(request):
    user = request.user
    if request.method == 'GET':
        queryParams = request.query_params
        query = queryParams['q']
        queryKeyword = Keywords.objects.get_or_create(text=query)
        responseText = ""
        try:
            response = rapidGoogle(rapidKey, queryKeyword[0])
            responseText += response['message']
            rapidGooglestatusCode = response['statusCode']
        except:
            pass
        try:
            response = rapidMassGoogle(rapidKey, queryKeyword[0])
            responseText += response['message']
            rapidMassGooglestatusCode = response['statusCode']
        except:
            pass
        if(not rapidGooglestatusCode == 200 or not rapidMassGooglestatusCode == 200):
            status = 400
        else:
            status = 200
        return Response({
            responseText
        }, status=status)


@api_view(['GET'])
@permission_classes([AllowAny])
def recrawl(request):
    user = request.user
    if request.method == 'GET':
        queryKeywords = Keywords.objects.all()
        responseText = ""
        for queryKeyword in queryKeywords:
            try:
                response = rapidGoogle(rapidKey, queryKeyword)
                responseText += response['message']
                rapidGooglestatusCode = response['statusCode']
            except:
                pass
            try:
                response = rapidMassGoogle(rapidKey, queryKeyword)
                responseText += response['message']
                rapidMassGooglestatusCode = response['statusCode']
            except:
                pass
        if(not rapidGooglestatusCode == 200 or not rapidMassGooglestatusCode == 200):
            status = 400
        else:
            status = 200
        return Response({
            responseText
        }, status=status)


# Yandex
# yandexSearch(yandexUsername, yandexKey, queryKeyword)

def rapidMassGoogle(rapidKey, queryKeyword):
    responseText = ""
    queryText = queryKeyword.text
    url = "https://google-search3.p.rapidapi.com/api/v1/search/q="+queryText+"&num=100"
    headers = {
        "X-User-Agent": "desktop",
        "X-Proxy-Location": "US",
        "X-RapidAPI-Host": "google-search3.p.rapidapi.com",
        "X-RapidAPI-Key": rapidKey
    }
    response = requests.request("GET", url, headers=headers)
    if (response.status_code == 200):
        responseJson = response.text
        resultDict = json.loads(responseJson)
        results = resultDict['results']
        position = 1
        for result in results:
            try:
                domain = urllib.parse.urlparse(result['link']).netloc
                if(Link.objects.filter(link=result['link']).exists()):
                    link = Link.objects.get(link=result['link'])
                    link.domain = domain
                    link.description = result['description']
                    link.title = result['title']
                else:
                    link = Link.objects.create(link=result['link'], domain=domain,
                                                description=result['description'], title=result['title'])
            except:
                responseText += "Link Creation of " + \
                    result['link']+" Got Error!\n"
            try:
                if(LinkPosition.objects.filter(queryKeyword=queryKeyword).filter(link=link).exists()):
                    linkPosition = LinkPosition.objects.get(
                        queryKeyword=queryKeyword, link=link)
                    linkPosition.position = int(position)
                    linkPosition.save()
                else:
                    linkPosition = LinkPosition.objects.create(
                        queryKeyword=queryKeyword, link=link, position=int(position))
            except:
                responseText += "Link Position Creation of " + \
                    result['link']+" Got Error!\n"
            position += 1
    else:
        return {
            'message': response.text,
            'statusCode': response.status_code
        }
    if(responseText == ""):
        return {
            'message': "Search with Mass Rapid Google Completed Successfuly",
            'statusCode': status.HTTP_200_OK
        }
    else:
        return {
            'message': responseText,
            'statusCode': status.HTTP_400_BAD_REQUEST
        }


def rapidGoogle(rapidKey, queryKeyword):
    responseText = ""
    queryText = queryKeyword.text
    url = "https://google-search1.p.rapidapi.com/google-search"
    querystring = {"hl": "en", "q": queryText, "gl": "us"}
    headers = {
        "X-RapidAPI-Host": "google-search1.p.rapidapi.com",
        "X-RapidAPI-Key": rapidKey
    }
    response = requests.request(
        "GET", url, headers=headers, params=querystring)
    if (response.status_code == 200):
        responseJson = response.text
        resultDict = json.loads(responseJson)
        results = resultDict['organic']
        relatedKeywords = resultDict['relatedKeywords']
        if(RelatedKeywords.objects.filter(queryKeyword=queryKeyword).exists()):
            queryRelatedKeywords = RelatedKeywords.objects.get(
                queryKeyword=queryKeyword)
        else:
            queryRelatedKeywords = RelatedKeywords.objects.create(
                queryKeyword=queryKeyword)
        for result in results:
            try:
                if(Link.objects.filter(link=result['url']).exists()):
                    link = Link.objects.get(link=result['url'])
                    link.domain = result['domain']
                    link.description = result['snippet']
                    link.title = result['title']
                    link.save()
                else:
                    link = Link.objects.create(link=result['url'], domain=result['domain'],
                                               description=result['snippet'], title=result['title'])
            except:
                responseText += "Link Creation of " + \
                    result['url']+" Got Error!\n"
            try:
                if(LinkPosition.objects.filter(queryKeyword=queryKeyword).filter(link=link).exists()):
                    linkPosition = LinkPosition.objects.get(
                        queryKeyword=queryKeyword, link=link)
                    linkPosition.position = int(result['position'])
                    linkPosition.save()
                else:
                    linkPosition = LinkPosition.objects.create(
                        queryKeyword=queryKeyword, link=link, position=int(result['position']))
            except:
                responseText += "Link Position Creation of " + \
                    result['url']+" Got Error!\n"
        for keyword in relatedKeywords:
            try:
                if(Keywords.objects.filter(text=keyword).exists()):
                    relatedKeyword = Keywords.objects.get(
                        text=keyword)
                else:
                    relatedKeyword = Keywords.objects.create(
                        text=keyword)
            except:
                responseText += "Keyword Creation of " + \
                    keyword+" Got Error!\n"
            try:
                queryRelatedKeywords.relatedKeywords.add(relatedKeyword)
            except:
                responseText += "Relate Keyword Addition of " + \
                    keyword+" to "+queryText+" Got Error!\n"
    else:
        return {
            'message': response.text,
            'statusCode': response.status_code
        }
    if(responseText == ""):
        return {
            'message': "Search with Mini Rapid Google Completed Successfuly",
            'statusCode': status.HTTP_200_OK
        }
    else:
        return {
            'message': responseText,
            'statusCode': status.HTTP_400_BAD_REQUEST
        }


def yandexSearch(yandexUsername, yandexKey, serachQuery):
    query = "&query="+serachQuery

    sortingByOptions = ["Relevance", "Time"]
    sortingByIds = ["rlv", "tm"]
    sortOption, index = pick(sortingByOptions, "Sort Result By:")
    position = sortingByOptions.index(sortOption)
    sortingById = sortingByIds[position]

    query += "&l10n=en&sortby="+sortingById

    if(sortOption == "Time"):
        sortingTimeByOptions = ["Ascending", "Descending"]
        sortingTimeByIds = ["ascending", "descending"]
        sortTimeOption, index = pick(sortingTimeByOptions, "Sort Result By:")
        position = sortingTimeByOptions.index(sortTimeOption)
        sortingTimeById = sortingTimeByIds[position]

        query += ".order%3D"+sortingTimeById

    filterOptions = ["None", "Moderate", "Strict"]
    filterIds = ["none", "moderate", "strict"]
    filterOption, index = pick(filterOptions, "Filter Options:")
    position = filterOptions.index(filterOption)
    filterId = filterIds[position]

    query += "&filter="+filterId

    # query += "&groupby=attr%3Dd.mode%3Ddeep.groups-on-page%3D100.docs-in-group%3D3"

    response = requests.get('https://yandex.com/search/xml?user=' +
                            str(yandexUsername)+'&key='+str(yandexKey)+str(query))

    if (response.status_code == 200):
        return {
            'statusCode': response.status_code,
            'Content': response.content
        }
    else:
        return {
            'statusCode': response.status_code,
            'Content': response.content
        }