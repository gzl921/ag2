package solid.service;

import solid.persistence.Database;
import solid.user.AdminUser;
import solid.user.User;

// Service for handling regular user operations
 
public class RegularUserService extends UserService {
    
    public RegularUserService(Database<User> database, NotificationService notificationService) {
        super(database, notificationService);
    }
    
    @Override
    public void removeUser(User user) {
        if (user instanceof AdminUser admin && admin.hasSuperAdminRights()) {
            System.out.println("Cannot delete admin user with super admin rights.");
            return; // do NOT call DB delete 
        }
        super.removeUser(user);
    }
    
    // Send a tax notification to a regular user
     // Override to prevent push notifications for regular users
     
    @Override
    public void sendTaxNotification(User user, String message, NotificationType notificationType) {
        if (notificationType == NotificationType.PUSH) {
            System.out.println("User " + user.getUsername() + " does not support receive push notifications.");
            return;
        }
        super.sendTaxNotification(user, message, notificationType);
    }
}