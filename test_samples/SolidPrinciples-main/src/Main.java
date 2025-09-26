import solid.persistence.Database;
import solid.persistence.drivers.PostgresDriver;
import solid.service.AdminUserService;
import solid.service.NotificationService;
import solid.service.NotificationType;
import solid.service.RegularUserService;
import solid.user.AdminUser;
import solid.user.User;

public class Main {
    public static void main(String[] args) {
        System.out.println("------------------Adding users-------------------------");
        
        // Create database and notification service instances
        Database<User> database = new PostgresDriver();
        NotificationService notificationService = new NotificationService();
        
        // Create User instances
        User user0 = new AdminUser(0, "bob_jones", 65, 100000, true);
        User user1 = new User(1, "john_doe", 25, 100000);
        User user2 = new User(2, "alice_smith", 35, 100000);

        // Create services with dependency injection
        RegularUserService regularUserService = new RegularUserService(database, notificationService);
        AdminUserService adminUserService = new AdminUserService(database, notificationService);

        // Save users 1 and 2 using RegularUserService
        regularUserService.addUser(user1);
        regularUserService.addUser(user2);
        adminUserService.addUser(user0);

        System.out.println("\n------------------Sending notifications-------------------------");

        // Send notifications using different services
        regularUserService.sendTaxNotification(user1, "Pay your taxes!", NotificationType.EMAIL);
        regularUserService.sendTaxNotification(user2, "Pay your taxes!", NotificationType.SMS);

        //This line should NOT break the system after refactoring the code
        regularUserService.sendTaxNotification(user2, "Pay your taxes!", NotificationType.PUSH);

        adminUserService.sendTaxNotification(user0, "Pay your taxes!", NotificationType.PUSH);

        System.out.println("\n------------------Fetching users-------------------------");

        // Fetch and display user by ID
        regularUserService.getUserById(1);
        adminUserService.getUserById(0);

        System.out.println("\n------------------Deleting users-------------------------");
        // Delete accounts
        regularUserService.removeUser(user1);
        regularUserService.removeUser(user2);
        adminUserService.removeUser(user2);
        regularUserService.removeUser(user0);

        adminUserService.removeUser(user0);

    }
}