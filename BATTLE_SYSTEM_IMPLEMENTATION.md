# 戰鬥系統實現總結

## 概述
已成功在 `battle_scene.py` 中實現了完整的回合制戰鬥系統。

## 實現的功能

### 1. 回合狀態管理 (BattleState Enum)
- **INTRO**: 戰鬥開始動畫
- **CHALLENGER**: 對手出現訊息
- **SEND_OPPONENT**: 對手派出怪物
- **SEND_PLAYER**: 玩家派出怪物
- **PLAYER_TURN**: 玩家回合 - 顯示主要行動按鈕
- **CHOOSE_MOVE**: 玩家選擇招式
- **ENEMY_TURN**: 敵方回合 - 敵人自動攻擊
- **BATTLE_END**: 戰鬥結束 (勝利或失敗)

### 2. 回合制系統
- **玩家先手**: 戰鬥開始時，玩家首先進行操作
- **輪流進行**: 玩家回合 → 敵方回合 → 玩家回合 (循環往復)
- **敵方延遲**: 敵方在進入 ENEMY_TURN 後 1.5 秒自動攻擊

### 3. 玩家行動選項
玩家在 PLAYER_TURN 時有以下選項：

| 按鈕 | 功能 | 狀態 |
|------|------|------|
| Fight | 進入招式選擇界面 | ✓ 實現 |
| Item | 使用物品 | ⚠ 預留 |
| Switch | 更換怪物 | ⚠ 預留 |
| Run | 逃離戰鬥 | ✓ 實現 |

### 4. 攻擊系統
**玩家攻擊**:
- 從 4 個招式中選擇 (Woodhammer, Headbutt, Howl, Leer)
- 傷害範圍: 10-20 HP
- 立即生效並傷害對手

**敵方攻擊**:
- 隨機選擇招式
- 傷害範圍: 8-15 HP
- 延遲 1.5 秒自動執行

### 5. 勝敗判定
- **玩家勝利**: 對手 HP ≤ 0 時顯示 "You won!"
- **玩家失敗**: 玩家 HP ≤ 0 時顯示 "You lost!"
- **戰鬥結束**: 進入 BATTLE_END 狀態，按 SPACE 返回遊戲

### 6. HP 動態更新
- 使用 `PokemonStatsPanel.update_pokemon()` 方法實時更新 HP 條
- HP 顏色變化:
  - 綠色: HP > 30%
  - 橙色: 10% < HP ≤ 30%
  - 紅色: HP ≤ 10%

## 核心實現細節

### 新增方法
```python
# 攻擊系統
_execute_player_attack()      # 玩家攻擊邏輯
_execute_enemy_attack()       # 敵方攻擊邏輯
_check_battle_end()           # 檢查戰鬥結束條件

# 按鈕回調
_on_fight_click()             # Fight 按鈕
_on_item_click()              # Item 按鈕
_on_run_click()               # Run 按鈕
_on_move_select(move: str)    # 招式選擇
```

### 新增屬性
```python
current_turn: str             # "player" 或 "enemy"
player_selected_move: str     # 玩家選擇的招式
enemy_selected_move: str      # 敵方選擇的招式
turn_message: str             # 回合訊息
```

## 遊戲流程圖

```
戰鬥開始
  ↓
[INTRO] 對手來了！(按 SPACE)
  ↓
[CHALLENGER] 對手派出 Leogreen！(按 SPACE)
  ↓
[SEND_OPPONENT] Leogreen 出場！(按 SPACE)
  ↓
[SEND_PLAYER] Go, [玩家怪獸]！(按 SPACE)
  ↓
[PLAYER_TURN] 玩家選擇行動
  ├─ Fight → [CHOOSE_MOVE] 選擇招式 → 攻擊 → HP 扣除
  ├─ Item → 物品功能 (WIP)
  ├─ Switch → 更換怪物 (WIP)
  └─ Run → 逃離戰鬥
  ↓
[ENEMY_TURN] 敵方攻擊中... (1.5秒延遲)
  ↓
  敵方選擇招式 → 攻擊 → 玩家 HP 扣除
  ↓
┌─ HP > 0? ─ 是 → 回到 [PLAYER_TURN]
└─────────── 否 → [BATTLE_END]
  ↓
[BATTLE_END] 勝利或失敗訊息 (按 SPACE 返回遊戲)
```

## 範例遊戲進行

```
玩家: Leogreen HP: 100/100
敵方: Leogreen HP: 45/45

回合 1:
玩家: 選擇 Woodhammer 攻擊
敵方: 受到 15 傷害 (HP: 30/45)

回合 2 (延遲1.5秒):
敵方: 使用 Headbutt
玩家: 受到 12 傷害 (HP: 88/100)

回合 3:
玩家: 選擇 Headbutt 攻擊
敵方: 受到 18 傷害 (HP: 12/45)

回合 4 (延遲1.5秒):
敵方: 使用 Leer
玩家: 受到 10 傷害 (HP: 78/100)

回合 5:
玩家: 選擇 Woodhammer 攻擊
敵方: 受到 14 傷害 (HP: -2/45 → 0)
→ 敵方倒下！玩家勝利！
```

## 文件修改清單

1. **src/scenes/battle_scene.py**
   - 新增 PLAYER_TURN, ENEMY_TURN, BATTLE_END 狀態
   - 實現回合系統邏輯
   - 實現攻擊和傷害計算
   - 實現勝敗判定
   - 更新 update() 和 draw() 方法

2. **src/interface/components/pokemon_stats_panel.py**
   - 新增 `update_pokemon()` 方法以動態更新 HP 顯示

## 測試清單

- [x] 回合順序正確 (玩家 → 敵方 → 玩家)
- [x] 玩家可選擇招式
- [x] 攻擊傷害正確應用
- [x] HP 正確減少
- [x] HP 不會低於 0
- [x] 敵方自動選擇招式
- [x] 敵方延遲攻擊正常運作
- [x] 勝利條件判定正確
- [x] 失敗條件判定正確
- [x] 戰鬥結束可返回遊戲
- [x] Run 按鈕可逃離戰鬥
- [x] HP 條實時更新顯示

## 未來改進建議

1. **Move System**: 實現實際的招式系統（目前無任何招式效果差異）
2. **Experience & Level Up**: 戰勝後獲得經驗
3. **Switch Pokemon**: 實現切換怪物功能
4. **Item System**: 實現物品使用系統
5. **Special Effects**: 添加攻擊動畫和音效
6. **Difficulty Levels**: 敵方 AI 難度等級

## 結論

成功實現了一個功能完整的回合制戰鬥系統，滿足所有基本需求：
- ✓ 回合制系統 (玩家先手)
- ✓ 兩種行動選項 (Attack + Run)
- ✓ 攻擊傷害機制
- ✓ HP 扣除
- ✓ 勝敗判定
