package com.auth.service;

import com.auth.dto.LoginRequest;
import com.auth.dto.LoginResponse;
import com.auth.dto.RegisterRequest;
import com.auth.model.User;
import com.auth.model.Role;
import com.auth.repository.UserRepository;
import com.auth.security.JwtTokenProvider;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AuthService {

    private static final Logger logger = LoggerFactory.getLogger(AuthService.class);

    private final UserRepository userRepository;
    private final AuthenticationManager authenticationManager;
    private final JwtTokenProvider jwtTokenProvider;
    private final RefreshTokenService refreshTokenService;
    private final TokenBlacklistService tokenBlacklistService;
    private final PasswordEncoder passwordEncoder;

    public AuthService(UserRepository userRepository,
                      AuthenticationManager authenticationManager,
                      JwtTokenProvider jwtTokenProvider,
                      RefreshTokenService refreshTokenService,
                      TokenBlacklistService tokenBlacklistService,
                      PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.authenticationManager = authenticationManager;
        this.jwtTokenProvider = jwtTokenProvider;
        this.refreshTokenService = refreshTokenService;
        this.tokenBlacklistService = tokenBlacklistService;
        this.passwordEncoder = passwordEncoder;
    }

    @Transactional
    public LoginResponse login(LoginRequest request) {
        try {
            // Authenticate user
            Authentication authentication = authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(
                            request.getEmail(),
                            request.getPassword()
                    )
            );

            // Get authenticated user
            User user = (User) authentication.getPrincipal();
            logger.info("Utilisateur authentifié: {}", user.getEmail());

            // Revoke all user tokens
            refreshTokenService.revokeAllUserTokens(user);

            // Generate new tokens
            String accessToken = jwtTokenProvider.generateAccessToken(user);
            com.auth.model.RefreshToken refreshToken = refreshTokenService.createRefreshToken(user);

            return new LoginResponse(accessToken, refreshToken.getToken(), "Bearer", 900000L, "Authentification réussie");

        } catch (AuthenticationException e) {
            logger.error("Authentification échouée pour l'email: {}", request.getEmail());
            throw new IllegalArgumentException("Email ou mot de passe incorrect");
        }
    }

    @Transactional
    public LoginResponse register(RegisterRequest request) {
        // Check if email already exists
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new IllegalArgumentException("Un utilisateur avec cet email existe déjà");
        }

        // Create user
        User user = new User();
        user.setEmail(request.getEmail());
        user.setFirstname(request.getFirstname());
        user.setLastname(request.getLastname());
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        user.setRole(Role.USER);
        user.setEnabled(true);
        user.setAccountNonExpired(true);
        user.setAccountNonLocked(true);
        user.setCredentialsNonExpired(true);

        User savedUser = userRepository.save(user);
        logger.info("Nouvel utilisateur enregistré: {}", savedUser.getEmail());

        // Generate tokens
        String accessToken = jwtTokenProvider.generateAccessToken(savedUser);
        com.auth.model.RefreshToken refreshToken = refreshTokenService.createRefreshToken(savedUser);

        return new LoginResponse(accessToken, refreshToken.getToken(), "Bearer", 900000L, "Utilisateur enregistré avec succès");
    }

    @Transactional
    public void logout(String accessToken, String refreshToken, User user) {
        try {
            // Blacklist access token
            tokenBlacklistService.blacklistToken(accessToken, user, "Logout");
            logger.info("Access token blacklisté pour logout: {}", user.getEmail());

            // Revoke refresh token
            if (refreshToken != null && !refreshToken.isEmpty()) {
                refreshTokenService.revokeRefreshToken(refreshToken);
                logger.info("Refresh token révoqué pour logout: {}", user.getEmail());
            }

            logger.info("Utilisateur déconnecté avec succès: {}", user.getEmail());
        } catch (Exception e) {
            logger.error("Erreur lors de la déconnexion: {}", e.getMessage());
            throw new RuntimeException("Erreur lors de la déconnexion");
        }
    }
}