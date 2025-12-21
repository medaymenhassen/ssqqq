package com.auth.repository;

import com.auth.model.CompanyCalendar;
import com.auth.model.User;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface CompanyCalendarRepository extends JpaRepository<CompanyCalendar, Long> {
    
    @EntityGraph(attributePaths = {"company"})
    List<CompanyCalendar> findByCompany(User company);
    
    @EntityGraph(attributePaths = {"company"})
    List<CompanyCalendar> findByCompanyAndStartTimeBetween(
        User company, 
        LocalDateTime start, 
        LocalDateTime end
    );
    
    @EntityGraph(attributePaths = {"company"})
    @Query("SELECT c FROM CompanyCalendar c WHERE c.company = :company AND c.startTime >= :start AND c.isAvailable = true")
    List<CompanyCalendar> findAvailableSlotsByCompany(
        @Param("company") User company,
        @Param("start") LocalDateTime start
    );
    
    @EntityGraph(attributePaths = {"company"})
    @Query("SELECT c FROM CompanyCalendar c")
    List<CompanyCalendar> findAllWithCompany();
    
    @EntityGraph(attributePaths = {"company"})
    @Query("SELECT c FROM CompanyCalendar c WHERE c.id = ?1")
    Optional<CompanyCalendar> findByIdEagerly(Long id);
    
    // Vérifier les conflits de dates/heures pour un utilisateur
    // Deux événements se chevauchent si : (start1 < end2) AND (start2 < end1)
    // Utiliser l'ID de l'utilisateur plutôt que l'objet User pour éviter les problèmes de comparaison
    @EntityGraph(attributePaths = {"company"})
    @Query("SELECT c FROM CompanyCalendar c WHERE c.company.id = :companyId AND " +
           "c.startTime < :endTime AND c.endTime > :startTime AND " +
           "c.id != :excludeId")
    List<CompanyCalendar> findConflictingEvents(
        @Param("companyId") Long companyId,
        @Param("startTime") LocalDateTime startTime,
        @Param("endTime") LocalDateTime endTime,
        @Param("excludeId") Long excludeId
    );
    
    // Version sans exclusion d'ID (pour création)
    // Deux événements se chevauchent si : (start1 < end2) AND (start2 < end1)
    // Utiliser l'ID de l'utilisateur plutôt que l'objet User pour éviter les problèmes de comparaison
    @EntityGraph(attributePaths = {"company"})
    @Query("SELECT c FROM CompanyCalendar c WHERE c.company.id = :companyId AND " +
           "c.startTime < :endTime AND c.endTime > :startTime")
    List<CompanyCalendar> findConflictingEventsForCreation(
        @Param("companyId") Long companyId,
        @Param("startTime") LocalDateTime startTime,
        @Param("endTime") LocalDateTime endTime
    );
    
    // Récupérer les événements de calendrier par leurs IDs (utilisé pour les demandes approuvées)
    @EntityGraph(attributePaths = {"company"})
    List<CompanyCalendar> findByIdIn(List<Long> ids);
}

