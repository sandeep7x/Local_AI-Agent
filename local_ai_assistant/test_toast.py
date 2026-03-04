import platform
import os
import time

print("Platform:", platform.system())
print("ENABLE_TOASTS:", os.getenv("ENABLE_TOASTS"))

try:
    from win10toast import ToastNotifier
    toaster = ToastNotifier()
    print("Calling show_toast...")
    # Use non-threaded to wait until toast call returns
    res = toaster.show_toast("Test", "Hello from win10toast", duration=5, threaded=False)
    print("show_toast returned:", res)
except Exception as e:
    print("Exception while showing toast:", repr(e))

time.sleep(1)
