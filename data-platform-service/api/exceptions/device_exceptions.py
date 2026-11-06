class DeviceError(Exception):
    pass

class GetDeviceError(DeviceError):
    pass

class GetDevicesError(DeviceError):
    pass

class CreateDeviceError(DeviceError):
    pass

class UpdateDeviceError(DeviceError):
    pass

class DeleteDeviceError(DeviceError):
    pass