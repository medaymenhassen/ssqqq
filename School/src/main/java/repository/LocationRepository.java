package com.auth.repository;

import com.auth.model.Location;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface LocationRepository extends JpaRepository<Location, Long> {
    
    List<Location> findByIsActiveTrueOrderByDisplayOrderAsc();
}

