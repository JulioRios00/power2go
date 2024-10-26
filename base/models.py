from django.db import models

class User(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Contract(models.Model):
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contracts")
    fidelity = models.IntegerField()
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Contract {self.id} - {self.user.name}"