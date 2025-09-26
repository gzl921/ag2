package solid.persistence.drivers;

import solid.persistence.Database;
import solid.user.User;

import java.util.HashMap;
import java.util.Optional;

// PostgreSQL DB driver implementation for better separate concerns
 
public class PostgresDriver implements Database<User> {
    private static HashMap<Integer, User> users = new HashMap<>();

 
    @Override
    public boolean save(User user) {
        System.out.println("Executing Save SQL: " + user);
        users.put(user.getId(), user);
        return true;
    }

  
    @Override
    public User query(int id) {
        System.out.println("Executing SQL query");
        try {
            return users.get(id);
        } catch (IndexOutOfBoundsException e) {
            return null;
        }
    }

   
    @Override
    public Optional<User> delete(int id) {
        System.out.println("Executing SQL delete");
        try {
            User user = users.remove(id);
            return Optional.ofNullable(user);
        } catch (IndexOutOfBoundsException e) {
            return Optional.empty();
        }
    }
}
