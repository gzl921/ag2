package solid.persistence;

import java.util.Optional;

// Database<T> abstraction that provides save, query and delete operations. @param <T> The type of entity stored in the database
 
public interface Database<T> {
    
    /**
     * Save entity to DB
     * @param entity: The entity to save
     * @return: true if the save was successful
     */
    boolean save(T entity);
    
    /**
     * Query entity by ID
     * @param id: The ID of the entity to query
     * @return: The entity if found, null otherwise
     */
    T query(int id);
    
    /**
     * Delete entity by ID
     * @param id: The ID of the entity to delete
     * @return: Optional containing the deleted entity if found, empty Optional otherwise
     */
    Optional<T> delete(int id);
}
