package solid.service.senders;

import solid.service.NotificationType;
import solid.user.User;

// Push notification sender implementation
 
public class PushSender implements NotificationSender {
    
    @Override
    public boolean send(User user, String message) {
        System.out.println("Sending PUSH to " + user.getUsername() + " -> " + message);
        return true;
    }
    
    @Override
    public NotificationType getNotificationType() {
        return NotificationType.PUSH;
    }
}
