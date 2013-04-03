from devices.models import DeviceType
from alerts.models import Alert

def run():
    """
    Initializes dictionaries
    """
    # DeviceType
    bed = DeviceType.objects.get_or_create(name=DeviceType.BED, icon='resources/devices/icons/bed.png')
    blood_pressure = DeviceType.objects.get_or_create(name=DeviceType.BLOOD_PRESSURE, icon='resources/devices/icons/blood-pressure.png')
    #DeviceType.objects.get_or_create(name=DeviceType.CONTROLLER, icon='resources/devices/icons/controller.png')
    door = DeviceType.objects.get_or_create(name=DeviceType.DOOR, icon='resources/devices/icons/door.png')
    emergency = DeviceType.objects.get_or_create(name=DeviceType.EMERGENCY, icon='resources/devices/icons/emergency.png')
    motion = DeviceType.objects.get_or_create(name=DeviceType.MOTION, icon='resources/devices/icons/motion.png')
    refrigerator = DeviceType.objects.get_or_create(name=DeviceType.REFRIGERATOR, icon='resources/devices/icons/refrigerator.png')
    scale = DeviceType.objects.get_or_create(name=DeviceType.SCALE, icon='resources/devices/icons/scale.png')
    seat = DeviceType.objects.get_or_create(name=DeviceType.SEAT, icon='resources/devices/icons/seat.png')
    window = DeviceType.objects.get_or_create(name=DeviceType.WINDOW, icon='resources/devices/icons/window.png')

    # Register alerts for device types
    o = Alert.objects.get_or_create(name=Alert.OPEN)
    o.add(door, window, refrigerator, seat, bed, emergency)
    ogt = Alert.objects.get_or_create(name=Alert.OPEN_GREATER_THAN)
    ogt.add(door, window, refrigerator, bed, seat)
    ogtnm = Alert.objects.get_or_create(name=Alert.OPEN_GREATER_THAN_NO_MOTION)
    ogtnm.add(door)
    cgt = Alert.objects.get_or_create(name=Alert.CLOSED_GREATER_THAN)
    cgt.add(bed, refrigerator)
    aipgt = Alert.objects.get_or_create(name=Alert.ACTIVE_IN_PERIOD_GREATER_THAN)
    aipgt.add(seat)
    iipgt = Alert.objects.get_or_create(name=Alert.ACTIVE_IN_PERIOD_GREATER_THAN)
    iipgt.add(bed)
    mir = Alert.objects.get_or_create(name=Alert.MOTION_IN_ROOM)
    mir.add(motion)
    mirgt = Alert.objects.get_or_create(name=Alert.MOTION_IN_ROOM_GREATER_THAN)
    mirgt.add(motion)
    mirlt = Alert.objects.get_or_create(name=Alert.MOTION_IN_ROOM_LESS_THAN)
    mirlt.add(motion)
    nmirgt = Alert.objects.get_or_create(name=Alert.NOMOTION_IN_ROOM_GREATER_THAN)
    nmirgt.add(motion)

