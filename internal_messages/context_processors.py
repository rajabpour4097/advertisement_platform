from .models import Message

def unread_messages(request):
    if request.user.is_authenticated:
        latest_messages = Message.objects.filter(
            receiver=request.user,
            is_read=False
        ).select_related('sender').order_by('-created_at')[:3]
        
        unread_count = latest_messages.count()
        
        return {
            'unread_messages_count': unread_count,
            'latest_messages': latest_messages,
        }
    return {'unread_messages_count': 0, 'latest_messages': []} 