package com.auth.util;

import com.auth.model.Role;
import com.auth.model.User;
import com.auth.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

@Component
public class CreateAdminUser implements CommandLineRunner {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Override
    public void run(String... args) throws Exception {
        // Check if admin user already exists
        var existingUserOpt = userRepository.findByEmail("mohamed@admin.com");
        if (existingUserOpt.isEmpty()) {
            User adminUser = new User();
            adminUser.setFirstname("Mohamed");
            adminUser.setLastname("Admin");
            adminUser.setEmail("mohamed@admin.com");
            adminUser.setPassword(passwordEncoder.encode("mohamed0192837465MED"));
            adminUser.setRole(Role.ADMIN);
            adminUser.setEnabled(true);
            
            // Set privacy consents
            adminUser.setRgpdAccepted(true);
            adminUser.setCcpaAccepted(true);
            adminUser.setCommercialUseConsent(true);
            
            userRepository.save(adminUser);
            System.out.println("✅ Admin user created successfully: mohamed@admin.com");
        } else {
            User existingUser = existingUserOpt.get();
            // Update role to ADMIN if it's not already
            if (existingUser.getRole() != Role.ADMIN) {
                existingUser.setRole(Role.ADMIN);
                userRepository.save(existingUser);
                System.out.println("✅ Existing user updated to admin: mohamed@admin.com");
            } else {
                System.out.println("⚠️ Admin user already exists with admin role");
            }
        }
    }
}