package solid.service;

import solid.user.User;
import solid.service.senders.EmailSender;
import solid.service.senders.SmsSender;
import solid.service.senders.PushSender;
import solid.service.senders.NotificationSender;

import java.util.HashMap;
import java.util.Map;

// Service responsible for sending notifications through different channels
public class NotificationService {
    private Map<NotificationType, NotificationSender> senders;
    
    public NotificationService() {
        this.senders = new HashMap<>();
        // Register default senders
        this.senders.put(NotificationType.EMAIL, new EmailSender());
        this.senders.put(NotificationType.SMS, new SmsSender());
        this.senders.put(NotificationType.PUSH, new PushSender());
    }
    
    // Send a notification to a user using the specified notification type
     
    public boolean sendNotification(User user, String message, NotificationType notificationType) {
        NotificationSender sender = senders.get(notificationType);
        if (sender == null) {
            System.out.println("User " + user.getUsername() + " does not support receive " + 
                             notificationType.name().toLowerCase() + " notifications.");
            return false;
        }
        
        return sender.send(user, message);
    }
    
    // Register a custom notification sender
     
    public void registerSender(NotificationType notificationType, NotificationSender sender) {
        this.senders.put(notificationType, sender);
    }
}
