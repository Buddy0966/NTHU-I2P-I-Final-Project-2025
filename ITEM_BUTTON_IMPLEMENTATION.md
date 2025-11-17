# Item 按鈕功能實現總結

## 概述
已成功實現了戰鬥場景中的 Item 按鈕功能，玩家可以在戰鬥中選擇物品進行攻擊。

## 實現細節

### 1. 新增 BattleState
```python
CHOOSE_ITEM = 9  # 物品選擇狀態
```

### 2. 新增 BattleItemPanel 組件
位置: `src/interface/components/battle_item_panel.py`

**功能**:
- 顯示玩家背包中的所有物品
- 類似 bag_panel.py 的 UI 設計
- 顯示物品圖片、名稱和數量
- 提供點擊按鈕選擇物品

**特點**:
- ✓ 使用 BattleActionButton 建立物品選擇按鈕
- ✓ 為每個物品顯示對應的圖片 (sprite)
- ✓ 顯示物品數量
- ✓ 背景使用 UI_Flat_Frame03a.png 框架
- ✓ 支持多個物品滾動

### 3. battle_scene.py 更新

#### 新增屬性
```python
item_panel: BattleItemPanel | None        # Item 面板
player_selected_item: dict | None         # 玩家選擇的物品
```

#### 新增方法

**_on_item_click()**
```python
def _on_item_click(self) -> None:
    # 檢查是否有物品
    # 創建 BattleItemPanel
    # 轉換到 CHOOSE_ITEM 狀態
```

**_execute_item_attack(item: dict)**
```python
def _execute_item_attack(self, item: dict) -> None:
    # 計算物品傷害 (5-25 HP)
    # 減少對手 HP
    # 減少物品數量
    # 檢查戰鬥是否結束
    # 轉換到敵方回合
```

#### update() 方法更新
- 處理 CHOOSE_ITEM 狀態
- 更新 item_panel
- 檢測物品選擇
- 支援按 ESC 取消物品選擇

#### draw() 方法更新
- 在 CHOOSE_ITEM 狀態下繪製 item_panel
- 顯示 "Press ESC to cancel" 提示

## 遊戲流程

### Item 使用流程
```
玩家在 PLAYER_TURN
  ↓
按下 "Item" 按鈕
  ↓
[CHOOSE_ITEM] 顯示 BattleItemPanel
  ├─ 顯示所有背包物品
  ├─ 每個物品有獨立按鈕
  └─ 可按 ESC 返回
  ↓
點擊物品或按 ESC
  ├─ 選擇物品 → 執行物品攻擊
  │   ├─ 計算傷害 (5-25 HP)
  │   ├─ 扣除對手 HP
  │   ├─ 物品數量 -1
  │   └─ 檢查戰鬥結束
  │   ↓
  │   轉換到 ENEMY_TURN
  │
  └─ 按 ESC → 返回 PLAYER_TURN
```

## 使用範例

### 物品使用範例
```
玩家: Pikachu HP: 80/100
敵方: Squirtle HP: 60/60

回合進行中...
玩家選擇: Item 按鈕
→ 顯示物品面板:
  ├─ 超級球 x3
  ├─ 治療藥物 x5
  └─ 爆炸彈 x2

玩家選擇: 爆炸彈 x2
→ 爆炸彈擊中 Squirtle!
→ 對手受到 18 傷害 (HP: 42/60)
→ 物品數量: 爆炸彈 x1

敵方回合...
Squirtle 使用 Water Gun
玩家受到 12 傷害 (HP: 68/100)
```

## 文件修改清單

| 文件 | 修改 |
|------|------|
| `src/scenes/battle_scene.py` | 新增 CHOOSE_ITEM 狀態、item_panel 屬性、_execute_item_attack() 方法、更新 update() 和 draw() |
| `src/interface/components/battle_item_panel.py` | **新建** - BattleItemPanel 類 |
| `src/interface/components/__init__.py` | 新增 BattleItemPanel 匯出 |

## 功能特性

### ✓ 已實現
- 物品選擇 UI (類似 bag_panel)
- 物品圖片顯示
- 物品名稱和數量顯示
- 物品點擊選擇
- 物品傷害計算 (5-25 HP 隨機)
- 物品數量扣除
- 敵方 HP 更新
- ESC 取消物品選擇
- 轉換回合制流程

### ⚠ 可進一步改進
- 不同物品有不同傷害值 (目前固定 5-25)
- 物品特殊效果 (如治療、強化等)
- 物品傷害動畫效果
- 物品數量為 0 時自動隱藏

## 物品傷害設定

目前物品傷害統一為:
- **傷害範圍**: 5-25 HP
- **計算方式**: `random.randint(5, 25)`

未來可以根據物品類型設定不同傷害:
```python
ITEM_DAMAGE = {
    "超級球": (5, 10),
    "爆炸彈": (15, 25),
    "治療藥物": (-10, -5),  # 負數表示治療
}
```

## 按鍵控制

| 按鍵 | 功能 |
|------|------|
| **滑鼠點擊** | 選擇物品 |
| **ESC** | 取消物品選擇，返回主菜單 |
| **SPACE** | (在其他狀態下使用) |

## 語法驗證

✓ `battle_scene.py` - 無語法錯誤
✓ `battle_item_panel.py` - 無語法錯誤
✓ `__init__.py` - 無語法錯誤

## 下一步建議

1. **物品系統完善**
   - 添加不同物品的不同傷害值
   - 實現治療物品功能
   - 添加特殊物品效果

2. **UI 改進**
   - 物品卡片設計
   - 物品詳細信息顯示
   - 物品使用動畫

3. **遊戲邏輯**
   - 物品掉落系統
   - 物品購買商店
   - 物品合成系統

## 結論

成功實現了戰鬥中的 Item 按鈕功能，提供了類似 bag_panel 的物品選擇 UI，允許玩家在戰鬥中使用物品對敵人進行傷害。
