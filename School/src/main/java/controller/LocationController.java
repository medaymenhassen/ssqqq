package com.auth.controller;

import com.auth.model.Location;
import com.auth.repository.LocationRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/springboot/locations")
@CrossOrigin(origins = {"http://localhost:4200", "https://cognitiex.com"})
public class LocationController {
    
    @Autowired
    private LocationRepository locationRepository;
    
    @GetMapping
    public ResponseEntity<List<Location>> getAllLocations() {
        return ResponseEntity.ok(locationRepository.findByIsActiveTrueOrderByDisplayOrderAsc());
    }
}

