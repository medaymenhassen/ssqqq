package com.auth.controller;

import com.auth.model.User;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/user")
public class UserController {

    @GetMapping("/profile")
    public Map<String, Object> getCurrentUser(@AuthenticationPrincipal User user) {
        Map<String, Object> userInfo = new HashMap<>();
        userInfo.put("id", user.getId());
        userInfo.put("email", user.getEmail());
        userInfo.put("firstname", user.getFirstname());
        userInfo.put("lastname", user.getLastname());
        userInfo.put("role", user.getRole());
        userInfo.put("enabled", user.isEnabled());
        
        return userInfo;
    }
}