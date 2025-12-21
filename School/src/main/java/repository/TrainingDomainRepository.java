package com.auth.repository;

import com.auth.model.TrainingDomain;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface TrainingDomainRepository extends JpaRepository<TrainingDomain, Long> {
    Optional<TrainingDomain> findBySlug(String slug);
    List<TrainingDomain> findByIsActiveTrueOrderByStudentCountDescDisplayOrderAsc();
    List<TrainingDomain> findByIsActiveTrueOrderByDisplayOrderAsc();
}

