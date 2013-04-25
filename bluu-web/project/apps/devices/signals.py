import django.dispatch

data_received = django.dispatch.Signal(providing_args=["device", "data",
                                                       "timestamp",
                                                       "ip_address"])
