"""Helper wrapper for winrt-based notifications.

This module provides a simple `show_toast` function that constructs a
ToastGeneric notification using the Windows Runtime APIs via `winrt`.
"""
from winrt.windows.ui.notifications import ToastNotificationManager, ToastNotification
from winrt.windows.data.xml.dom import XmlDocument


def show_toast(title: str, message: str):
    template = f"""<toast>
  <visual>
    <binding template='ToastGeneric'>
      <text>{title}</text>
      <text>{message}</text>
    </binding>
  </visual>
</toast>"""
    doc = XmlDocument()
    doc.load_xml(template)
    toast = ToastNotification(doc)
    notifier = ToastNotificationManager.create_toast_notifier()
    notifier.show(toast)
