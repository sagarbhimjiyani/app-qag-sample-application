# Warehouse Inventory Management System

A Spring Boot REST API for managing warehouse inventory with CSV storage backend.

## Quick Start

### Prerequisites
- Java 17 or higher
- Maven 3.6+

### Run Locally

**Option 1: Maven (Recommended)**
```bash
cd C:\Users\sagar\IdeaProjects\app-qag-sample-application
mvn spring-boot:run
```

**Option 2: Run JAR directly**
```bash
cd C:\Users\sagar\IdeaProjects\app-qag-sample-application
mvn clean package
java -jar target/inventory-app-0.0.1-SNAPSHOT.jar
```

**Option 3: IntelliJ IDEA**
1. Open project in IntelliJ IDEA
2. Right-click `InventoryApplication.java` → Run
3. Or use Debug mode for development

### Access the App
- **API Base URL:** http://localhost:8080/api/inventory
- **Swagger UI:** http://localhost:8080/swagger-ui.html
- **OpenAPI Spec:** http://localhost:8080/v3/api-docs

## API Endpoints

### 1. Get All Items
```bash
GET /api/inventory
```
Response: Array of all inventory items

### 2. Get Item by ID
```bash
GET /api/inventory/{id}
```
Example: `GET /api/inventory/550e8400-e29b-41d4-a716-446655440000`

### 3. Create New Item
```bash
POST /api/inventory
Content-Type: application/json

{
  "name": "Widget",
  "quantity": 10,
  "location": "A1"
}
```
Response: 201 Created with auto-generated ID

### 4. Update Existing Item
```bash
POST /api/inventory
Content-Type: application/json

{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Widget Updated",
  "quantity": 15,
  "location": "A2"
}
```
Response: 200 OK

### 5. Delete Item
```bash
DELETE /api/inventory/{id}
```
Response: 204 No Content

## Project Structure
```
app-qag-sample-application/
├── src/main/java/com/example/inventory/
│   ├── InventoryApplication.java       (Main app)
│   ├── controller/
│   │   ├── InventoryController.java    (REST endpoints)
│   │   └── GlobalExceptionHandler.java (Error handling)
│   ├── model/
│   │   └── Inventory.java              (Data model with validation)
│   ├── repository/
│   │   └── CsvInventoryRepository.java (CSV persistence)
│   └── config/
│       └── OpenApiConfig.java          (Swagger config)
├── data/
│   └── inventory.csv                   (Data storage)
├── pom.xml                             (Maven config)
├── Dockerfile                          (Docker build)
└── README.md                           (This file)
```

## Configuration

Edit `src/main/resources/application.properties`:
```properties
inventory.file=data/inventory.csv    # CSV file location
server.port=8080                      # Server port
```

## Data Model

```json
{
  "id": "auto-generated-uuid",
  "name": "Product name (required)",
  "quantity": 0,
  "location": "Warehouse location (required)"
}
```

**Validation Rules:**
- `name`: Required, non-blank
- `quantity`: Must be >= 0
- `location`: Required, non-blank
- `id`: Auto-generated if not provided

## Testing with cURL

```bash
# Create
curl -X POST http://localhost:8080/api/inventory \
  -H "Content-Type: application/json" \
  -d '{"name":"Widget","quantity":10,"location":"A1"}'

# Get all
curl http://localhost:8080/api/inventory

# Get by ID
curl http://localhost:8080/api/inventory/550e8400-e29b-41d4-a716-446655440000

# Update
curl -X POST http://localhost:8080/api/inventory \
  -H "Content-Type: application/json" \
  -d '{"id":"550e8400-e29b-41d4-a716-446655440000","name":"Widget","quantity":15,"location":"A2"}'

# Delete
curl -X DELETE http://localhost:8080/api/inventory/550e8400-e29b-41d4-a716-446655440000
```

## CSV Storage

Inventory data is stored in `data/inventory.csv`:
```
id,name,quantity,location
550e8400-e29b-41d4-a716-446655440000,Widget,10,A1
```

## Docker

Build and run with Docker:
```bash
docker build -t inventory-app:latest .
docker run -d -p 8080:8080 --name inventory-app inventory-app:latest
```

## Dependencies

- Spring Boot 3.1.4
- Spring Web
- Jakarta Validation
- SpringDoc OpenAPI 2.1.0 (Swagger/OpenAPI)

## License

MIT
