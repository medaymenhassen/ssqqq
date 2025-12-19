package com.auth.service;

import com.auth.dto.UserTypeRequest;
import com.auth.dto.UserTypeResponse;
import com.auth.dto.DocumentResponse;
import com.auth.model.UserType;
import com.auth.model.Document;
import com.auth.repository.UserTypeRepository;
import com.auth.repository.DocumentRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class UserTypeService {

    private static final Logger log = LoggerFactory.getLogger(UserTypeService.class);

    private final UserTypeRepository userTypeRepository;
    private final DocumentRepository documentRepository;

    public UserTypeService(UserTypeRepository userTypeRepository,
                          DocumentRepository documentRepository) {
        this.userTypeRepository = userTypeRepository;
        this.documentRepository = documentRepository;
    }

    /**
     * Créer un nouveau type d'utilisateur
     */
    @Transactional
    public UserTypeResponse createUserType(UserTypeRequest request) {
        // Vérifier que le nom n'existe pas
        if (userTypeRepository.existsByNom(request.getNom())) {
            throw new IllegalArgumentException("Un type avec ce nom existe déjà");
        }

        // Créer l'entité
        UserType userType = new UserType();
        userType.setNom(request.getNom());
        userType.setDescription(request.getDescription());
        userType.setSpecial(request.isSpecial());

        UserType saved = userTypeRepository.save(userType);
        log.info("Type d'utilisateur créé: {} (special: {})", saved.getNom(), saved.isSpecial());

        return mapToResponse(saved);
    }

    /**
     * Récupérer tous les types d'utilisateurs
     */
    public List<UserTypeResponse> getAllUserTypes() {
        return userTypeRepository.findAll()
                .stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    /**
     * Récupérer les types "spéciaux" uniquement
     */
    public List<UserTypeResponse> getSpecialUserTypes() {
        return userTypeRepository.findAllSpecial()
                .stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    /**
     * Récupérer les types "normaux" uniquement
     */
    public List<UserTypeResponse> getNormalUserTypes() {
        return userTypeRepository.findAllNormal()
                .stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    /**
     * Récupérer un type par ID
     */
    public UserTypeResponse getUserTypeById(Long id) {
        UserType userType = userTypeRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Type d'utilisateur non trouvé"));
        
        return mapToResponse(userType);
    }

    /**
     * Récupérer les documents d'un type
     */
    public List<DocumentResponse> getDocumentsByUserType(Long userTypeId) {
        // Vérifier que le type existe
        UserType userType = userTypeRepository.findById(userTypeId)
                .orElseThrow(() -> new IllegalArgumentException("Type d'utilisateur non trouvé"));

        // Si ce n'est pas un type "spécial", retourner une liste vide
        if (!userType.isSpecial()) {
            log.warn("Tentative d'accès aux documents d'un type non-spécial: {}", userTypeId);
            return List.of();
        }

        // Retourner les documents
        return documentRepository.findByUserTypeId(userTypeId)
                .stream()
                .map(this::mapDocumentToResponse)
                .collect(Collectors.toList());
    }

    /**
     * Ajouter un document à un type
     */
    @Transactional
    public DocumentResponse addDocumentToUserType(Long userTypeId, Document document) {
        // Vérifier que le type existe
        UserType userType = userTypeRepository.findById(userTypeId)
                .orElseThrow(() -> new IllegalArgumentException("Type d'utilisateur non trouvé"));

        // Associer le document au type
        document.setUserType(userType);
        Document saved = documentRepository.save(document);

        return mapDocumentToResponse(saved);
    }

    /**
     * Mettre à jour un type
     */
    @Transactional
    public UserTypeResponse updateUserType(Long id, UserTypeRequest request) {
        UserType userType = userTypeRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Type d'utilisateur non trouvé"));

        // Vérifier unicité du nom (si changé)
        if (!userType.getNom().equals(request.getNom()) && 
            userTypeRepository.existsByNom(request.getNom())) {
            throw new IllegalArgumentException("Un type avec ce nom existe déjà");
        }

        // Mettre à jour
        userType.setNom(request.getNom());
        userType.setDescription(request.getDescription());
        userType.setSpecial(request.isSpecial());

        UserType updated = userTypeRepository.save(userType);
        log.info("Type d'utilisateur mis à jour: {}", updated.getNom());

        return mapToResponse(updated);
    }

    /**
     * Supprimer un type
     */
    @Transactional
    public void deleteUserType(Long id) {
        UserType userType = userTypeRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Type d'utilisateur non trouvé"));

        // Supprimer d'abord les documents associés
        documentRepository.deleteByUserTypeId(id);
        
        // Puis supprimer le type
        userTypeRepository.delete(userType);
        log.info("Type d'utilisateur supprimé: {}", id);
    }

    /**
     * Mapper vers DTO de réponse
     */
    private UserTypeResponse mapToResponse(UserType userType) {
        return new UserTypeResponse(
                userType.getId(),
                userType.getNom(),
                userType.getDescription(),
                userType.isSpecial(),
                userType.getCreatedAt(),
                userType.getUpdatedAt()
        );
    }

    /**
     * Mapper Document vers DTO de réponse
     */
    private DocumentResponse mapDocumentToResponse(Document document) {
        return new DocumentResponse(
                document.getId(),
                document.getName(),
                document.getDescription(),
                document.getFilePath(),
                document.getUserType().getId(),
                document.getCreatedAt(),
                document.getUpdatedAt()
        );
    }
}