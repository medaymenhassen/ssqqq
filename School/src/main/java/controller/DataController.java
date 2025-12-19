package com.auth.controller;

import com.auth.dto.DataRequest;
import com.auth.dto.DataResponse;
import com.auth.service.DataService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/data")
@CrossOrigin(origins = "http://localhost:4200") // Allow requests from Angular frontend
public class DataController {

    @Autowired
    private DataService dataService;

    // Create new data record
    @PostMapping
    public ResponseEntity<DataResponse> createData(@RequestBody DataRequest dataRequest) {
        try {
            DataResponse response = dataService.createData(dataRequest);
            return new ResponseEntity<>(response, HttpStatus.CREATED);
        } catch (Exception e) {
            return new ResponseEntity<>(HttpStatus.BAD_REQUEST);
        }
    }

    // Get all data records
    @GetMapping
    public ResponseEntity<List<DataResponse>> getAllData() {
        try {
            List<DataResponse> data = dataService.getAllData();
            return new ResponseEntity<>(data, HttpStatus.OK);
        } catch (Exception e) {
            return new ResponseEntity<>(HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }

    // Get data records by user ID
    @GetMapping("/user/{userId}")
    public ResponseEntity<List<DataResponse>> getDataByUserId(@PathVariable Long userId) {
        try {
            List<DataResponse> data = dataService.getDataByUserId(userId);
            return new ResponseEntity<>(data, HttpStatus.OK);
        } catch (Exception e) {
            return new ResponseEntity<>(HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }

    // Get data record by ID
    @GetMapping("/{id}")
    public ResponseEntity<DataResponse> getDataById(@PathVariable Long id) {
        try {
            DataResponse data = dataService.getDataById(id);
            return new ResponseEntity<>(data, HttpStatus.OK);
        } catch (Exception e) {
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }
    }

    // Update data record
    @PutMapping("/{id}")
    public ResponseEntity<DataResponse> updateData(@PathVariable Long id, @RequestBody DataRequest dataRequest) {
        try {
            DataResponse response = dataService.updateData(id, dataRequest);
            return new ResponseEntity<>(response, HttpStatus.OK);
        } catch (Exception e) {
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }
    }

    // Delete data record
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteData(@PathVariable Long id) {
        try {
            dataService.deleteData(id);
            return new ResponseEntity<>(HttpStatus.NO_CONTENT);
        } catch (Exception e) {
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }
    }
}