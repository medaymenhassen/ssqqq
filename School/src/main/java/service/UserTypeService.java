package com.auth.service;

import com.auth.model.UserType;
import com.auth.repository.UserTypeRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class UserTypeService {

    @Autowired
    private UserTypeRepository userTypeRepository;

    public List<UserType> getAllUserTypes() {
        return userTypeRepository.findAll();
    }

    public Optional<UserType> getUserTypeById(Long id) {
        return userTypeRepository.findById(id);
    }

    public UserType createUserType(UserType userType) {
        return userTypeRepository.save(userType);
    }

    public UserType updateUserType(Long id, UserType userDetails) {
        UserType userType = userTypeRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("UserType not found with id: " + id));
        
        userType.setNameFr(userDetails.getNameFr());
        userType.setNameEn(userDetails.getNameEn());
        userType.setDescFr(userDetails.getDescFr());
        userType.setDescEn(userDetails.getDescEn());
        userType.setBigger(userDetails.getBigger());
        
        return userTypeRepository.save(userType);
    }

    public void deleteUserType(Long id) {
        userTypeRepository.deleteById(id);
    }
}