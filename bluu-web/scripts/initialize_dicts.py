from devices.models import DeviceType
from alerts.models import Alert

def run():
    """
    Initializes dictionaries
    """
    # DeviceType
    bed, created = DeviceType.objects.get_or_create(name=DeviceType.BED, icon='resources/devices/icons/bed.png')
    blood_pressure, created = DeviceType.objects.get_or_create(name=DeviceType.BLOOD_PRESSURE, icon='resources/devices/icons/blood-pressure.png')
    #DeviceType.objects.get_or_create(name=DeviceType.CONTROLLER, icon='resources/devices/icons/controller.png')
    door, created = DeviceType.objects.get_or_create(name=DeviceType.DOOR, icon='resources/devices/icons/door.png')
    emergency, created = DeviceType.objects.get_or_create(name=DeviceType.EMERGENCY, icon='resources/devices/icons/emergency.png')
    motion, created = DeviceType.objects.get_or_create(name=DeviceType.MOTION, icon='resources/devices/icons/motion.png')
    refrigerator, created = DeviceType.objects.get_or_create(name=DeviceType.REFRIGERATOR, icon='resources/devices/icons/refrigerator.png')
    scale, created = DeviceType.objects.get_or_create(name=DeviceType.SCALE, icon='resources/devices/icons/scale.png')
    seat, created = DeviceType.objects.get_or_create(name=DeviceType.SEAT, icon='resources/devices/icons/seat.png')
    window, created = DeviceType.objects.get_or_create(name=DeviceType.WINDOW, icon='resources/devices/icons/window.png')

    # Register alerts for device types
    o, created = Alert.objects.get_or_create(alert_type=Alert.OPEN)
    o.device_types.add(door, window, refrigerator, emergency)
    ogt, created = Alert.objects.get_or_create(alert_type=Alert.OPEN_GREATER_THAN)
    ogt.device_types.add(door, window, refrigerator, bed, seat)
    ogtnm, created = Alert.objects.get_or_create(alert_type=Alert.OPEN_GREATER_THAN_NO_MOTION)
    ogtnm.device_types.add(door)
    cgt, created = Alert.objects.get_or_create(alert_type=Alert.CLOSED_GREATER_THAN)
    cgt.device_types.add(bed, refrigerator)
    aipgt, created = Alert.objects.get_or_create(alert_type=Alert.ACTIVE_IN_PERIOD_GREATER_THAN)
    aipgt.device_types.add(seat)
    iipgt, created = Alert.objects.get_or_create(alert_type=Alert.INACTIVE_IN_PERIOD_GREATER_THAN)
    iipgt.device_types.add(bed)
    mir, created = Alert.objects.get_or_create(alert_type=Alert.MOTION_IN_ROOM)
    mir.device_types.add(motion)
    mirgt, created = Alert.objects.get_or_create(alert_type=Alert.MOTION_IN_ROOM_GREATER_THAN)
    mirgt.device_types.add(motion)
    mirlt, created = Alert.objects.get_or_create(alert_type=Alert.MOTION_IN_ROOM_LESS_THAN)
    mirlt.device_types.add(motion)
    nmirgt, created = Alert.objects.get_or_create(alert_type=Alert.NOMOTION_IN_ROOM_GREATER_THAN)
    nmirgt.device_types.add(motion)
    #scale
    wgt, created = Alert.objects.get_or_create(alert_type=Alert.WEIGHT_GREATER_THAN)
    wgt.device_types.add(scale)
    wlt, created = Alert.objects.get_or_create(alert_type=Alert.WEIGHT_LESS_THAN)
    wlt.device_types.add(scale)
    su, created = Alert.objects.get_or_create(alert_type=Alert.SCALE_USED)
    su.device_types.add(scale)

