# # middleware.py
# # middleware.py
# from django.http import HttpResponseForbidden

# class SwaggerAuthMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         response = self.process_request(request)
#         if response:
#             return response
#         return self.get_response(request)

#     def process_request(self, request):
#         print(f"Request path: {request.path}")

#         if 'swagger' in request.path and not request.user.is_authenticated:
#             return HttpResponseForbidden('Not allowed. Authentication required.')
