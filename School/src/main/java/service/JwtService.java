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
        return jwtUtil.getUsernameFromToken(token);
    }

    public String getRoleFromToken(String token) {
        try {
            return jwtUtil.getRoleFromToken(token);
        } catch (Exception e) {
            return null;
        }
    }

    public Boolean validateToken(String token, String username) {
        return jwtUtil.validateToken(token, username);
    }
}