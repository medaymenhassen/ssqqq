package com.auth.service;

import com.auth.util.JwtUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class JwtService {

    @Autowired
    private JwtUtil jwtUtil;

    public String generateToken(String username, String role) {
        return jwtUtil.generateToken(username, role);
    }

    public String getUsernameFromToken(String token) {
        String username = jwtUtil.getUsernameFromToken(token);
        System.out.println("JwtService - Username from token: '" + username + "'");
        return username;
    }

    public String getRoleFromToken(String token) {
        try {
            String role = jwtUtil.getRoleFromToken(token);
            System.out.println("JwtService - Role from token: '" + role + "'");
            
            return role;
        } catch (Exception e) {
            System.out.println("JwtService - Error getting role from token: " + e.getMessage());
            e.printStackTrace();
            return null;
        }
    }

    public Boolean validateToken(String token, String username) {
        return jwtUtil.validateToken(token, username);
    }
}