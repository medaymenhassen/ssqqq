package com.auth.service;

import com.auth.dto.DataRequest;
import com.auth.dto.DataResponse;
import com.auth.model.Data;
import com.auth.model.User;
import com.auth.repository.DataRepository;
import com.auth.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class DataService {

    @Autowired
    private DataRepository dataRepository;

    @Autowired
    private UserRepository userRepository;

    public DataResponse createData(DataRequest dataRequest) {
        // Find the user
        User user = userRepository.findById(dataRequest.getUserId())
                .orElseThrow(() -> new RuntimeException("User not found with id: " + dataRequest.getUserId()));

        // Create new Data entity
        Data data = new Data();
        data.setUser(user);
        data.setImageData(dataRequest.getImageData());
        data.setVideoUrl(dataRequest.getVideoUrl());
        data.setJsonData(dataRequest.getJsonData());
        data.setTimestamp(dataRequest.getTimestamp());
        data.setMovementDetected(dataRequest.getMovementDetected());

        // Save the data
        Data savedData = dataRepository.save(data);

        // Convert to response DTO
        return convertToResponse(savedData);
    }

    public List<DataResponse> getAllData() {
        return dataRepository.findAll()
                .stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }

    public List<DataResponse> getDataByUserId(Long userId) {
        return dataRepository.findByUserIdOrderByTimestampDesc(userId)
                .stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }

    public DataResponse getDataById(Long id) {
        Data data = dataRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Data not found with id: " + id));
        return convertToResponse(data);
    }

    public DataResponse updateData(Long id, DataRequest dataRequest) {
        Data data = dataRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Data not found with id: " + id));

        // Update fields if provided
        if (dataRequest.getImageData() != null) {
            data.setImageData(dataRequest.getImageData());
        }
        if (dataRequest.getVideoUrl() != null) {
            data.setVideoUrl(dataRequest.getVideoUrl());
        }
        if (dataRequest.getJsonData() != null) {
            data.setJsonData(dataRequest.getJsonData());
        }
        if (dataRequest.getTimestamp() != null) {
            data.setTimestamp(dataRequest.getTimestamp());
        }
        data.setMovementDetected(dataRequest.getMovementDetected());

        Data updatedData = dataRepository.save(data);
        return convertToResponse(updatedData);
    }

    public void deleteData(Long id) {
        Data data = dataRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Data not found with id: " + id));
        dataRepository.delete(data);
    }

    private DataResponse convertToResponse(Data data) {
        return new DataResponse(
                data.getId(),
                data.getUser().getId(),
                data.getImageData(),
                data.getVideoUrl(),
                data.getJsonData(),
                data.getTimestamp(),
                data.getMovementDetected(),
                data.getCreatedAt(),
                data.getUpdatedAt()
        );
    }
}