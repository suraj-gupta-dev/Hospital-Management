from django.db import transaction
from auditlogs.services import AuditLogsServices



class AuditLogMixin:

    @transaction.atomic
    def perform_create(self, serializer):
        instance = self.get_object()

        AuditLogsServices.log_model_create(
            request=self.request,
            instance=instance
        )
        return instance

    @transaction.atomic
    def perform_update(self, serializer):
        instance = serializer.instance

        #capture data before updating
        old_data = AuditLogsServices.get_model_snapshot(instance)

        # save updated data
        updated_instance = serializer.save()

        # Record the differences
        AuditLogsServices.log_model_update(
            request=self.request,
            instance=updated_instance,
            old_data=old_data
        )

        return updated_instance

    @transaction.atomic
    def perform_destroy(self, instance):
        
        # Record deletion before deleting the object
        AuditLogsServices.log_model_delete(
            request=self.request,
            instance=instance
        )

        instance.delete()

