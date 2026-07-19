package com.example.inventory.controller;

import com.example.inventory.model.Inventory;
import com.example.inventory.repository.CsvInventoryRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import jakarta.validation.Valid;

import java.net.URI;
import java.util.List;

@RestController
@RequestMapping("/api/inventory")
public class InventoryController {

    private final CsvInventoryRepository repository;

    public InventoryController(CsvInventoryRepository repository) {
        this.repository = repository;
    }

    @GetMapping
    public List<Inventory> getAll() {
        return repository.findAll();
    }

    @GetMapping("/{id}")
    public ResponseEntity<Inventory> getById(@PathVariable String id) {
        return repository.findById(id).map(ResponseEntity::ok).orElseGet(() -> ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<Inventory> createOrUpdate(@Valid @RequestBody Inventory item) {
        boolean isNew = item.getId() == null || item.getId().isBlank();
        Inventory saved = repository.save(item);
        if (isNew) return ResponseEntity.created(URI.create("/api/inventory/" + saved.getId())).body(saved);
        return ResponseEntity.ok(saved);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable String id) {
        boolean deleted = repository.deleteById(id);
        return deleted ? ResponseEntity.noContent().build() : ResponseEntity.notFound().build();
    }
}
