
import time
from plyer import notification


class NotificationManager:
    def __init__(self, cooldown=300):
        self.cooldown = cooldown
        self.last_notifications = {}

    def send_notification(self, title, message):
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="System Monitoring",
                timeout=10
            )
            print(f"Desktop notification sent: {title}")

        except Exception as error:
            print(f"Notification error: {error}")

    def check_threshold(self, resource, value, threshold):
        current_time = time.time()

        if value >= threshold:
            last_sent = self.last_notifications.get(resource, 0)

            if current_time - last_sent >= self.cooldown:
                self.send_notification(
                    title=f"High {resource} Usage Detected",
                    message=(
                        f"{resource} usage is currently "
                        f"{value:.1f}%, exceeding the "
                        f"{threshold}% threshold."
                    )
                )

                self.last_notifications[resource] = current_time


if __name__ == "__main__":
    notification_manager = NotificationManager()

    notification_manager.send_notification(
        title="System Monitoring",
        message="Desktop notifications are working!"
    )
