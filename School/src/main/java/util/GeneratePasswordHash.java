package com.auth.util;

import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

/**
 * Utilitaire pour générer un nouveau hash BCrypt pour "password123"
 * Exécuter avec: mvn compile exec:java -Dexec.mainClass="com.cognitiex.util.GeneratePasswordHash"
 */
public class GeneratePasswordHash {
    public static void main(String[] args) {
        BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();
        String password = "password123";
        
        // Générer un nouveau hash
        String hash = encoder.encode(password);
        System.out.println("==========================================");
        System.out.println("Nouveau hash BCrypt pour 'password123':");
        System.out.println(hash);
        System.out.println("==========================================");
        
        // Vérifier que le hash fonctionne
        boolean matches = encoder.matches(password, hash);
        System.out.println("Vérification: " + (matches ? "✓ OK" : "✗ ERREUR"));
        System.out.println("==========================================");
    }
}

