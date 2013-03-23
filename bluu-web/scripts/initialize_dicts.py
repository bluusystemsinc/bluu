from devices.models import DeviceType

def run():
    """
    Initializes dictionaries
    """
    # DeviceType
    DeviceType.objects.get_or_create(name=DeviceType.BED, icon='resources/devices/icons/bed.png')
    DeviceType.objects.get_or_create(name=DeviceType.BLOOD_PRESSURE, icon='resources/devices/icons/blood-pressure.png')
    #DeviceType.objects.get_or_create(name=DeviceType.CONTROLLER, icon='resources/devices/icons/controller.png')
    DeviceType.objects.get_or_create(name=DeviceType.DOOR, icon='resources/devices/icons/door.png')
    DeviceType.objects.get_or_create(name=DeviceType.EMERGENCY, icon='resources/devices/icons/emergency.png')
    DeviceType.objects.get_or_create(name=DeviceType.MOTION, icon='resources/devices/icons/motion.png')
    DeviceType.objects.get_or_create(name=DeviceType.REFRIGERATOR, icon='resources/devices/icons/refrigerator.png')
    DeviceType.objects.get_or_create(name=DeviceType.SCALE, icon='resources/devices/icons/scale.png')
    DeviceType.objects.get_or_create(name=DeviceType.SEAT, icon='resources/devices/icons/seat.png')
    DeviceType.objects.get_or_create(name=DeviceType.WINDOW, icon='resources/devices/icons/window.png')

