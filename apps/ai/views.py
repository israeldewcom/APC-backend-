import openai
from django.conf import settings
from rest_framework import generics, permissions, status
from rest_framework.response import Response

openai.api_key = settings.OPENAI_API_KEY

class SmartReplyView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        message = request.data.get('message')
        if not message:
            return Response({'error': 'message required'}, status=400)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant generating short, natural replies for social media messages."},
                    {"role": "user", "content": f"Generate a short reply to: {message}"}
                ],
                max_tokens=50,
                temperature=0.7
            )
            reply = response.choices[0].message.content.strip()
        except Exception as e:
            reply = "Sorry, I couldn't generate a reply right now."

        return Response({'reply': reply})
