package com.auth.config;

import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;

@Component
public class RequestLoggingFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        
        // Log request details
        System.out.println("🌐 Incoming Request:");
        System.out.println("   Method: " + request.getMethod());
        System.out.println("   URI: " + request.getRequestURI());
        System.out.println("   Query String: " + request.getQueryString());
        System.out.println("   Remote Address: " + request.getRemoteAddr());
        
        // Log headers
        System.out.println("   Headers:");
        request.getHeaderNames().asIterator().forEachRemaining(headerName -> {
            System.out.println("     " + headerName + ": " + request.getHeader(headerName));
        });
        
        // Continue with the filter chain
        filterChain.doFilter(request, response);
        
        // Log response details
        System.out.println("   Response Status: " + response.getStatus());
    }
}