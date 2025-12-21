package com.auth.repository;

import com.auth.model.Offer;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface OfferRepository extends JpaRepository<Offer, Long> {
    List<Offer> findByIsActiveTrue();
    List<Offer> findByUserTypeIdAndIsActiveTrue(Long userTypeId);
}