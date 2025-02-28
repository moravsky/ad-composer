from django.db import models

class CompanyInfo(models.Model):
    """Model for company information."""
    company_name = models.CharField(max_length=255, null=True)
    company_website = models.URLField(max_length=255, null=True)
    company_description = models.TextField(null=True)
    official_overview = models.TextField(null=True)
    product_overview = models.TextField(null=True)
    differentiators = models.TextField(null=True)
    ap_automation_url = models.URLField(max_length=255, null=True)
    
    class Meta:
        db_table = 'company_info'
        verbose_name_plural = 'Company Info'
    
    def __str__(self):
        return self.company_name or "Company Info"


class Persona(models.Model):
    """Model for personas."""
    name = models.CharField(max_length=255)
    description = models.TextField(null=True)
    url = models.URLField(max_length=255, null=True)
    
    class Meta:
        db_table = 'personas'
        verbose_name_plural = 'Personas'
    
    def __str__(self):
        return self.name


class Industry(models.Model):
    """Model for industries."""
    name = models.CharField(max_length=255)
    description = models.TextField(null=True)
    url = models.URLField(max_length=255, null=True)
    
    class Meta:
        db_table = 'industries'
        verbose_name_plural = 'Industries'
    
    def __str__(self):
        return self.name


class Account(models.Model):
    """Model for accounts."""
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=255, null=True)
    
    class Meta:
        db_table = 'accounts'
        verbose_name_plural = 'Accounts'
    
    def __str__(self):
        return self.name


class HealthcareSubvertical(models.Model):
    """Model for healthcare subverticals."""
    name = models.CharField(max_length=255)
    description = models.TextField(null=True)
    url = models.URLField(max_length=255, null=True)
    
    class Meta:
        db_table = 'healthcare_subverticals'
        verbose_name_plural = 'Healthcare Subverticals'
    
    def __str__(self):
        return self.name
