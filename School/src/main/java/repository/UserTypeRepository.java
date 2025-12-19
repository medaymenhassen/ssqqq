package com.auth.repository;

import com.auth.model.UserType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface UserTypeRepository extends JpaRepository<UserType, Long> {
    
    boolean existsByNom(String nom);
    
    @Query("SELECT ut FROM UserType ut WHERE ut.isSpecial = true")
    List<UserType> findAllSpecial();
    
    @Query("SELECT ut FROM UserType ut WHERE ut.isSpecial = false")
    List<UserType> findAllNormal();
}