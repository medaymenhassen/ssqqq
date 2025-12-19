package com.auth.service;

import com.auth.model.TokenBlacklist;
import com.auth.model.User;
import com.auth.repository.TokenBlacklistRepository;
import org.springframework.stereotype.Service;

@Service
public class TokenBlacklistService {

    private final TokenBlacklistRepository tokenBlacklistRepository;

    public TokenBlacklistService(TokenBlacklistRepository tokenBlacklistRepository) {
        this.tokenBlacklistRepository = tokenBlacklistRepository;
    }

    public void blacklistToken(String token, User user, String reason) {
        if (!tokenBlacklistRepository.existsByToken(token)) {
            TokenBlacklist tokenBlacklist = new TokenBlacklist();
            tokenBlacklist.setToken(token);
            tokenBlacklist.setUser(user);
            tokenBlacklist.setReason(reason);
            
            tokenBlacklistRepository.save(tokenBlacklist);
        }
    }

    public boolean isTokenBlacklisted(String token) {
        return tokenBlacklistRepository.existsByToken(token);
    }
}