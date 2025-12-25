package com.auth.model;

public enum ApprovalStatus {
    PENDING,      // Offer purchased but awaiting admin approval
    APPROVED,     // Admin has approved the offer access
    REJECTED      // Admin has rejected the offer access
}