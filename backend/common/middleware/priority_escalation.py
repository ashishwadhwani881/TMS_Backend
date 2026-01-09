from apps.tasks.services.priority_escalation import escalate_priorities


class PriorityEscalationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        
        try:
            escalate_priorities()
        except Exception:
            
            pass

        return response
