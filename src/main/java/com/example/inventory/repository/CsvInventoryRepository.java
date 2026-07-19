package com.example.inventory.repository;

import com.example.inventory.model.Inventory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Repository;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;

@Repository
public class CsvInventoryRepository {

    @Value("${inventory.file:data/inventory.csv}")
    private String inventoryFile;

    private Path filePath;
    private final Object lock = new Object();

    private void ensureInit() {
        if (filePath != null) return;
        synchronized (lock) {
            if (filePath != null) return;
            try {
                filePath = Path.of(inventoryFile);
                if (!Files.exists(filePath.getParent())) {
                    Files.createDirectories(filePath.getParent());
                }
                if (!Files.exists(filePath)) {
                    Files.writeString(filePath, "id,name,quantity,location\\n", StandardOpenOption.CREATE_NEW);
                }
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }
    }

    public List<Inventory> findAll() {
        ensureInit();
        synchronized (lock) {
            try {
                List<String> lines = Files.readAllLines(filePath);
                return lines.stream().skip(1)
                        .map(Inventory::fromCsv)
                        .filter(i -> i != null)
                        .collect(Collectors.toList());
            } catch (IOException e) {
                return new ArrayList<>();
            }
        }
    }

    public Optional<Inventory> findById(String id) {
        ensureInit();
        return findAll().stream().filter(i -> id.equals(i.getId())).findFirst();
    }

    public Inventory save(Inventory item) {
        ensureInit();
        synchronized (lock) {
            List<Inventory> all = findAll();
            if (item.getId() == null || item.getId().isBlank()) {
                item.setId(UUID.randomUUID().toString());
                all.add(item);
            } else {
                boolean replaced = false;
                List<Inventory> updated = new ArrayList<>();
                for (Inventory inv : all) {
                    if (inv.getId().equals(item.getId())) {
                        updated.add(item);
                        replaced = true;
                    } else {
                        updated.add(inv);
                    }
                }
                if (!replaced) updated.add(item);
                all = updated;
            }
            writeAll(all);
            return item;
        }
    }

    public boolean deleteById(String id) {
        ensureInit();
        synchronized (lock) {
            List<Inventory> all = findAll();
            List<Inventory> remaining = all.stream().filter(i -> !id.equals(i.getId())).collect(Collectors.toList());
            if (remaining.size() == all.size()) return false;
            writeAll(remaining);
            return true;
        }
    }

    private void writeAll(List<Inventory> items) {
        ensureInit();
        List<String> lines = new ArrayList<>();
        lines.add("id,name,quantity,location");
        lines.addAll(items.stream().map(Inventory::toCsv).collect(Collectors.toList()));
        try {
            Files.write(filePath, lines);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
}