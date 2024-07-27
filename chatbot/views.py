from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Conversation, Message
from .serializers import ConversationSerializer
import anthropic
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ChatView(APIView):
    def post(self, request):
        try:
            conversation_id = request.data.get('conversation_id')
            user_message = request.data.get('message')

            if conversation_id:
                conversation = Conversation.objects.get(id=conversation_id)
            else:
                conversation = Conversation.objects.create()

            Message.objects.create(conversation=conversation, content=user_message, role='user')

            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

            # Prepare messages in the correct format
            db_messages = conversation.messages.order_by('created_at')
            api_messages = []
            for msg in db_messages:
                if not api_messages or api_messages[-1]['role'] != msg.role:
                    api_messages.append({"role": msg.role, "content": msg.content})
                else:
                    api_messages[-1]['content'] += f"\n\n{msg.content}"

            logger.info(f"Prepared messages for API: {api_messages}")

            response = client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=500,
                temperature=0,
                messages=api_messages
            )

            Message.objects.create(conversation=conversation, content=response.content, role='assistant')

            serializer = ConversationSerializer(conversation)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in ChatView: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=500)