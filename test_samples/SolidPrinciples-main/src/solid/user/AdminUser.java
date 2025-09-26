package solid.user;

public class AdminUser extends User {
    private boolean hasSuperAdminRights;

    public AdminUser(int id, String username, int age, double salary, boolean hasSuperAdminRights) {
        super(id, username, age, salary);
        this.hasSuperAdminRights = hasSuperAdminRights;
    }

    public boolean hasSuperAdminRights() {
        return hasSuperAdminRights;
    }

    // Override the deleteAccount method
    @Override
    public void deleteAccount() {
        if (hasSuperAdminRights) {
            System.out.println("Cannot delete admin user with super admin rights.");
        } else {
            super.deleteAccount();
        }
    }
}
