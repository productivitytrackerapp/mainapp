import ctypes
import ctypes.util

cg = ctypes.CDLL(ctypes.util.find_library("CoreGraphics"))

cg.CGEventSourceSecondsSinceLastEventType.argtypes = [
    ctypes.c_int32,   # CGEventSourceStateID
    ctypes.c_uint32,  # CGEventType
]
cg.CGEventSourceSecondsSinceLastEventType.restype = ctypes.c_double

# Values from CoreGraphics headers
kCGEventSourceStateCombinedSessionState = 0
kCGAnyInputEventType = 0xFFFFFFFF


def find_idle_state() -> float:
    return cg.CGEventSourceSecondsSinceLastEventType(
        kCGEventSourceStateCombinedSessionState,
        kCGAnyInputEventType,
    )