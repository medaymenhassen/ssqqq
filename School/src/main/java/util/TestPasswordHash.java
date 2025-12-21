package com.auth.util;

import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

public class TestPasswordHash {
    public static void main(String[] args) {
        BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();
        String password = "password123";
        
        // Générer un nouveau hash
        String newHash = encoder.encode(password);
        System.out.println("Nouveau hash pour 'password123': " + newHash);
        
        // Vérifier que le hash existant fonctionne
        String existingHash = "$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy";
        boolean matches = encoder.matches(password, existingHash);
        System.out.println("Le hash existant fonctionne: " + matches);
        
        if (!matches) {
            System.out.println("ATTENTION: Le hash existant ne fonctionne pas! Utilisez le nouveau hash ci-dessus.");
        }
    }
}

