# Offer System Implementation

This document describes the implementation of the offer system that provides time-based access control to course content.

## System Overview

The offer system allows users to purchase time-limited access to course content. Users must purchase an offer before they can view lessons. Each offer has:
- A title and description
- A price
- A duration in hours
- An associated user type

## Components

### 1. Models

#### Offer Model
Represents a purchasable offer with time-based access.

**Fields:**
- `id`: Unique identifier
- `title`: Offer name
- `description`: Detailed description
- `price`: Cost in currency
- `durationHours`: Access duration in hours
- `userTypeId`: Associated user type
- `isActive`: Whether the offer is available for purchase
- `createdAt`: Creation timestamp
- `updatedAt`: Last update timestamp

#### UserOffer Model
Tracks which users have purchased which offers.

**Fields:**
- `id`: Unique identifier
- `user`: Reference to the user
- `offer`: Reference to the purchased offer
- `purchaseDate`: When the offer was purchased
- `expirationDate`: When access expires
- `isActive`: Whether the purchase is still valid
- `createdAt`: Creation timestamp
- `updatedAt`: Last update timestamp

### 2. Repositories

#### OfferRepository
Provides database access for offers with methods to:
- Find all active offers
- Find offers by user type

#### UserOfferRepository
Provides database access for user purchases with methods to:
- Find purchases by user
- Check if a user has an active offer
- Find unexpired offers for a user

### 3. Services

#### OfferService
Business logic for managing offers and purchases:

**Methods:**
- `getAllActiveOffers()`: Get all available offers
- `getOffersByUserType()`: Get offers for a specific user type
- `getOfferById()`: Get a specific offer
- `createOffer()`: Create a new offer (admin only)
- `updateOffer()`: Update an existing offer (admin only)
- `deleteOffer()`: Delete an offer (admin only)
- `purchaseOffer()`: Allow a user to purchase an offer
- `userHasAccessToContent()`: Check if a user has active access
- `getUserPurchasedOffers()`: Get a user's purchased offers

### 4. Controllers

#### OfferController
REST API endpoints for offer management:

**Endpoints:**
- `GET /api/offers`: Get all active offers
- `GET /api/offers/{id}`: Get a specific offer
- `POST /api/offers`: Create a new offer (admin only)
- `PUT /api/offers/{id}`: Update an offer (admin only)
- `DELETE /api/offers/{id}`: Delete an offer (admin only)
- `POST /api/offers/{offerId}/purchase?userId={userId}`: Purchase an offer
- `GET /api/offers/user/{userId}/access`: Check user access
- `GET /api/offers/user/{userId}/purchases`: Get user's purchases

#### Modified CourseLessonController
Updated to enforce access control:

**Modified Endpoints:**
- `GET /api/course-lessons/{id}?userId={userId}`: Check access before returning lesson
- `GET /api/course-lessons/user/{userId}`: Check access before returning user lessons

## Access Control Logic

1. When a user tries to access course content, the system checks if they have any active, unexpired offers
2. If no valid offers are found, access is denied with a 403 Forbidden response
3. If valid offers are found, access is granted
4. Users can purchase multiple offers, but cannot purchase the same offer twice

## Usage Examples

### For Users
1. Browse available offers: `GET /api/offers`
2. Purchase an offer: `POST /api/offers/{offerId}/purchase?userId={userId}`
3. Check access status: `GET /api/offers/user/{userId}/access`
4. View purchased offers: `GET /api/offers/user/{userId}/purchases`
5. Access lessons (with access): `GET /api/course-lessons/{id}?userId={userId}`

### For Administrators
1. Create new offers: `POST /api/offers`
2. Update existing offers: `PUT /api/offers/{id}`
3. Delete offers: `DELETE /api/offers/{id}`

## Testing

The system includes a Python test script (`test_offer_system.py`) that demonstrates:
1. User registration and login
2. Offer browsing and purchase
3. Access control enforcement
4. Content access verification

Run the test with:
```
python test_offer_system.py
```

Or use the batch script:
```
run_offer_test.bat
```

## Database Schema

The system adds two new tables:
1. `offers`: Stores available offers
2. `user_offers`: Tracks user purchases

## Security

- Only administrators can create, update, or delete offers
- Users can only purchase offers for themselves
- All endpoints use proper authentication and authorization
- Access checks are performed server-side

## Future Enhancements

1. **Offer Categories**: Group offers by category or topic
2. **Discounts**: Implement promotional pricing
3. **Subscription Model**: Recurring payment options
4. **Usage Analytics**: Track how users utilize their access time
5. **Refund System**: Allow users to request refunds
6. **Gift Purchases**: Allow users to purchase offers for others