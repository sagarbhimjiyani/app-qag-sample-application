package com.example.inventory.model;

import java.util.Objects;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;

public class Inventory {
    private String id;

    @NotBlank(message = "name must not be blank")
    private String name;

    @Min(value = 0, message = "quantity must be >= 0")
    private int quantity;

    @NotBlank(message = "location must not be blank")
    private String location;

    public Inventory() {}

    public Inventory(String id, String name, int quantity, String location) {
        this.id = id;
        this.name = name;
        this.quantity = quantity;
        this.location = location;
    }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public int getQuantity() { return quantity; }
    public void setQuantity(int quantity) { this.quantity = quantity; }
    public String getLocation() { return location; }
    public void setLocation(String location) { this.location = location; }

    public String toCsv() {
        return String.format("%s,%s,%d,%s", escape(id), escape(name), quantity, escape(location));
    }

    public static Inventory fromCsv(String line) {
        String[] parts = line.split(",", -1);
        if (parts.length < 4) return null;
        return new Inventory(unescape(parts[0]), unescape(parts[1]), parseInt(parts[2]), unescape(parts[3]));
    }

    private static int parseInt(String s) {
        try { return Integer.parseInt(s); } catch (Exception e) { return 0; }
    }

    private static String escape(String s) { return s == null ? "" : s.replace("\n", " ").replace(",", "\\,"); }
    private static String unescape(String s) { return s == null ? "" : s.replace("\\,", ","); }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Inventory inventory = (Inventory) o;
        return Objects.equals(id, inventory.id);
    }

    @Override
    public int hashCode() { return Objects.hash(id); }
}
