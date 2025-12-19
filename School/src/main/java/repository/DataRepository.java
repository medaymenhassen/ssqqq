package com.auth.repository;

import com.auth.model.Data;
import com.auth.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface DataRepository extends JpaRepository<Data, Long> {
    List<Data> findByUser(User user);
    List<Data> findByUserId(Long userId);
    List<Data> findByUserOrderByTimestampDesc(User user);
    List<Data> findByUserIdOrderByTimestampDesc(Long userId);
}