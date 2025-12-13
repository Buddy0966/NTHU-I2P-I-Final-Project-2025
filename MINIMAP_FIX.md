# Minimap Coordinate Fix

## Problem
The minimap was not properly synchronizing coordinates with the player's position, especially when the player was near the edges of the map (bottom-left and other corners).

## Root Cause
The original implementation had a flaw in the coordinate system:

1. **Player was always drawn at center**: The player indicator was always drawn at the exact center of the minimap (100, 100), regardless of whether the viewport was clamped to a map edge.

2. **Entity positions used offset-based calculation**: Entities were positioned relative to the camera center, which didn't account for viewport clamping at map edges.

3. **Viewport clamping wasn't communicated**: When the map viewport was clamped to an edge (e.g., at bottom-left corner), this information wasn't passed to the player/entity drawing functions.

## Solution

### Changes Made

#### 1. Viewport Information Return
Modified `_draw_map_viewport()` to return a dictionary containing:
```python
{
    "source_x": source_x,      # Where we're reading from on the scaled map
    "source_y": source_y,
    "dest_x": dest_x,          # Where we're drawing on the minimap
    "dest_y": dest_y,
    "center_x": center_x,      # Player's position in scaled coordinates
    "center_y": center_y
}
```

#### 2. Player Position Calculation
Changed from:
```python
# OLD - Always at center
center_x = self.size[0] / 2
center_y = self.size[1] / 2
```

To:
```python
# NEW - Accounts for viewport offset
player_scaled_x = viewport_info["center_x"]
player_scaled_y = viewport_info["center_y"]

center_x = viewport_info["dest_x"] + (player_scaled_x - viewport_info["source_x"])
center_y = viewport_info["dest_y"] + (player_scaled_y - viewport_info["source_y"])
```

#### 3. Entity Position Calculation
Changed from:
```python
# OLD - Relative offset from camera
offset_x = (entity_x - camera_center_x) * self.scale_factor
offset_y = (entity_y - camera_center_y) * self.scale_factor
minimap_x = minimap_center_x + offset_x
minimap_y = minimap_center_y + offset_y
```

To:
```python
# NEW - Absolute position with viewport offset
entity_scaled_x = entity_x * self.scale_factor
entity_scaled_y = entity_y * self.scale_factor

minimap_x = viewport_info["dest_x"] + (entity_scaled_x - viewport_info["source_x"])
minimap_y = viewport_info["dest_y"] + (entity_scaled_y - viewport_info["source_y"])
```

## How It Works Now

### Normal Case (Middle of Map)
```
Player at (1000, 1000) in world coordinates
Scaled: (100, 100) at 10% scale
Viewport source: (0, 0) to (200, 200)
Viewport dest: (0, 0)

Player minimap position:
  x = 0 + (100 - 0) = 100 ✓ (centered)
  y = 0 + (100 - 0) = 100 ✓ (centered)
```

### Edge Case (Bottom-Left Corner)
```
Player at (100, 100) in world coordinates
Scaled: (10, 10) at 10% scale
Viewport would want source: (-90, -90) to (110, 110)
But clamped to: (0, 0) to (200, 200)
Viewport dest: (0, 0)

Player minimap position:
  x = 0 + (10 - 0) = 10 ✓ (not centered, correct!)
  y = 0 + (10 - 0) = 10 ✓ (not centered, correct!)
```

### Edge Case (Top-Right Corner of Large Map)
```
Player at (2000, 100) in world coordinates
Map size: 2200x1500 pixels (220x150 scaled)
Scaled player: (200, 10)
Viewport would want: (100, -90) to (300, 110)
But clamped to: (20, 0) to (220, 200)
Viewport dest: (0, 0)

Player minimap position:
  x = 0 + (200 - 20) = 180 ✓ (near right edge, correct!)
  y = 0 + (10 - 0) = 10 ✓ (near top edge, correct!)
```

## Files Modified

- `src/interface/components/minimap.py`:
  - `_draw_map_viewport()`: Now returns viewport_info dict
  - `_draw_player()`: Updated to use viewport_info for positioning
  - `_draw_entities()`: Updated to use viewport_info for positioning
  - `draw()`: Passes viewport_info to player and entity drawing functions

## Benefits

1. **Accurate positioning**: Player and entities now appear at their true map positions
2. **Edge handling**: Correctly handles all map edges (top, bottom, left, right, corners)
3. **Small map support**: Works with maps smaller than the minimap size
4. **Large map support**: Works with maps larger than the minimap viewport

## Testing Scenarios

To verify the fix works, test these scenarios:

1. ✓ **Center of map**: Player should be centered in minimap
2. ✓ **Top-left corner**: Player should be near top-left of minimap
3. ✓ **Top-right corner**: Player should be near top-right of minimap
4. ✓ **Bottom-left corner**: Player should be near bottom-left of minimap
5. ✓ **Bottom-right corner**: Player should be near bottom-right of minimap
6. ✓ **Top edge**: Player should be near top, horizontally centered
7. ✓ **Bottom edge**: Player should be near bottom, horizontally centered
8. ✓ **Left edge**: Player should be near left, vertically centered
9. ✓ **Right edge**: Player should be near right, vertically centered
10. ✓ **Entities**: NPCs and trainers should maintain correct relative positions

---

**Fixed**: 2025-12-13
**Issue**: Coordinate synchronization at map edges
**Status**: ✅ Resolved
