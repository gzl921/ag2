package solid.service.senders;

import solid.service.NotificationType;
import solid.user.User;

// SMS notification sender implementation
public class SmsSender implements NotificationSender {
    
    @Override
    public boolean send(User user, String message) {
        System.out.println("Sending SMS to " + user.getUsername() + " -> " + message);
        return true;
    }
    
    @Override
    public NotificationType getNotificationType() {
        return NotificationType.SMS;
    }
}
