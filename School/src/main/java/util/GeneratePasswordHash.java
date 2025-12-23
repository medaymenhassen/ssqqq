package com.auth.util;

import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

/**
 * Utilitaire pour générer un nouveau hash BCrypt pour "password123"
 * Exécuter avec: mvn compile exec:java -Dexec.mainClass="com.cognitiex.util.GeneratePasswordHash"
 */
public class GeneratePasswordHash {
    public static void main(String[] args) {
        System.out.println(generateHash());
    }
    
    public static String generateHash() {
        BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();
        String password = "password123";
        
        // Générer un nouveau hash
        String hash = encoder.encode(password);
        
        // Vérifier que le hash fonctionne
        boolean matches = encoder.matches(password, hash);
        
        // Output hash for use in scripts
        return hash;
    }
}

