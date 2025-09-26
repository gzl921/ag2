package solid.service;

import solid.persistence.Database;
import solid.user.User;

import java.util.Optional;

// Service responsible for user operations using dependency injection
 
public class UserService {
    protected final Database<User> database;
    protected final NotificationService notificationService;
    
    public UserService(Database<User> database, NotificationService notificationService) {
        this.database = database;
        this.notificationService = notificationService;
    }
    
    /**
     * Add a user to the system
     * @param user The user to add
     */
    public void addUser(User user) {
        database.save(user);
    }
    
    /**
     * Get a user by ID
     * @param id The ID of the user to fetch
     * @return The user if found, null otherwise
     */
    public User getUserById(int id) {
        User fetchedUser = database.query(id);
        
        if (fetchedUser == null) {
            System.out.println("User with ID " + id + " not found.");
            return null;
        }
        System.out.println("Fetched User: " + fetchedUser.getUsername() + ", " + fetchedUser.getAge() + "\n");
        return fetchedUser;
    }
    
    /**
     * Remove a user from the system
     * @param user The user to remove
     */
    public void removeUser(User user) {
        Optional<User> deletedUser = database.delete(user.getId());
        
        if (deletedUser.isPresent()) {
            user.deleteAccount();
            System.out.println("Account deleted successfully.");
        } else {
            System.out.println("User with id " + user.getId() + " not found!");
        }
    }
    
    /**
     * Send a tax notification to a user
     * @param user The user to send the notification to
     * @param message The base message
     * @param notificationType The type of notification to send
     */
    public void sendTaxNotification(User user, String message, NotificationType notificationType) {
        String taxMessage = message + " Value: " + user.calculateTax();
        notificationService.sendNotification(user, taxMessage, notificationType);
    }
}
