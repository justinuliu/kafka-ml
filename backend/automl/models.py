from django.db import models
from django.utils.timezone import now
from django.conf import settings
from model_utils import Choices
from model_utils.fields import StatusField, MonitorField

class MLModel(models.Model):
    """Machine learning model to be trained in the system"""

    name = models.CharField(unique=True, max_length=30)
    description = models.CharField(max_length=100, blank=True)
    imports = models.TextField(blank=True)
    code = models.TextField()
    distributed = models.BooleanField(default=False)
    father = models.OneToOneField('self', null=True, blank=True, default=None, related_name='child', on_delete=models.SET_NULL)
    framework = models.TextField()


class Configuration(models.Model):
    """Set of ML models to be used for training"""

    name = models.CharField(unique=True, max_length=30)
    description = models.CharField(max_length=100, blank=True)
    ml_models = models.ManyToManyField(MLModel)
    time = models.DateTimeField(default=now, editable=False)

    class Meta(object):
        ordering = ('-time', )
    

class Deployment(models.Model):
    """Deployment of a configuration of models for training"""

    batch = models.IntegerField(default=1)
    tf_kwargs_fit = models.CharField(max_length=100, blank=True)
    tf_kwargs_val = models.CharField(max_length=100, blank=True)
    pth_kwargs_fit = models.CharField(max_length=100, blank=True)
    pth_kwargs_val = models.CharField(max_length=100, blank=True)
    conf_mat_settings = models.BooleanField()
    configuration = models.ForeignKey(Configuration, related_name='deployments', on_delete=models.CASCADE)
    time = models.DateTimeField(default=now, editable=False)

    class Meta(object):
        ordering = ('-time', )
    
class TrainingResult(models.Model):
    """Training result information obtained once deployed a model"""
    
    STATUS = Choices('created', 'deployed', 'stopped', 'finished')
    """Sets its default value to the first item in the STATUS choices:"""
    status = StatusField()
    status_changed = MonitorField(monitor='status')
    deployment = models.ForeignKey(Deployment, default=None, related_name='results', on_delete=models.CASCADE)
    model = models.ForeignKey(MLModel, related_name='trained', on_delete=models.CASCADE)
    train_metrics =  models.JSONField(blank=True, null=True)
    val_metrics   =  models.JSONField(blank=True, null=True)
    test_metrics  =  models.JSONField(blank=True, null=True)
    confusion_matrix =  models.JSONField(blank=True, null=True)
    training_time =  models.DecimalField(max_digits=14, decimal_places=4, blank=True, null=True)
    trained_model =  models.FileField(upload_to=settings.TRAINED_MODELS_DIR, blank=True)
    confusion_mat_img =  models.FileField(upload_to=settings.TRAINED_MODELS_DIR, blank=True, null=True)

    class Meta(object):
        ordering = ('-status_changed', )


class Datasource(models.Model):
    """Datasource used for training a deployed model"""

    INPUT_FORMAT = Choices('RAW', 'AVRO')
    """Sets its default value to the first item in the STATUS choices:"""
    input_format = StatusField(choices_name='INPUT_FORMAT')
    deployment = models.TextField() 
    input_config = models.TextField(blank=True) 
    description = models.TextField(blank=True)
    topic = models.TextField()
    total_msg= models.IntegerField()
    validation_rate = models.DecimalField(max_digits=7, decimal_places=6)
    test_rate = models.DecimalField(max_digits=7, decimal_places=6)
    time = models.DateTimeField()

    class Meta(object):
        ordering = ('-time', )

class Inference(models.Model):
    """Training result information obtained once deployed a model"""
    INPUT_FORMAT = Choices('RAW', 'AVRO')
    STATUS = Choices('deployed', 'stopped')
    """Sets its default value to the first item in the STATUS choices:"""
    
    status = StatusField()
    status_changed = MonitorField(monitor='status')
    model_result = models.ForeignKey(TrainingResult, null=True, related_name='inferences', on_delete=models.SET_NULL)
    replicas = models.IntegerField(default=1)
    input_format = StatusField(choices_name='INPUT_FORMAT')
    input_config = models.TextField(blank=True)
    input_topic =  models.TextField(blank=True)
    output_topic =  models.TextField(blank=True)
    time = models.DateTimeField(default=now, editable=False)
    limit = models.DecimalField(max_digits=15, decimal_places=10, blank=True,  null=True)
    output_upper = models.TextField(blank=True)
    token = models.TextField(blank=True, default=None, null=True)
    external_host = models.TextField(blank=True, default=None, null=True)
    input_kafka_broker = models.TextField(blank=True, default=None, null=True)
    output_kafka_broker = models.TextField(blank=True, default=None, null=True)
    upper_kafka_broker = models.TextField(blank=True, default=None, null=True)

    class Meta(object):
        ordering = ('-time', )
