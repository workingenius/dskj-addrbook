from django.http.response import HttpResponse

def check_HTTP_USER_AGENT(request):
    return HttpResponse(request.user_agent.browser.family)
    
