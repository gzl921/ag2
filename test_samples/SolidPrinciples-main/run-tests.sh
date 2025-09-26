#!/bin/bash

# Compile with JUnit
javac -cp ".:lib/junit-platform-console-standalone-1.9.3.jar" -d . \
    src/solid/persistence/Database.java \
    src/solid/persistence/drivers/PostgresDriver.java \
    src/solid/service/NotificationType.java \
    src/solid/service/senders/*.java \
    src/solid/service/NotificationService.java \
    src/solid/service/UserService.java \
    src/solid/service/AdminUserService.java \
    src/solid/service/RegularUserService.java \
    src/solid/user/User.java \
    src/solid/user/AdminUser.java \
    test/UserServiceTest.java

# Run tests
java -jar lib/junit-platform-console-standalone-1.9.3.jar --class-path . --scan-class-path
