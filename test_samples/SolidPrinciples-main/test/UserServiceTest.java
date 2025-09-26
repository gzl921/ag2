import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import static org.junit.jupiter.api.Assertions.*;

import solid.persistence.Database;
import solid.service.AdminUserService;
import solid.service.NotificationService;
import solid.service.NotificationType;
import solid.service.RegularUserService;
import solid.user.AdminUser;
import solid.user.User;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

// Test suite for UserService functionality
 
public class UserServiceTest {
    
    private Database<User> mockDatabase;
    private NotificationService notificationService;
    private RegularUserService regularUserService;
    private AdminUserService adminUserService;
    private ByteArrayOutputStream outputStream;
    
    @BeforeEach
    void setUp() {
        // Create mock database
        mockDatabase = new MockDatabase();
        notificationService = new NotificationService();
        regularUserService = new RegularUserService(mockDatabase, notificationService);
        adminUserService = new AdminUserService(mockDatabase, notificationService);
        outputStream = new ByteArrayOutputStream();
        System.setOut(new PrintStream(outputStream));
    }
    
    @Test
    @DisplayName("Should add user successfully")
    void testAddUser() {
        User user = new User(1, "test_user", 25, 50000);
        
        regularUserService.addUser(user);
        
        String output = outputStream.toString();
        assertTrue(output.contains("Executing Save SQL"));
        assertTrue(output.contains("test_user"));
    }
    
    @Test
    @DisplayName("Should fetch existing user by ID")
    void testGetUserById_ExistingUser() {
        User user = new User(1, "test_user", 25, 50000);
        regularUserService.addUser(user);
        
        User fetchedUser = regularUserService.getUserById(1);
        
        assertNotNull(fetchedUser);
        assertEquals("test_user", fetchedUser.getUsername());
        assertTrue(outputStream.toString().contains("Fetched User: test_user, 25"));
    }
    
    @Test
    @DisplayName("Should handle non-existent user gracefully")
    void testGetUserById_NonExistentUser() {
        User fetchedUser = regularUserService.getUserById(999);
        
        assertNull(fetchedUser);
        assertTrue(outputStream.toString().contains("User with ID 999 not found"));
    }
    
    @Test
    @DisplayName("Should delete existing user successfully")
    void testRemoveUser_ExistingUser() {
        User user = new User(1, "test_user", 25, 50000);
        regularUserService.addUser(user);
        
        regularUserService.removeUser(user);
        
        String output = outputStream.toString();
        assertTrue(output.contains("User account deleted: test_user"));
        assertTrue(output.contains("Account deleted successfully"));
    }
    
    @Test
    @DisplayName("Should handle deletion of non-existent user")
    void testRemoveUser_NonExistentUser() {
        User user = new User(999, "non_existent", 25, 50000);
        
        regularUserService.removeUser(user);
        
        String output = outputStream.toString();
        assertTrue(output.contains("User with id 999 not found"));
    }
    
    @Test
    @DisplayName("Should send email notification to regular user")
    void testSendTaxNotification_Email() {
        User user = new User(1, "test_user", 25, 50000);
        regularUserService.addUser(user);
        
        regularUserService.sendTaxNotification(user, "Test message", NotificationType.EMAIL);
        
        String output = outputStream.toString();
        assertTrue(output.contains("Sending EMAIL to test_user"));
        assertTrue(output.contains("Test message Value: 5000.0")); // 10% age < 30
    }
    
    @Test
    @DisplayName("Should send SMS notification to regular user")
    void testSendTaxNotification_SMS() {
        User user = new User(1, "test_user", 35, 50000);
        regularUserService.addUser(user);
        
        regularUserService.sendTaxNotification(user, "Test message", NotificationType.SMS);
        
        String output = outputStream.toString();
        assertTrue(output.contains("Sending SMS to test_user"));
        assertTrue(output.contains("Test message Value: 10000.0")); // 20% for 30-60
    }
    
    @Test
    @DisplayName("Should prevent push notifications for regular users")
    void testSendTaxNotification_Push_RegularUser() {
        User user = new User(1, "test_user", 25, 50000);
        regularUserService.addUser(user);
        
        regularUserService.sendTaxNotification(user, "Test message", NotificationType.PUSH);
        
        String output = outputStream.toString();
        assertTrue(output.contains("User test_user does not support receive push notifications"));
    }
    
    @Test
    @DisplayName("Should allow push notifications for admin users")
    void testSendTaxNotification_Push_AdminUser() {
        User adminUser = new AdminUser(1, "admin_user", 65, 50000, true);
        adminUserService.addUser(adminUser);
        
        adminUserService.sendTaxNotification(adminUser, "Test message", NotificationType.PUSH);
        
        String output = outputStream.toString();
        assertTrue(output.contains("Sending PUSH to admin_user"));
        assertTrue(output.contains("Test message Value: 7500.0")); // 15% for afe > 60
    }
    
    @Test
    @DisplayName("Should prevent deletion of admin user with super admin rights")
    void testRemoveUser_AdminWithSuperRights() {
        User adminUser = new AdminUser(1, "super_admin", 30, 50000, true);
        adminUserService.addUser(adminUser);
        
        adminUserService.removeUser(adminUser);
        
        String output = outputStream.toString();
        assertTrue(output.contains("Cannot delete admin user with super admin rights"));
        assertFalse(output.contains("Account deleted successfully"));
        
        // Try to delete again 
        //  Should get same message, user still exists
        outputStream.reset();
        adminUserService.removeUser(adminUser);
        String output2 = outputStream.toString();
        assertTrue(output2.contains("Cannot delete admin user with super admin rights"));
    }
    
    @Test
    @DisplayName("Should allow deletion of admin user without super admin rights")
    void testRemoveUser_AdminWithoutSuperRights() {
        User adminUser = new AdminUser(1, "regular_admin", 30, 50000, false);
        adminUserService.addUser(adminUser);
        
        adminUserService.removeUser(adminUser);
        
        String output = outputStream.toString();
        assertTrue(output.contains("User account deleted: regular_admin"));
        assertTrue(output.contains("Account deleted successfully"));
    }
    
    @Test
    @DisplayName("Should handle repeated deletion attempts gracefully")
    void testRemoveUser_RepeatedDeletion() {
        User user = new User(1, "test_user", 25, 50000);
        regularUserService.addUser(user);
        
        // First deletion should succeed
        regularUserService.removeUser(user);
        String firstOutput = outputStream.toString();
        assertTrue(firstOutput.contains("Account deleted successfully"));
        
        // Second deletion should fail
        regularUserService.removeUser(user);
        String secondOutput = outputStream.toString();
        assertTrue(secondOutput.contains("User with id 1 not found"));
    }
    
    // Mock database implementation for testing
     
    private static class MockDatabase implements Database<User> {
        private Map<Integer, User> users = new HashMap<>();
        
        @Override
        public boolean save(User user) {
            System.out.println("Executing Save SQL: " + user);
            users.put(user.getId(), user);
            return true;
        }
        
        @Override
        public User query(int id) {
            System.out.println("Executing SQL query");
            return users.get(id);
        }
        
        @Override
        public Optional<User> delete(int id) {
            System.out.println("Executing SQL delete");
            User user = users.remove(id);
            return Optional.ofNullable(user);
        }
    }
}
