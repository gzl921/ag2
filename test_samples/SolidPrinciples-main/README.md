# SOLID Principles Refactoring Assignment

The SOLID principles are a set of five design principles in object-oriented programming that help create more understandable, flexible, and maintainable software. They were introduced by Robert C. Martin ("Uncle Bob") to guide developers in building systems that are easy to scale and refactor.

Single Responsibility Principle (SRP):
A class should have only one reason to change, meaning it should have only one job or responsibility.

Open-Closed Principle (OCP):
Software entities (classes, modules, functions, etc.) should be open for extension but closed for modification. You should be able to add new functionality without changing existing code.

Liskov Substitution Principle (LSP):
Objects of a superclass should be replaceable with objects of its subclasses without affecting the correctness of the program. In other words, subclasses should behave in a way that does not break the expectations set by their parent class.

Interface Segregation Principle (ISP):
Clients should not be forced to depend on interfaces they do not use. It's better to have many small, specific interfaces than one large, general-purpose interface.

Dependency Inversion Principle (DIP):
High-level modules should not depend on low-level modules; both should depend on abstractions. Additionally, abstractions should not depend on details, but details should depend on abstractions.

By following the SOLID principles, developers can create more modular and robust software that is easier to test, maintain, and extend.

Documentation

## Part 1: List each SOLID principle violated

### 1. Single Responsibility Principle (SRP) Violations

**Violation 1: `RegularUserService`**
- **Why it's a violation:** This class did too many things. It saved users, sent notifications, and managed user data all in one place. A class should only have one job.
- **Refactoring applied:** Made separate classes: `UserService` for users, `NotificationService` for notifications, and `Database<T>` for saving data.

**Violation 2: `AdminUserService`**
- **Why it's a violation:** This class only added push notifications but used inheritance. This made the parent and child classes have different jobs.
- **Refactoring applied:** Changed to use composition instead of inheritance with `NotificationService`.

### 2. Open-Closed Principle (OCP) Violations

**Violation 1: `RegularUserService.sendTaxNotification()`**
- **Why it's a violation:** The method used if-else to handle different notification types. Adding new types meant changing the code.
- **Refactoring applied:** Made `NotificationSender` interface and `NotificationType` enum so new types can be added without changing old code.

**Violation 2: `PostgresDriver`**
- **Why it's a violation:** The class was hard to extend for different databases. It was stuck to one database type.
- **Refactoring applied:** Made `Database<T>` interface and moved `PostgresDriver` to `persistence.drivers` package so new databases can be added easily.

### 3. Liskov Substitution Principle (LSP) Violations

**Violation 1: `AdminUserService`**
- **Why it's a violation:** The subclass threw exceptions for push notifications. You couldn't use it the same way as the parent class.
- **Refactoring applied:** Fixed notification handling so both services work the same way for push notifications.

**Violation 2: `AdminUser.deleteAccount()`**
- **Why it's a violation:** The subclass behaved differently than parent. It could prevent deletion, breaking the expected behavior.
- **Refactoring applied:** Made sure both classes follow the same rules while handling admin-specific logic properly.

### 4. Interface Segregation Principle (ISP) Violations

**Violation 1: `UserOperations` interface**
- **Why it's a violation:** The interface forced classes to handle all notification types, even ones they couldn't use.
- **Refactoring applied:** Split into smaller interfaces: `Database<T>` for saving, `NotificationSender` for notifications, and specific service classes.

**Violation 2: Service classes**
- **Why it's a violation:** Classes had to implement methods they didn't need, leading to empty methods or errors.
- **Refactoring applied:** Made focused service classes with only the methods they actually need.

### 5. Dependency Inversion Principle (DIP) Violations

**Violation 1: `RegularUserService`**
- **Why it's a violation:** The class directly created `PostgresDriver`. It was stuck to one database type and hard to test.
- **Refactoring applied:** Used dependency injection so services depend on interfaces, not concrete classes.

**Violation 2: `Main` class**
- **Why it's a violation:** The main class directly created service instances, making everything tightly connected.
- **Refactoring applied:** Used dependency injection to create services with their dependencies passed in.

## Part 2: Explain how you fixed the delete bug and improved the system robustness

### The Delete Bug
The original system had a bug where:
1. The delete method returned `boolean` but didn't handle missing users properly
2. Admin users with super admin rights showed "success" messages even when deletion was prevented
3. Trying to delete the same user twice would falsely say it worked

### How Fixed It
1. **Changed Return Type**: Made `Database<T>.delete()` return `Optional<T>` instead of `boolean`. This clearly shows if a user was found and deleted.

2. **Better Error Handling**: Updated services to check the result properly:
   ```java
   Optional<User> deletedUser = database.delete(user.getId());
   if (deletedUser.isPresent()) {
       user.deleteAccount();
       System.out.println("Account deleted successfully.");
   } else {
       System.out.println("User with id " + user.getId() + " not found!");
   }
   ```

3. **Fixed Admin Logic**: Made sure admin users with super admin rights show the right message:
   ```java
   if (hasSuperAdminRights) {
       System.out.println("Cannot delete admin user with super admin rights.");
   }
   ```

### System Improvements
1. **Dependency Injection**: Services now get their dependencies passed in, making testing easier
2. **Better Interfaces**: Made smaller, focused interfaces instead of big ones
3. **Error Handling**: System now handles missing users, unsupported notifications, and repeated operations gracefully
4. **Single Responsibility**: Each class now has one clear job

## Running the System

### To run the main application:
```bash
javac -d . src/solid/persistence/Database.java src/solid/persistence/drivers/PostgresDriver.java src/solid/service/NotificationType.java src/solid/service/NotificationSender.java src/solid/service/senders/*.java src/solid/service/NotificationService.java src/solid/service/UserService.java src/solid/service/AdminUserService.java src/solid/service/RegularUserService.java src/solid/user/User.java src/solid/user/AdminUser.java src/Main.java

java Main
```

### To run the test suite:
```bash
./run-tests.sh
```