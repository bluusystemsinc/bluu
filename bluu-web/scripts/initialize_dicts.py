from devices.models import DeviceType

def run():
    """
    Initializes dictionaries
    """
    # DeviceType
    DeviceType.objects.get_or_create(name='Bed', icon='resources/devices/icons/bed.png')
    DeviceType.objects.get_or_create(name='Blood pressure', icon='resources/devices/icons/blood-pressure.png')
    DeviceType.objects.get_or_create(name='Controller', icon='resources/devices/icons/controller.png')
    DeviceType.objects.get_or_create(name='Door', icon='resources/devices/icons/door.png')
    DeviceType.objects.get_or_create(name='Emergency', icon='resources/devices/icons/emergency.png')
    DeviceType.objects.get_or_create(name='Motion', icon='resources/devices/icons/motion.png')
    DeviceType.objects.get_or_create(name='Refrigerator', icon='resources/devices/icons/refrigerator.png')
    DeviceType.objects.get_or_create(name='Scale', icon='resources/devices/icons/scale.png')
    DeviceType.objects.get_or_create(name='Seat', icon='resources/devices/icons/seat.png')
    DeviceType.objects.get_or_create(name='Window', icon='resources/devices/icons/window.png')

