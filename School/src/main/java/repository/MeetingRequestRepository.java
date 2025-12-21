package com.auth.repository;

import com.auth.model.MeetingRequest;
import com.auth.model.MeetingRequestStatus;
import com.auth.model.User;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface MeetingRequestRepository extends JpaRepository<MeetingRequest, Long> {
    
    @EntityGraph(attributePaths = {"requester", "company", "calendarEvent"})
    List<MeetingRequest> findByRequester(User requester);
    
    @EntityGraph(attributePaths = {"requester", "company", "calendarEvent"})
    List<MeetingRequest> findByCompany(User company);
    
    @EntityGraph(attributePaths = {"requester", "company", "calendarEvent"})
    List<MeetingRequest> findByCompanyAndStatus(User company, MeetingRequestStatus status);
    
    @EntityGraph(attributePaths = {"calendarEvent", "requester", "company"})
    List<MeetingRequest> findByRequesterAndStatus(User requester, MeetingRequestStatus status);
}

