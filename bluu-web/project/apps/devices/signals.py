import django.dispatch

data_received = django.dispatch.Signal(providing_args=["instance", "ip_address"])
