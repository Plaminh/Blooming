# Data Model: Garden Plant Selection

## Entities

### `PlantPresentation`
View-model representation of a plant in the Garden Selection carousel.
* **id**: `PlantId` (e.g. 'monstera', 'sunflower')
* **name**: `string`
* **description**: `string[]` (Array of description lines, max 2)
* **species**: `PlantSpecies` (Mapped to the sprite atlas species)
* **unlockCost**: `number`

### `UserSessionState`
Local mock representation of the user's progress.
* **leafBalance**: `number`
* **unlockedPlants**: `Set<PlantId>` (Tracks which plants have been purchased)

### `GardenSelectionState`
The root state controller for the page.
* **plants**: `PlantPresentation[]`
* **currentIndex**: `number`
* **session**: `UserSessionState`

## State Transitions
* **Unlock Action**: 
  - Validates `session.leafBalance >= plants[currentIndex].unlockCost`
  - Validates `!session.unlockedPlants.has(plants[currentIndex].id)`
  - Mutates `session.leafBalance -= plants[currentIndex].unlockCost`
  - Mutates `session.unlockedPlants.add(plants[currentIndex].id)`
* **Navigation Action**:
  - `next()`: `currentIndex = min(currentIndex + 1, plants.length - 1)`
  - `previous()`: `currentIndex = max(currentIndex - 1, 0)`
