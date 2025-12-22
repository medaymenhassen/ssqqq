package com.auth.model;

import com.fasterxml.jackson.annotation.JsonBackReference;
import com.fasterxml.jackson.annotation.JsonManagedReference;
import jakarta.persistence.*;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.time.LocalDateTime;
import java.util.Collection;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "users")
public class User implements UserDetails {

    public User() {}

    public User(Long id, String firstname, String lastname, String email, String password, Role role, boolean enabled, boolean accountNonExpired, boolean accountNonLocked, boolean credentialsNonExpired, LocalDateTime createdAt, LocalDateTime updatedAt) {
        this.id = id;
        this.firstname = firstname;
        this.lastname = lastname;
        this.email = email;
        this.password = password;
        this.role = role;
        this.enabled = enabled;
        this.accountNonExpired = accountNonExpired;
        this.accountNonLocked = accountNonLocked;
        this.credentialsNonExpired = credentialsNonExpired;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String firstname;

    @Column(nullable = false)
    private String lastname;

    @Column(nullable = false, unique = true)
    private String email;

    @Column(nullable = false)
    private String password;

    @Enumerated(EnumType.STRING)
    private Role role;

    private boolean enabled = true;
    private boolean accountNonExpired = true;
    private boolean accountNonLocked = true;
    private boolean credentialsNonExpired = true;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_type_id", nullable = true)
    private UserType userType;
    
    @Column(name = "is_blocked")
    private Boolean isBlocked = false;
    
    @Column(name = "blocked_reason", length = 500)
    private String blockedReason;
    
    @Column(name = "rgpd_accepted")
    private Boolean rgpdAccepted = false;
    
    @Column(name = "rgpd_accepted_at")
    private LocalDateTime rgpdAcceptedAt;
    
    @Column(name = "ccpa_accepted")
    private Boolean ccpaAccepted = false;
    
    @Column(name = "ccpa_accepted_at")
    private LocalDateTime ccpaAcceptedAt;
    
    @Column(name = "commercial_use_consent")
    private Boolean commercialUseConsent = false;
    
    @Column(name = "commercial_use_consent_at")
    private LocalDateTime commercialUseConsentAt;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getFirstname() {
        return firstname;
    }

    public void setFirstname(String firstname) {
        this.firstname = firstname;
    }

    public String getLastname() {
        return lastname;
    }

    public void setLastname(String lastname) {
        this.lastname = lastname;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public Role getRole() {
        return role;
    }

    public void setRole(Role role) {
        this.role = role;
    }

    public boolean isEnabled() {
        return enabled;
    }

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

    public boolean isAccountNonExpired() {
        return accountNonExpired;
    }

    public void setAccountNonExpired(boolean accountNonExpired) {
        this.accountNonExpired = accountNonExpired;
    }

    public boolean isAccountNonLocked() {
        return accountNonLocked;
    }

    public void setAccountNonLocked(boolean accountNonLocked) {
        this.accountNonLocked = accountNonLocked;
    }

    public boolean isCredentialsNonExpired() {
        return credentialsNonExpired;
    }

    public void setCredentialsNonExpired(boolean credentialsNonExpired) {
        this.credentialsNonExpired = credentialsNonExpired;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
    
    public UserType getUserType() {
        return userType;
    }

    public void setUserType(UserType userType) {
        this.userType = userType;
    }

    public Boolean getIsBlocked() {
        return isBlocked;
    }

    public void setIsBlocked(Boolean isBlocked) {
        this.isBlocked = isBlocked;
    }

    public String getBlockedReason() {
        return blockedReason;
    }

    public void setBlockedReason(String blockedReason) {
        this.blockedReason = blockedReason;
    }

    public Boolean getRgpdAccepted() {
        return rgpdAccepted;
    }

    public void setRgpdAccepted(Boolean rgpdAccepted) {
        this.rgpdAccepted = rgpdAccepted;
    }

    public LocalDateTime getRgpdAcceptedAt() {
        return rgpdAcceptedAt;
    }

    public void setRgpdAcceptedAt(LocalDateTime rgpdAcceptedAt) {
        this.rgpdAcceptedAt = rgpdAcceptedAt;
    }

    public Boolean getCcpaAccepted() {
        return ccpaAccepted;
    }

    public void setCcpaAccepted(Boolean ccpaAccepted) {
        this.ccpaAccepted = ccpaAccepted;
    }

    public LocalDateTime getCcpaAcceptedAt() {
        return ccpaAcceptedAt;
    }

    public void setCcpaAcceptedAt(LocalDateTime ccpaAcceptedAt) {
        this.ccpaAcceptedAt = ccpaAcceptedAt;
    }

    public Boolean getCommercialUseConsent() {
        return commercialUseConsent;
    }

    public void setCommercialUseConsent(Boolean commercialUseConsent) {
        this.commercialUseConsent = commercialUseConsent;
    }

    public LocalDateTime getCommercialUseConsentAt() {
        return commercialUseConsentAt;
    }

    public void setCommercialUseConsentAt(LocalDateTime commercialUseConsentAt) {
        this.commercialUseConsentAt = commercialUseConsentAt;
    }

    // Additional methods for compatibility
    public Boolean getIsAdmin() {
        return role == Role.ADMIN;
    }

    public Boolean getIsApproved() {
        return true; // Default implementation
    }

    public User getParent() {
        return null; // Default implementation
    }

    public String getJob() {
        return ""; // Default implementation
    }

    public String getLevel() {
        return ""; // Default implementation
    }

    public Boolean getIsActive() {
        return enabled;
    }

    public void setFirstName(String firstName) {
        this.firstname = firstName;
    }

    public void setLastName(String lastName) {
        this.lastname = lastName;
    }

    public void setUsername(String username) {
        this.email = username;
    }

    public void setParent(User parent) {
        // Default implementation
    }

    public void setJob(String job) {
        // Default implementation
    }

    public void setLevel(String level) {
        // Default implementation
    }

    public void setIsActive(Boolean isActive) {
        this.enabled = isActive != null ? isActive : false;
    }

    public void setIsApproved(Boolean isApproved) {
        // Default implementation
    }

    public void setBigger(Boolean bigger) {
        // Default implementation
    }

    public Boolean getBigger() {
        return false; // Default implementation
    }

    public List<User> getSubUsers() {
        return new ArrayList<>(); // Default implementation
    }

    public Long countByParentId(Long parentId) {
        return 0L; // Default implementation
    }

    public List<User> findByParentId(Long parentId) {
        return new ArrayList<>(); // Default implementation
    }

    public Boolean existsByUsername(String username) {
        return false; // Default implementation
    }

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return List.of(new SimpleGrantedAuthority("ROLE_" + role.name()));
    }

    @Override
    public String getUsername() {
        return email;
    }
}