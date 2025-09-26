package solid.service.senders;

import solid.service.NotificationType;
import solid.user.User;

// abstraction to represent a notification sender.

public interface NotificationSender {
    
    /**
     * Send a notification to a user
     * @param user: The user to send the notification to
     * @param message: The message to send
     * @return: true if the notification was sent successfully
     */
    boolean send(User user, String message);
    
    /**
     * Get the notification type this sender handles
     * @return: The notification type
     */
    NotificationType getNotificationType();
}
