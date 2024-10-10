from django.db import models


class User(models.Model):  # chatbot_user
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)


class Message(models.Model):  # chatbot_message
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class Document(models.Model):  # chatbot_document
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Summary(models.Model):  # chatbot_summary
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    summary_text = models.TextField()
    key_terms = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Result(models.Model):  # chatbot_result
    summary = models.ForeignKey(Summary, on_delete=models.CASCADE)
    result_text = models.TextField()
    saved_to_file = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
