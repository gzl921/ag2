package solid.service;

import solid.persistence.Database;
import solid.user.AdminUser;
import solid.user.User;

import java.util.Optional;

//Service for handling admin user operations
public class AdminUserService extends UserService {
    
    public AdminUserService(Database<User> database, NotificationService notificationService) {
        super(database, notificationService);
    }
    
    @Override
    public void removeUser(User user) {
        if (user instanceof AdminUser admin && admin.hasSuperAdminRights()) {
            System.out.println("Cannot delete admin user with super admin rights.");
            return; // do NOT call DB delete or print success
        }
        // For non-super-admin users, handle deletion manually to avoid double messages
        Optional<User> deletedUser = database.delete(user.getId());
        
        if (deletedUser.isPresent()) {
            user.deleteAccount();
            System.out.println("Account deleted successfully.");
        } else {
            System.out.println("User with id " + user.getId() + " not found!");
        }
    }
    
    // Send a push notification to an admin user
     
    public void sendPushNotification(User user, String message) {
        sendTaxNotification(user, message, NotificationType.PUSH);
    }
}