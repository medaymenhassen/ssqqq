package com.auth.security;

import com.auth.service.JwtService;
import com.auth.model.Role;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.springframework.core.annotation.Order;
import org.springframework.core.Ordered;

@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    @Autowired
    private JwtService jwtService;

    @Autowired
    private UserDetailsService userDetailsService;

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        
        try {
            logger.info("Processing request: " + request.getMethod() + " " + request.getRequestURI());
            
            final String authorizationHeader = request.getHeader("Authorization");
            
            logger.info("Authorization header: " + (authorizationHeader != null ? "present" : "absent"));
            
            String username = null;
            String jwt = null;
            
            if (authorizationHeader != null && authorizationHeader.startsWith("Bearer ")) {
                jwt = authorizationHeader.substring(7);
                logger.info("Extracted JWT token: " + jwt.substring(0, Math.min(jwt.length(), 20)) + "...");
                
                try {
                    username = jwtService.getUsernameFromToken(jwt);
                    logger.info("Extracted username from token: " + username);
                } catch (Exception e) {
                    logger.warn("Invalid JWT token provided: " + e.getMessage());
                    // Don't set username, which will skip authentication
                    username = null;
                }
            }
            
            if (username != null && SecurityContextHolder.getContext().getAuthentication() == null) {
                logger.info("Loading user details for: " + username);
                try {
                    UserDetails userDetails = this.userDetailsService.loadUserByUsername(username);
                    
                    logger.info("Validating token for user: " + username);
                    if (jwtService.validateToken(jwt, userDetails.getUsername())) {
                        logger.info("Token is valid for user: " + username);
                        // Extract role from token
                        String role = jwtService.getRoleFromToken(jwt);
                        logger.info("Extracted role from token: " + role);
                        
                        List<SimpleGrantedAuthority> authorities = new ArrayList<>();
                        if (role != null) {
                            authorities.add(new SimpleGrantedAuthority("ROLE_" + role));
                        }
                        
                        UsernamePasswordAuthenticationToken authToken = new UsernamePasswordAuthenticationToken(
                                userDetails, null, authorities);
                        authToken.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
                        SecurityContextHolder.getContext().setAuthentication(authToken);
                        logger.info("Authentication set for user: " + username);
                    } else {
                        logger.warn("Token validation failed for user: " + username);
                    }
                } catch (Exception e) {
                    logger.warn("Error loading user details for: " + username + ", error: " + e.getMessage());
                    // Continue without authentication
                }
            }
            
            logger.info("Request processed: " + request.getMethod() + " " + request.getRequestURI() + " - Authentication: " + (SecurityContextHolder.getContext().getAuthentication() != null ? "authenticated" : "not authenticated") + " - Status: " + response.getStatus());
            
            filterChain.doFilter(request, response);
        } catch (Exception e) {
            logger.error("Error in JWT filter: " + e.getMessage(), e);
            // Continue with the filter chain even if there's an error
            filterChain.doFilter(request, response);
        }
    }
}