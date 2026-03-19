from django.conf import settings
from django.core.cache import cache
from apps.multi_tenant.models import Organization

class MultiTenantMiddleware:
    """
    Middleware to set the current organization based on the request's domain/subdomain.
    Stores the organization in request.org and also in thread-local for use in models.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0]  # remove port
        org = None
        try:
            cache_key = f"org_domain_{host}"
            org_id = cache.get(cache_key)
            if org_id:
                org = Organization.objects.get(id=org_id)
            else:
                org = Organization.objects.get(domain=host)
                cache.set(cache_key, org.id, 300)
        except Organization.DoesNotExist:
            default_domain = settings.MULTI_TENANT_DOMAIN_PATTERN
            if host.endswith('.' + default_domain):
                subdomain = host.replace('.' + default_domain, '')
                try:
                    org = Organization.objects.get(subdomain=subdomain)
                    cache.set(cache_key, org.id, 300)
                except Organization.DoesNotExist:
                    pass

        request.organization = org
        from threading import local
        _thread_locals = local()
        _thread_locals.organization = org

        response = self.get_response(request)
        return response
