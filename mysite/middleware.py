from django.shortcuts import redirect

class MentorRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        mentor_usernames = [
            "GroupAMentor", "GroupBMentor", "GroupCMentor", "GroupDMentor",
            "GroupEMentor", "GroupFMentor", "GroupGMentor", "GroupHMentor",
            "GroupIMentor", "GroupJMentor", "GroupKMentor", "GroupLMentor", 
            "GroupMMentor", "GroupNMentor", "GroupOMentor", "GroupPMentor", 
            "GroupQMentor", "GroupRMentor", "GroupSMentor", "GroupTMentor",
            "GroupUMentor","GroupVMentor","GroupWMentor","GroupXMentor"
            
        ]

        if hasattr(request, 'user') and request.user.is_authenticated:
            if request.user.username in mentor_usernames and request.path not in ['/mentor/', '/accounts/logout/']:
                return redirect('mentor_page')
            elif request.user.username in mentor_usernames and request.path == '/mentor/':
                return self.get_response(request)

        response = self.get_response(request)
        return response
