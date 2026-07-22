package com.example.inventory.controller;

import com.example.inventory.model.Inventory;
import com.example.inventory.repository.CsvInventoryRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import jakarta.validation.Valid;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;

import java.net.URI;
import java.util.List;

@RestController
@RequestMapping("/api/inventory")
@Tag(name = "Inventory", description = "Warehouse inventory CRUD operations")
public class InventoryController {

    private final CsvInventoryRepository repository;

    public InventoryController(CsvInventoryRepository repository) {
        this.repository = repository;
    }

    @GetMapping
    @Operation(summary = "Get all inventory items")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "List of all items")
    })
    public List<Inventory> getAll() {
        return repository.findAll();
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get inventory item by ID")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Item found"),
        @ApiResponse(responseCode = "404", description = "Item not found")
    })
    public ResponseEntity<Inventory> getById(@PathVariable String id) {
        return repository.findById(id).map(ResponseEntity::ok).orElseGet(() -> ResponseEntity.notFound().build());
    }

    @PostMapping
    @Operation(summary = "Create or update inventory item", description = "If no id provided, creates new item. If id provided, updates existing.")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "201", description = "Item created"),
        @ApiResponse(responseCode = "200", description = "Item updated"),
        @ApiResponse(responseCode = "400", description = "Invalid input")
    })
    public ResponseEntity<Inventory> createOrUpdate(@Valid @RequestBody Inventory item) {
        boolean isNew = item.getId() == null || item.getId().isBlank();
        Inventory saved = repository.save(item);
        if (isNew) return ResponseEntity.created(URI.create("/api/inventory/" + saved.getId())).body(saved);
        return ResponseEntity.ok(saved);
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Delete inventory item by ID")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "204", description = "Item deleted"),
        @ApiResponse(responseCode = "404", description = "Item not found")
    })
    public ResponseEntity<Void> delete(@PathVariable String id) {
        boolean deleted = repository.deleteById(id);
        return deleted ? ResponseEntity.noContent().build() : ResponseEntity.notFound().build();
    }
}
