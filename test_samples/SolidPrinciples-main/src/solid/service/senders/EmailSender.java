package solid.service.senders;

import solid.service.NotificationType;
import solid.user.User;

// Email notification sender implementation
 
public class EmailSender implements NotificationSender {
    
    @Override
    public boolean send(User user, String message) {
        System.out.println("Sending EMAIL to " + user.getUsername() + " -> " + message);
        return true;
    }
    
    @Override
    public NotificationType getNotificationType() {
        return NotificationType.EMAIL;
    }
}
